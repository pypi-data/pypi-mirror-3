import grok

from zope import component

from zope.app.intid.interfaces import IIntIds
from zc.relation.interfaces import ICatalog

from horae.core import utils
from horae.properties.interfaces import IProperties, \
    IClientProperties, IClientPropertiesHolder, \
    IProjectProperties, IProjectPropertiesHolder, \
    IMilestoneProperties, IMilestonePropertiesHolder, \
    ITicketProperties, ITicketPropertiesHolder
from horae.timeaware.interfaces import ITimeAware
from horae.timeaware.timeaware import TimeAware

from horae.ticketing import interfaces


@grok.adapter(interfaces.IClient, name='client')
@grok.implementer(IProperties)
def properties_for_clients(propertied):
    """ Provides client properties for clients
    """
    holder = utils.findParentByInterface(propertied, IClientPropertiesHolder)
    return IClientProperties(holder)


@grok.adapter(interfaces.IProject, name='project')
@grok.implementer(IProperties)
def properties_for_projects(propertied):
    """ Provides project properties for projects
    """
    holder = utils.findParentByInterface(propertied, IProjectPropertiesHolder)
    return IProjectProperties(holder)


@grok.adapter(interfaces.IMilestone, name='milestone')
@grok.implementer(IProperties)
def properties_for_milestones(propertied):
    """ Provides milestone properties for milestones
    """
    holder = utils.findParentByInterface(propertied, IMilestonePropertiesHolder)
    return IMilestoneProperties(holder)


@grok.adapter(interfaces.ITicket, name='ticket')
@grok.implementer(IProperties)
def properties_for_tickets(propertied):
    """ Provides ticket properties for tickets
    """
    holder = utils.findParentByInterface(propertied, ITicketPropertiesHolder)
    return ITicketProperties(holder)


@grok.adapter(interfaces.IProjectContainerHolder)
@grok.implementer(ITimeAware)
def time_of_project_container_holder(holder):
    """ Provides time aware functionality for project container holders
    """
    projects = interfaces.IProjectContainer(holder)
    timeaware = TimeAware()
    for project in projects.objects():
        timeaware.extend(ITimeAware(project).objects())
    return timeaware


@grok.adapter(interfaces.ITicketContainerHolder)
@grok.implementer(ITimeAware)
def time_of_ticket_container_holder(holder):
    """ Provides time aware functionality for ticket container holders
    """
    tickets = interfaces.ITicketContainer(holder)
    timeaware = TimeAware()
    for ticket in tickets.objects():
        timeaware.extend(ITimeAware(ticket).objects())
    return timeaware


@grok.adapter(interfaces.IMilestone)
@grok.implementer(ITimeAware)
def time_of_milestone(milestone):
    """ Provides time aware functionality for milestone container holders
    """
    catalog = component.getUtility(ICatalog)
    intids = component.getUtility(IIntIds)
    timeaware = TimeAware()
    for relation in catalog.findRelations({'to_id': intids.getId(milestone)}):
        timeaware.extend(ITimeAware(relation.from_object).objects())
    return timeaware
