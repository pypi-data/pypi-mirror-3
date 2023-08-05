# -*- coding: utf-8 -*-

from pkg_resources import resource_filename

from genshi.builder import tag
from trac.core import *
from trac.web.api import ITemplateStreamFilter
from trac.web.chrome import ITemplateProvider
from trac.resource import ResourceNotFound
from trac.ticket.model import Ticket
from trac.util.text import shorten_line

from model import TICKETREF as TREF
from utils import cnv_text2list

TEMPLATE_FILES = [
    "report_view.html", "query_results.html", "ticket.html", "query.html",
]


class TicketRefsTemplate(Component):
    """ Extend template for ticket cross-reference """

    implements(ITemplateStreamFilter, ITemplateProvider)

    # ITemplateStreamFilter methods
    def filter_stream(self, req, method, filename, stream, data):
        if not data or (not filename in TEMPLATE_FILES):
            return stream

        # For ticket.html
        if "fields" in data and isinstance(data["fields"], list):
            self._filter_fields(req, data)

        # For query_results.html and query.html
        if "groups" in data and isinstance(data["groups"], list):
            self._filter_groups(req, data)

        # For report_view.html
        if "row_groups" in data and isinstance(data["row_groups"], list):
            self._filter_row_groups(req, data)

        return stream

    def _filter_fields(self, req, data):
        for field in data["fields"]:
            if field["name"] == TREF and data["ticket"][TREF]:
                field["rendered"] = self._link_refs(req, data["ticket"][TREF])

    def _filter_groups(self, req, data):
        for group, tickets in data["groups"]:
            for ticket in tickets:
                if TREF in ticket:
                    ticket[TREF] = self._link_refs(req, ticket[TREF])

    def _filter_row_groups(self, req, data):
        for group, rows in data["row_groups"]:
            for row in rows:
                _is_list = isinstance(row["cell_groups"], list)
                if "cell_groups" in row and _is_list:
                    for cells in row["cell_groups"]:
                        for cell in cells:
                            if cell.get("header", {}).get("col") == TREF:
                                cell["value"] = self._link_refs(req,
                                                                cell["value"])

    def _link_refs(self, req, refs_text):
        items = []
        for ref_id in cnv_text2list(refs_text):
            elem = "#%s" % ref_id
            try:
                ticket = Ticket(self.env, ref_id)
                if "TICKET_VIEW" in req.perm(ticket.resource):
                    elem = tag.a("#%s" % ref_id, class_=ticket["status"],
                                 href=req.href.ticket(ref_id),
                                 title=shorten_line(ticket["summary"]))
            except ResourceNotFound:
                pass  # not supposed to happen, just in case
            items.append(elem)
            items.append(", ")
        return items and tag(items[:-1]) or None

    # ITemplateProvider methods
    def get_htdocs_dirs(self):
        """Return the absolute path of a directory containing additional
        static resources (such as images, style sheets, etc).
        """
        return [("ticketref", resource_filename(__name__, "htdocs"))]

    def get_templates_dirs(self):
        """Return the absolute path of the directory containing the provided
        ClearSilver templates.
        """
        return [resource_filename(__name__, "templates")]
