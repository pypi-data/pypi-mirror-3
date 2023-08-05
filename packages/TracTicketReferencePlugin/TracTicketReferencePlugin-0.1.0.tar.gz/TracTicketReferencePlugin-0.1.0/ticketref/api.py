# -*- coding: utf-8 -*-

from trac.core import *
from trac.env import IEnvironmentSetupParticipant
from trac.ticket.api import ITicketChangeListener, ITicketManipulator
from trac.ticket.model import Ticket

from model import CUSTOM_FIELDS, TICKETREF, TicketLinks


class TicketRefsPlugin(Component):
    """ Extend custom field for ticket cross-reference """

    implements(IEnvironmentSetupParticipant,
               ITicketChangeListener, ITicketManipulator)

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
        if self.has_ticket_refs(ticket):
            self.log.debug("TracTicketReference: ticket are creating")
            links = TicketLinks(self.env, ticket)
            links.create()

    def ticket_changed(self, ticket, comment, author, old_values):
        if TICKETREF in old_values:
            self.log.debug("TracTicketReference: ticket are changing")
            links = TicketLinks(self.env, ticket)
            links.change(author, old_values[TICKETREF])

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
            for _id in ticket[TICKETREF].split(","):
                ref_id = int(_id.strip())
                try:
                    assert ref_id != ticket.id
                    Ticket(self.env, ref_id)
                except Exception, err:
                    _prop = ("ticket-custom", "ticketref.label")
                    yield self.env.config.get(*_prop), err
