import grok

from horae.properties import properties
from horae.properties import interfaces

from horae.planning import _


def minimum_entry_length_property():
    """ Project and milestone property defining the minimum length of time entries
    """
    property = properties.FloatProperty()
    property.id = 'minimum_entry_length'
    property.name = _(u'Minimum time entry length (hours)')
    property.initial = True
    property.editable = True
    property.customizable = False
    property.searchable = False
    property.order = 210
    return property
grok.global_utility(minimum_entry_length_property, provides=interfaces.IDefaultProjectProperty, name='minimum_entry_length')
grok.global_utility(minimum_entry_length_property, provides=interfaces.IDefaultMilestoneProperty, name='minimum_entry_length')


def ticket_minimum_entry_length_property():
    """ Ticket property defining the minimum length of time entries
    """
    property = minimum_entry_length_property()
    property.editable = False
    return property
grok.global_utility(ticket_minimum_entry_length_property, provides=interfaces.IDefaultTicketProperty, name='minimum_entry_length')


def maximum_week_hours_property():
    """ Project and milestone property defining the maximum hours per week
        to be worked on a ticket
    """
    property = properties.FloatProperty()
    property.id = 'maximum_week_hours'
    property.name = _(u'Maximum hours per week')
    property.initial = True
    property.editable = True
    property.customizable = False
    property.searchable = False
    property.order = 220
    return property
grok.global_utility(maximum_week_hours_property, provides=interfaces.IDefaultProjectProperty, name='maximum_week_hours')
grok.global_utility(maximum_week_hours_property, provides=interfaces.IDefaultMilestoneProperty, name='maximum_week_hours')


def ticket_maximum_week_hours_property():
    """ Ticket property defining the maximum hours per week to be worked on
        a ticket
    """
    property = maximum_week_hours_property()
    property.editable = False
    return property
grok.global_utility(ticket_maximum_week_hours_property, provides=interfaces.IDefaultTicketProperty, name='maximum_week_hours')
