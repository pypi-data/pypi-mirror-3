from zope import interface
from zope.component.interfaces import IObjectEvent

from z3c.relationfield import Relation, RelationList
from z3c.relationfield.interfaces import IHasRelations

from horae.core import interfaces
from horae.properties.interfaces import IPropertied, IMultipleChoiceProperty
from horae.auth.interfaces import IShareable


class ITicketReferenceProperty(IMultipleChoiceProperty):
    """ A property referencing multiple tickets
    """


class IClientContainer(interfaces.IContainer):
    """ A container for clients
    """


class IClientContainerHolder(interface.Interface):
    """ Marker interface for objects adaptable to IClientContainer
    """


class IClient(interfaces.IIntId, IPropertied, IShareable):
    """ A client
    """


class IProjectContainer(interfaces.IContainer):
    """ A container for projects
    """


class IProjectContainerHolder(interface.Interface):
    """ Marker interface for objects adaptable to IProjectContainer
    """


class IProject(interfaces.IIntId, IPropertied, IShareable):
    """ A project
    """


class IMilestoneContainer(interfaces.IContainer):
    """ A container for milestones
    """


class IMilestoneContainerHolder(interface.Interface):
    """ Marker interface for objects adaptable to IMilestoneContainer
    """


class IMilestone(interfaces.IIntId, IPropertied, IHasRelations):
    """ A milestone
    """


class ITicketContainer(interfaces.IContainer):
    """ A container for tickets
    """


class ITicketContainerHolder(interface.Interface):
    """ Marker interface for objects adaptable to ITicketContainer
    """


class ITicket(interfaces.IIntId, IPropertied, IShareable):
    """ A ticket
    """


class IRelationTicket(ITicket, IHasRelations):
    """ A ticket using zc.relation to reference the milestone
    """

    milestone_rel = Relation()
    dependencies_rel = RelationList()


class ITicketDependencies(interface.Interface):
    """ Dependency information of a ticket
    """

    def dependents(object=True):
        """ Returns a list of the immediate dependents of a ticket
        """

    def all_dependents(object=True):
        """ Returns a list of all the dependents (including dependents
            of dependents) of a ticket
        """

    def dependencies(object=True):
        """ Returns a list of the immediate dependencies of a ticket
        """

    def all_dependencies(object=True):
        """ Returns a list of all the dependencies (including dependencies
            of dependencies) of a ticket
        """


class ITicketChangedEvent(IObjectEvent):
    """ A ticket has been changed
    """

    change = interface.Attribute("The changes made to the ticket (IPropertyChange)")
    previous = interface.Attribute("A dictionary holding the previous values of the properties")


class ITickets(interface.Interface):
    """ Ticket iterator
    """

    def __iter__():
        """ Iterator over the tickets of the given object
        """
