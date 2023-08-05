Notes
=====

`TracTicketReferencePlugin`_ adds simple ticket cross-reference for Trac.

Note: TracTicketReference requires Trac 0.12 or higher.

.. _TracTicketReferencePlugin: http://trac-hacks.org/wiki/TracTicketReferencePlugin

What is it?
-----------

This plugin adds "Relationships" fields to each ticket, enabling you
to express cross-reference between tickets. 

Configuration
=============

To enable the plugin::

    [components]
    ticketref.* = enabled

    [ticket-custom]
    ticketref = text
    ticketref.label = Relationships

Custom fields
-------------
While the field names must be ``ticketref``, you are free to use any
text for the field labels.

Acknowledgment
==============

This plugin was inspired by `MasterTicketsPlugin`_.

.. _MasterTicketsPlugin: http://trac-hacks.org/wiki/MasterTicketsPlugin
