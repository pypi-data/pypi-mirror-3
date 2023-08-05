import grok
from hashlib import sha1

from zope import schema
from zope import component
from zope.i18n import translate
from zope.site.hooks import getSite
from zope.traversing.interfaces import ITraversable
from zope.publisher.interfaces import IRequest

from plone.memoize import ram
from megrok import navigation

from hurry.query import query, set

from horae.core.utils import findParentByInterface, getRequest
from horae.core.interfaces import IHorae
from horae.auth.utils import getUser
from horae.auth.interfaces import IUser, IUserURL
from horae.layout import layout
from horae.layout.interfaces import IDisplayView, IViewsMenu, IObjectTableActionsProvider
from horae.search.search import SearchMixin, row_factory_cache_key

from horae.ticketing.interfaces import ITicket, IClient, IProject, IMilestone
from horae.ticketing import _

grok.templatedir('templates')


class UserTraverser(grok.MultiAdapter):
    """ Namespace traverser for users enabling traversing using an URL
        of the form *http://localhost:8080/app/++user++<username>*
    """
    grok.adapts(IHorae, IRequest)
    grok.name('user')
    grok.implements(ITraversable)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def traverse(self, name, furtherPath):
        return getUser(name)


class Index(SearchMixin, layout.View):
    """ Base implementation of a view of a user rendering the tickets he is responsible for
    """
    grok.implements(IDisplayView)
    grok.context(IUser)
    grok.require('horae.View')
    grok.template('user')
    grok.baseclass()
    no_results_msg = _(u'The selected user is currently not responsible for any ticket.')
    page_size = None
    project_urls = {}
    client_urls = {}
    milestone_urls = {}

    @ram.cache(row_factory_cache_key)
    def row_factory(self, object, columns, request):
        row = super(Index, self).row_factory(object, columns, request)
        if 'dependencies' in columns:
            row['dependencies'] = object.find_property('dependencies').render(object.get_property('dependencies'), self.context, self.request)
        if 'client' in columns:
            client = findParentByInterface(object, IClient)
            if not client.id in self.client_urls:
                self.client_urls[client.id] = self.url(client)
            row['client'] = '<a href="%s" title="%s">#%s</a>' % (self.client_urls[client.id], client.name, client.id)
        if 'project' in columns:
            project = findParentByInterface(object, IProject)
            if not project.id in self.project_urls:
                self.project_urls[project.id] = self.url(project)
            row['project'] = '<a href="%s" title="%s">#%s</a>' % (self.project_urls[project.id], project.name, project.id)
        if 'milestone' in columns:
            milestone = object.milestone
            if milestone is not None and not milestone.id in self.milestone_urls:
                self.milestone_urls[milestone.id] = self.url(milestone)
            row['milestone'] = milestone is not None and '<a href="%s" title="%s">#%s</a>' % (self.milestone_urls[milestone.id], milestone.name, milestone.id) or u''
        return row

    @property
    def caption(self):
        return _(u'Open tickets of ${user}', mapping={'user': self.context.name})

    def query(self):
        return query.And(set.AnyOf(('catalog', 'implements'), [ITicket.__identifier__, ]),
                         query.Eq(('properties', 'responsible'), self.context.username),
                         query.Eq(('catalog', 'complete'), 0))

    def base_url(self):
        return self.url(getSite()) + '/++user++' + self.context.username

    def session_key(self):
        return sha1(self.base_url()).hexdigest()

    def results(self):
        self.client_urls = {}
        self.project_urls = {}
        self.milestone_urls = {}
        results, table = super(Index, self).results()
        if table is not None:
            table.columns = [column for column in table.columns if not column[0] in ('type', 'modification_date', 'modifier', 'complete', 'offer')]
        return results, table

    def createTable(self):
        table = super(Index, self).createTable()
        if table is not None:
            table.columns.insert(2, ('dependencies', _('Dependencies')))
            table.columns.insert(3, ('client', _(u'Client')))
            table.columns.insert(4, ('project', _(u'Project')))
            table.columns.insert(5, ('milestone', _(u'Milestone')))
        return table

    def filterable(self):
        filterable = super(Index, self).filterable()
        catalog = component.getUtility(query.interfaces.IQuery)
        clients = catalog.searchResults(query.And(set.AnyOf(('catalog', 'implements'), [IClient.__identifier__, ]),
                                                  query.Eq(('catalog', 'complete'), 0),
                                                  query.Eq(('catalog', 'offer'), 0)), sort_field=('catalog', 'sortable_name'))
        terms = []
        for client in clients:
            terms.append(schema.vocabulary.SimpleTerm(client.id, client.id, client.name))
        filterable['client'] = schema.vocabulary.SimpleVocabulary(terms)

        projects = catalog.searchResults(query.And(set.AnyOf(('catalog', 'implements'), [IProject.__identifier__, ]),
                                                   query.Eq(('catalog', 'complete'), 0),
                                                   query.Eq(('catalog', 'offer'), 0)), sort_field=('catalog', 'sortable_name'))
        terms = []
        for project in projects:
            terms.append(schema.vocabulary.SimpleTerm(project.id, project.id, project.name))
        filterable['project'] = schema.vocabulary.SimpleVocabulary(terms)

        milestones = catalog.searchResults(query.And(set.AnyOf(('catalog', 'implements'), [IMilestone.__identifier__, ]),
                                                     query.Eq(('catalog', 'complete'), 0),
                                                     query.Eq(('catalog', 'offer'), 0)), sort_field=('catalog', 'sortable_name'))
        terms = []
        for milestone in milestones:
            terms.append(schema.vocabulary.SimpleTerm(milestone.id, milestone.id, milestone.name))
        filterable['milestone'] = schema.vocabulary.SimpleVocabulary(terms)
        return filterable


class UserIndex(Index):
    """ View of a user rendering the tickets he is responsible for
    """
    grok.name('index')
    navigation.menuitem(IViewsMenu, _(u'Tickets'))


class UserURL(grok.Adapter):
    """ Provides an URL for :py:class:`horae.auth.interfaces.IUser` using
        the namespace traverser :py:class:`UserTraverser`
    """
    grok.context(IUser)
    grok.implements(IUserURL)

    def __call__(self):
        try:
            return grok.url(getRequest(), getSite()) + '/++user++' + self.context.username
        except:
            return None


class UserTicketActionProvider(grok.Adapter):
    """ Action provider for users adding a button to view the tickets
        a user is responsible for
    """
    grok.context(IUser)
    grok.implements(IObjectTableActionsProvider)
    grok.name('horae.ticketing.user.tickets')

    order = 1

    def actions(self, request):
        return [{'url': '%s/++user++%s' % (grok.url(request, findParentByInterface(self.context, IHorae)), self.context.username),
                 'label': translate(_(u'Tickets'), context=request),
                 'cssClass': 'button-alternative'}, ]
