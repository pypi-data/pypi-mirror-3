import grok

from zope import component
from zope.schema import vocabulary
from zope.site.hooks import getSite
from zope.app.intid.interfaces import IIntIds

from z3c.relationfield.interfaces import IHasRelations
from z3c.relationfield import RelationValue

from horae.core import utils
from horae.properties import interfaces
from horae.properties import properties
from horae.search.properties import BaseSearchableProperty, KeywordProperty

from horae.ticketing import _
from horae.ticketing.interfaces import ITicketContainerHolder, ITicketContainer, ITicketReferenceProperty, ITicketDependencies


class TicketReferenceProperty(properties.MultipleChoiceProperty):
    """ A property referencing multiple tickets
    """
    grok.implements(ITicketReferenceProperty)

    def _collectReferences(self, container, ticket):
        references = []
        for ref in ticket.get_property(self.id, []):
            references.append(ref)
            ref = container.get_object(ref)
            if ref is not None:
                references.extend(self._collectReferences(container, ref))
        return references

    def render(self, value, context, request, widget=None):
        """ Returns the rendered value
        """
        if not value:
            if widget is None:
                return _(u'None')
            return None
        base = grok.url(request, getSite())
        return ', '.join(['<a href="%s/++ticket++%s">#%s</a>' % (base, val, val) for val in value])

    def getVocabulary(self, context):
        """ Returns the vocabulary used by the field
        """
        terms = []
        parent = utils.findParentByInterface(context, ITicketContainerHolder)
        deps = ITicketDependencies(context, None)
        dependents = []
        if deps is not None:
            dependents = [id for id in deps.all_dependents(False)]
        if parent is not None:
            container = ITicketContainer(parent)
            for ticket in container.objects():
                if ticket is context or ticket.id in dependents:
                    continue
                terms.append(vocabulary.SimpleTerm(ticket.id, str(ticket.id), '#%s (%s)' % (ticket.id, ticket.get_property('name', ''))))
        return vocabulary.SimpleVocabulary(terms)

    def apply(self, obj, **data):
        """ Applies the data to the obj
        """
        if (not self.id in data or
            not IHasRelations.providedBy(obj) or
            not hasattr(obj, self.id + '_rel')):
            return
        dependencies = data[self.id]
        if not dependencies:
            setattr(obj, self.id + '_rel', None)
            return
        parent = utils.findParentByInterface(obj, ITicketContainerHolder)
        if parent is not None:
            container = ITicketContainer(parent)
            intids = component.getUtility(IIntIds)
            value = []
            for dep in dependencies:
                dep = container.get(str(dep))
                if dep is None:
                    continue
                value.append(RelationValue(intids.queryId(dep)))
            setattr(obj, self.id + '_rel', value)


class SearchableTicketReferenceProperty(BaseSearchableProperty):
    """ Searchable ticket reference property
    """
    grok.context(ITicketReferenceProperty)

    def index(self, value, field, context):
        """ Processes the value before indexing
        """
        if not value or not len(value):
            return None
        return list(value)

    def indexes(self):
        """ Returns a list of indexes required for this property
        """
        return []

    def fields(self, catalog, context, request):
        """ Returns a list of fields used to search for values of this property
        """
        return []

    def field_names(self):
        """ Returns a list of field names provided by this property
        """
        return []

    def query(self, **data):
        """ Returns a query
        """
        return None


def name_property():
    """ Global property providing a field to define the name
    """
    property = properties.TextLineProperty()
    property.id = 'name'
    property.name = _(u'Name')
    property.required = True
    property.order = 1
    property.display = False
    return property
grok.global_utility(name_property, provides=interfaces.IDefaultGlobalProperty, name='name')


def description_property():
    """ Global property providing a field to define the description
    """
    property = properties.RichTextProperty()
    property.id = 'description'
    property.name = _(u'Description')
    property.order = 10
    property.display = False
    return property
grok.global_utility(description_property, provides=interfaces.IDefaultGlobalProperty, name='description')


def tags_property():
    """ Global property providing a field to set tags
    """
    property = KeywordProperty()
    property.id = 'tags'
    property.name = _(u'Tags')
    property.order = 250
    property.display = True
    return property
grok.global_utility(tags_property, provides=interfaces.IDefaultGlobalProperty, name='tags')


def name_ticket_property():
    """ Ticket property providing a field to define
        the name but only on the edit form
    """
    property = name_property()
    property.editable = False
    return property
grok.global_utility(name_ticket_property, provides=interfaces.IDefaultTicketProperty, name='name')


def description_ticket_property():
    """ Ticket property providing a field to define
        the description but only on the edit form
    """
    property = description_property()
    property.editable = False
    return property
grok.global_utility(description_ticket_property, provides=interfaces.IDefaultTicketProperty, name='description')


def estimated_hours_property():
    """ Ticket property providing a field to define the estimated hours
    """
    property = properties.FloatProperty()
    property.id = 'estimated_hours'
    property.name = _(u'Estimated hours')
    property.order = 21
    property.min = 0.0
    property.initial = True
    property.editable = False
    property.complete = False
    return property
grok.global_utility(estimated_hours_property, provides=interfaces.IDefaultTicketProperty, name='estimated_hours')


def start_due_date_property():
    """ Project and milestone property providing a fields to define
        the start and due date
    """
    property = properties.DateTimeRangeProperty()
    property.id = 'start_due_date'
    property.name = _(u'Start date')
    property.name_end = _(u'Due date')
    property.default = None
    property.default_now = False
    property.default_diff = 0.0
    property.order = 140
    property.complete = False
    return property
grok.global_utility(start_due_date_property, provides=interfaces.IDefaultProjectProperty, name='start_due_date')
grok.global_utility(start_due_date_property, provides=interfaces.IDefaultMilestoneProperty, name='start_due_date')


def ticket_start_due_date_property():
    """ Ticket property providing a fields to define
        the start and due date
    """
    property = start_due_date_property()
    property.editable = False
    property.complete = False
    return property
grok.global_utility(ticket_start_due_date_property, provides=interfaces.IDefaultTicketProperty, name='start_due_date')


def responsible_property():
    """ Ticket property providing a field to define the responsible user
    """
    property = properties.UserRoleProperty()
    property.id = 'responsible'
    property.name = _(u'Responsible')
    property.role = u'horae.Responsible'
    property.order = 17
    return property
grok.global_utility(responsible_property, provides=interfaces.IDefaultTicketProperty, name='responsible')


def comment_title_property():
    """ Ticket property providing a field to enter a comment title for
        every change made
    """
    property = properties.TextLineProperty()
    property.id = 'title'
    property.name = _(u'Title')
    property.initial = False
    property.order = 0
    property.display = False
    property.remember = False
    property.searchable = False
    return property
grok.global_utility(comment_title_property, provides=interfaces.IDefaultTicketProperty, name='title')


def comment_property():
    """ Ticket property providing a field to enter a comment for
        every change made
    """
    property = properties.RichTextProperty()
    property.id = 'comment'
    property.name = _(u'Comment')
    property.initial = False
    property.order = 10
    property.display = False
    property.remember = False
    property.searchable = False
    return property
grok.global_utility(comment_property, provides=interfaces.IDefaultTicketProperty, name='comment')


def milestone_property():
    """ Ticket property providing a field to select the associated milestone
    """
    property = properties.MilestoneProperty()
    property.id = 'milestone'
    property.name = _(u'Milestone')
    property.order = 19
    return property
grok.global_utility(milestone_property, provides=interfaces.IDefaultTicketProperty, name='milestone')


def hidden_fields_property():
    """ Ticket property providing a field to select the fields to hide for
        users not having the **horae.ViewHiddenProperties** permission
    """
    property = properties.FieldsProperty()
    property.id = 'hidden'
    property.name = _(u'Hidden fields')
    property.initial = False
    property.order = 200
    property.customizable = False
    property.display = False
    property.remember = False
    property.searchable = False
    property.permission = 'horae.ViewHiddenProperties'
    return property
grok.global_utility(hidden_fields_property, provides=interfaces.IDefaultTicketProperty, name='hidden')


def ticket_reference_property():
    """ Ticket property providing a field to select tickets this ticket depends on
    """
    property = TicketReferenceProperty()
    property.id = 'dependencies'
    property.name = _(u'Dependencies')
    property.initial = True
    property.editable = True
    property.customizable = False
    property.order = 210
    property.complete = False
    return property
grok.global_utility(ticket_reference_property, provides=interfaces.IDefaultTicketProperty, name='dependencies')
