import grok

from zope import schema
from zope import component
from zope.location.interfaces import ILocationInfo
from zope.intid.interfaces import IIntIds
from zope.publisher.interfaces.browser import IBrowserRequest

from zc.relation.interfaces import ICatalog
from hurry import query

from horae.core import container
from horae.core.interfaces import IHorae
from horae.properties.interfaces import IGlobalPropertiesHolder, IProjectPropertiesHolder, \
    IMilestonePropertiesHolder, ITicketPropertiesHolder, IPropertied, IObjectType
from horae.properties import propertied
from horae.lifecycle import lifecycle
from horae.timeaware import timeaware
from horae.timeaware.interfaces import ITimeEntry
from horae.layout import layout

from horae.ticketing import _
from horae.ticketing import interfaces


class Client(grok.Container, propertied.PropertiedMixin, lifecycle.LifecycleAwareMixin):
    """ A client
    """
    grok.implements(interfaces.IClient,
                    interfaces.IProjectContainerHolder,
                    IGlobalPropertiesHolder,
                    IProjectPropertiesHolder,
                    IMilestonePropertiesHolder,
                    ITicketPropertiesHolder)
    id = schema.fieldproperty.FieldProperty(interfaces.IClient['id'])


@grok.adapter(IHorae)
@grok.implementer(interfaces.ITickets)
def tickets_of_horae(horae):
    """ Iterator over all tickets
    """
    for client in interfaces.IClientContainer(horae).objects():
        for ticket in interfaces.ITickets(client):
            yield ticket


@grok.adapter(interfaces.IClient)
@grok.implementer(interfaces.ITickets)
def tickets_of_client(client):
    """ Iterator over the tickets of a client
    """
    for project in interfaces.IProjectContainer(client).objects():
        for ticket in interfaces.ITickets(project):
            yield ticket


@grok.adapter(interfaces.IClient)
@grok.implementer(IObjectType)
def object_type_of_client(client):
    """ User readable object type of a client
    """
    return lambda: _(u'Client')


class Project(grok.Container, propertied.PropertiedMixin, lifecycle.LifecycleAwareMixin):
    """ A project containing tickets and/or milestones
    """
    grok.implements(interfaces.IProject,
                    interfaces.ITicketContainerHolder,
                    interfaces.IMilestoneContainerHolder,
                    IGlobalPropertiesHolder,
                    IMilestonePropertiesHolder,
                    ITicketPropertiesHolder)
    id = schema.fieldproperty.FieldProperty(interfaces.IProject['id'])


@grok.adapter(interfaces.IProject)
@grok.implementer(interfaces.ITickets)
def tickets_of_project(project):
    """ Iterator over the tickets of a project
    """
    return interfaces.ITicketContainer(project).objects()


@grok.adapter(interfaces.IProject)
@grok.implementer(IObjectType)
def object_type_of_project(project):
    """ User readable object type of a project
    """
    return lambda: _(u'Project')


class Milestone(grok.Container, propertied.PropertiedMixin, lifecycle.LifecycleAwareMixin):
    """ A milestone containing tickets
    """
    grok.implements(interfaces.IMilestone,
                    IGlobalPropertiesHolder,
                    ITicketPropertiesHolder)
    id = schema.fieldproperty.FieldProperty(interfaces.IMilestone['id'])


@grok.adapter(interfaces.IMilestone)
@grok.implementer(interfaces.ITickets)
def tickets_of_milestone(milestone):
    """ Iterator over the tickets of a milestone
    """
    return component.getUtility(query.interfaces.IQuery).searchResults(query.And(query.set.AnyOf(('catalog', 'implements'), [interfaces.ITicket.__identifier__, ]),
                                                                                 query.set.AnyOf(('catalog', 'path'), [ILocationInfo(milestone).getPath(), ])), unrestricted=True)


@grok.adapter(interfaces.IMilestone)
@grok.implementer(IObjectType)
def object_type_of_milestone(milestone):
    """ User readable object type of a milestone
    """
    return lambda: _(u'Milestone')


class Ticket(grok.Container, timeaware.PersistentTimeEntryFactory, propertied.TicketPropertiedMixin, lifecycle.LifecycleAwareMixin):
    """ A ticket
    """
    grok.implements(interfaces.IRelationTicket)
    id = schema.fieldproperty.FieldProperty(interfaces.ITicket['id'])
    milestone_rel = None
    dependencies_rel = None


@grok.adapter(interfaces.ITicket)
@grok.implementer(interfaces.ITickets)
def tickets_of_ticket(ticket):
    """ Iterator over the tickets of a ticket
    """
    yield ticket


@grok.subscribe(ITimeEntry, grok.IObjectAddedEvent)
def timeentry_creation(obj, event):
    """ Links the created time entry with the last
        :py:class:`horae.properties.interfaces.IPropertyChange`
    """
    if interfaces.ITicket.providedBy(event.newParent):
        IPropertied(event.newParent).set_property('timeentry', obj)


@grok.adapter(interfaces.ITicket)
@grok.implementer(IObjectType)
def object_type_of_ticket(ticket):
    """ User readable object type of a ticket
    """
    return lambda: _(u'Ticket')


class TicketDependencies(grok.Adapter):
    """ Dependency information of a ticket
    """
    grok.context(interfaces.ITicket)
    grok.implements(interfaces.ITicketDependencies)

    def dependents(self, object=True):
        """ Returns an iterator of the immediate dependents of a ticket
        """
        catalog = component.queryUtility(ICatalog)
        intids = component.queryUtility(IIntIds)
        if catalog is not None and intids is not None:
            for r in catalog.findRelations({'to_id': intids.getId(self.context), 'from_attribute': 'dependencies_rel'}):
                if object:
                    yield r.from_object
                else:
                    yield r.from_object.id

    def all_dependents(self, object=True):
        """ Returns a list of all the dependents (including dependents
            of dependents) of a ticket
        """
        for dependent in self.dependents():
            if object:
                yield dependent
            else:
                yield dependent.id
            for dep_of_dep in interfaces.ITicketDependencies(dependent).all_dependents(object):
                yield dep_of_dep

    def dependencies(self, object=True):
        """ Returns a list of the immediate dependencies of a ticket
        """
        catalog = component.queryUtility(ICatalog)
        intids = component.queryUtility(IIntIds)
        if catalog is not None and intids is not None:
            for r in catalog.findRelations({'from_id': intids.getId(self.context), 'from_attribute': 'dependencies_rel'}):
                if object:
                    yield r.to_object
                else:
                    yield r.to_object.id

    def all_dependencies(self, object=True):
        """ Returns a list of all the dependencies (including dependencies
            of dependencies) of a ticket
        """
        for dependency in self.dependencies():
            if object:
                yield dependency
            else:
                yield dependency.id
            for dep_of_dep in interfaces.ITicketDependencies(dependency).all_dependencies(object):
                yield dep_of_dep


class ClientContainer(container.Container):
    """ A container for clients
    """
    grok.implements(interfaces.IClientContainer)

    def id_key(self):
        return 'client'


@grok.adapter(interfaces.IClientContainerHolder)
@grok.implementer(interfaces.IClientContainer)
def client_container_of_holder(holder):
    """ Returns a :py:class:`ClientContainer` if it does not yet exist
        one is created
    """
    if not 'clients' in holder:
        holder['clients'] = ClientContainer()
    return holder['clients']


class ProjectContainer(container.Container):
    """ A container for projects
    """
    grok.implements(interfaces.IProjectContainer)

    def id_key(self):
        return 'project'


@grok.adapter(interfaces.IProjectContainerHolder)
@grok.implementer(interfaces.IProjectContainer)
def project_container_of_holder(holder):
    """ Returns a :py:class:`ProjectContainer` if it does not yet exist
        one is created
    """
    if not 'projects' in holder:
        holder['projects'] = ProjectContainer()
    return holder['projects']


class MilestoneContainer(container.Container):
    """ A container for milestones
    """
    grok.implements(interfaces.IMilestoneContainer)

    def id_key(self):
        return 'milestone'


@grok.adapter(interfaces.IMilestoneContainerHolder)
@grok.implementer(interfaces.IMilestoneContainer)
def milestone_container_of_holder(holder):
    """ Returns a :py:class:`MilestoneContainer` if it does not yet exist one is created
    """
    if not 'milestones' in holder:
        holder['milestones'] = MilestoneContainer()
    return holder['milestones']


class TicketContainer(container.Container):
    """ A container for tickets
    """
    grok.implements(interfaces.ITicketContainer)

    def id_key(self):
        return 'ticket'


@grok.adapter(interfaces.ITicketContainerHolder)
@grok.implementer(interfaces.ITicketContainer)
def ticket_container_of_holder(holder):
    """ Returns a :py:class:`TicketContainer` if it does not yet exist
        one is created
    """
    if not 'tickets' in holder:
        holder['tickets'] = TicketContainer()
    return holder['tickets']


class PropertiedBreadcrumbs(layout.BaseBreadcrumbs):
    """ Making clients, projects, milestones and tickets visible in
        breadcrumbs
    """
    grok.adapts(IPropertied, IBrowserRequest)

    @property
    def name(self):
        return self.context.name
