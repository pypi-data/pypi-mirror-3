# -*- coding: utf-8 -*-

from pkg_resources import resource_filename

from trac.core import *
from trac.env import IEnvironmentSetupParticipant
from trac.ticket.api import ITicketChangeListener, ITicketManipulator
from trac.ticket.model import Ticket
from trac.util.translation import domain_functions

from model import CUSTOM_FIELDS, TICKETREF, TicketLinks
from utils import cnv_sorted_refs, get_refs_in_comment

_, add_domain = domain_functions("ticketref", ("_", "add_domain"))


class TicketRefsPlugin(Component):
    """ Extend custom field for ticket cross-reference """

    implements(IEnvironmentSetupParticipant,
               ITicketChangeListener, ITicketManipulator)

    def __init__(self):
        add_domain(self.env.path, resource_filename(__name__, "locale"))

    # IEnvironmentSetupParticipant methods
    def environment_created(self):
        self.upgrade_environment(self.env.get_db_cnx())

    def environment_needs_upgrade(self, db):
        for field in CUSTOM_FIELDS:
            if field["name"] not in self.config["ticket-custom"]:
                return True
        return False

    def upgrade_environment(self, db):
        custom = self.config["ticket-custom"]
        for field in CUSTOM_FIELDS:
            if field["name"] not in custom:
                custom.set(field["name"], field["type"])
                for key, value in field["properties"]:
                    custom.set(key, value)
                self.config.save()

    def has_ticket_refs(self, ticket):
        refs = ticket[TICKETREF]
        return refs and refs.strip()

    # ITicketChangeListener methods
    def ticket_created(self, ticket):
        links = None
        desc_refs = get_refs_in_comment(ticket["description"])
        if desc_refs:
            ticket[TICKETREF] = cnv_sorted_refs(ticket[TICKETREF], desc_refs)
            links = TicketLinks(self.env, ticket)
            links.add_reference(desc_refs)

        if self.has_ticket_refs(ticket):
            self.log.debug("TracTicketReference: ticket are creating")
            if not links:
                links = TicketLinks(self.env, ticket)
            links.create()

    def ticket_changed(self, ticket, comment, author, old_values):
        links = None
        need_change = TICKETREF in old_values

        com_refs = get_refs_in_comment(comment)
        if com_refs:
            links = TicketLinks(self.env, ticket)
            links.add_reference(com_refs)
            need_change = True

        if need_change:
            self.log.debug("TracTicketReference: ticket are changing")
            if not links:
                links = TicketLinks(self.env, ticket)
            links.change(author, old_values.get(TICKETREF))

    def ticket_deleted(self, ticket):
        if self.has_ticket_refs(ticket):
            self.log.debug("TracTicketReference: ticket are deleting")
            links = TicketLinks(self.env, ticket)
            links.delete()

    # ITicketManipulator methods
    def prepare_ticket(self, req, ticket, fields, actions):
        pass

    def validate_ticket(self, req, ticket):
        if self.has_ticket_refs(ticket):
            _prop = ("ticket-custom", "ticketref.label")
            for _id in ticket[TICKETREF].split(","):
                ref_id = int(_id.strip())
                try:
                    assert ref_id != ticket.id
                    Ticket(self.env, ref_id)
                except AssertionError:
                    msg = _("Ticket %s is this ticket id, remove it.") % ref_id
                    yield self.env.config.get(*_prop), msg
                except Exception, err:
                    yield self.env.config.get(*_prop), err
