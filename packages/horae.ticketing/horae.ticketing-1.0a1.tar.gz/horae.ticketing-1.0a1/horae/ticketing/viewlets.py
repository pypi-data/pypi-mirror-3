import grok
from hashlib import sha1

from grokcore.chameleon.components import PageTemplateFile
from zope.interface import Interface
from zope.component import queryAdapter
from zope.schema import vocabulary
from zope.component import getUtility, getMultiAdapter
from zope.location.interfaces import ILocationInfo

from hurry import query

from plone.memoize import ram

from horae.core import utils
from horae.auth.utils import getUser
from horae.auth.interfaces import IUserURL, IUser
from horae.search.search import SearchMixin, row_factory_cache_key
from horae.layout import layout
from horae.layout.viewlets import ContentAfterManager, ContentBeforeManager
from horae.layout.interfaces import IDisplayView, IViewView
from horae.layout.resource import nestedlist
from horae.properties.interfaces import IPropertied

from horae.ticketing import _
from horae.ticketing import interfaces

grok.context(Interface)
grok.templatedir('templates')


class Name(layout.Viewlet):
    """ Renders the name of clients, projects, milestones and tickets
    """
    grok.viewletmanager(ContentBeforeManager)
    grok.context(IPropertied)
    grok.view(IDisplayView)
    grok.order(30)

    def update(self):
        self.name = self.context.name
        self.description = None
        self.id = self.context.id


class Description(layout.Viewlet):
    """ Renders the description of clients, projects, milestones and tickets
    """
    grok.viewletmanager(ContentBeforeManager)
    grok.context(IPropertied)
    grok.view(IDisplayView)
    grok.order(40)

    def update(self):
        self.description = self.context.description


class UserName(Name):
    """ Renders the name of a user
    """
    grok.context(IUser)

    def update(self):
        self.name = _(u'User')
        self.description = self.context.name
        self.id = None


class Listing(layout.Viewlet, SearchMixin):
    """ Base class for viewlets rendering a list of objects
    """
    grok.baseclass()
    # To be defined by subclass
    css_class = None
    caption = None
    interface = None
    page_size = None
    current_context = None
    current_view = None

    cell_template = '<a href="%(url)s">%(name)s</a>'

    def query(self):
        return query.And(query.set.AnyOf(('catalog', 'implements'), [self.interface.__identifier__, ]),
                         query.set.AnyOf(('catalog', 'path'), [ILocationInfo(self.context).getPath(), ]))

    def base_url(self):
        context = self.context
        if self.current_context is not None:
            context = self.current_context
        view = self.view
        if self.current_view is not None:
            view = self.current_view
        return grok.url(self.request, context) + '/' + view.__name__

    def session_key(self):
        return sha1(grok.url(self.request, self.context) + '/' + self.view.__name__ + self.interface.__identifier__).hexdigest()

    def results(self):
        results, table = super(Listing, self).results()
        if table is not None:
            table.columns = [column for column in table.columns if not column[0] == 'type']
        table.css_class = self.css_class
        return results, table

    def render(self):
        return self.table()


class NestedList(layout.Viewlet, SearchMixin):
    """ Base class for viewlets rendering a nested list of objects
    """
    grok.baseclass()
    recurse_template = PageTemplateFile('templates/nestedlist_recurse.cpt')

    # To be defined by subclass
    caption = None
    empty_message = None
    types = ()
    renderers = ()
    item_template = '<h%(level)s class="heading"><a class="detail" href="%(url)s">%(name)s <small class="id">#%(id)s</small></a></h%(level)s>'

    def query(self, context, iface):
        return query.And(query.set.AnyOf(('catalog', 'implements'), [iface.__identifier__, ]),
                         query.set.AnyOf(('catalog', 'path'), [ILocationInfo(context).getPath(), ]))

    def results(self, context, iface):
        q = self.query(context, iface)
        if not q:
            return None
        results = getUtility(query.interfaces.IQuery).searchResults(q, **self.searchArguments())
        return results

    def namespace(self):
        namespace = super(NestedList, self).namespace()
        namespace['childs'] = self.childs
        return namespace

    def recurse(self, childs):
        self.childs = childs
        return self.recurse_template(self)

    def render_item(self, item, level):
        return self.item_template % dict(level=level, url=self.view.url(item), name=item.name, id=item.id)

    def update(self):
        nestedlist.need()
        self.childs = []
        self.list = []
        childs = self.results(self.context, self.types[-1])
        for child in childs:
            parents = list(self.types[:-1])
            clist = self.list
            while parents:
                iface = parents.pop(0)
                parent = utils.findParentByInterface(child, iface)
                if clist and clist[-1]['item'] is parent:
                    clist = clist[-1]['childs']
                else:
                    clist.append({'item': parent, 'childs': [], 'renderer': self.renderers[self.types.index(iface)]})
                    clist = clist[-1]['childs']
            clist.append({'item': child, 'childs': [], 'renderer': self.renderers[-1]})


class ClientsProjects(NestedList):
    """ Renders a list of projects including the associated client
    """
    grok.viewletmanager(ContentAfterManager)
    grok.view(IViewView)
    grok.context(interfaces.IClientContainerHolder)
    grok.template('nestedlist')
    grok.order(10)
    caption = _(u'Projects')
    empty_message = _(u'No clients and projects available')
    types = (interfaces.IProject,)
    renderers = ()
    item_template = '<h%(level)s class="heading"><a class="parent" href="%(clienturl)s">%(clientname)s <small class="id">#%(clientid)s</small></a><a class="detail" href="%(url)s">%(name)s <small class="id">#%(id)s</small></a></h%(level)s>'

    def update(self):
        self.renderers = (self.render_project,)
        super(ClientsProjects, self).update()

    @ram.cache(lambda method, *args, **kwargs: (method.__module__, method.__name__, args[1], args[1].modification_date, args[2], args[0].request.getURL()))
    def render_item(self, item, level):
        client = utils.findParentByInterface(item, interfaces.IClient)
        return self.item_template % dict(level=level, clienturl=self.view.url(client), clientname=client.name, clientid=client.id, url=self.view.url(item), name=item.name, id=item.id)

    def render_project(self, project, childs):
        return self.render_item(project, 2)


class Projects(NestedList):
    """ Renders a nested list of projects of a client and their milestones
    """
    grok.viewletmanager(ContentAfterManager)
    grok.view(IViewView)
    grok.context(interfaces.IProjectContainerHolder)
    grok.template('nestedlist')
    grok.order(20)
    empty_message = _(u'No projects available')
    types = (interfaces.IProject, interfaces.IMilestone)
    renderers = ()

    def update(self):
        self.types = (interfaces.IProject, interfaces.IMilestone)
        self.renderers = (self.render_project, self.render_milestone)
        super(Projects, self).update()
        if not len(self.list):
            self.types = (interfaces.IProject,)
            self.renderers = (self.render_project,)
            super(Projects, self).update()

    def render_project(self, project, childs):
        return self.render_item(project, 2)

    def render_milestone(self, milestone, childs):
        return self.render_item(milestone, 3)


class Tickets(Listing):
    """ Renders a list of tickets
    """
    grok.viewletmanager(ContentAfterManager)
    grok.view(IViewView)
    grok.context(interfaces.ITicketContainerHolder)
    grok.order(40)
    caption = _(u'Tickets with no milestone')
    interface = interfaces.ITicket
    css_class = 'nestedlisting'

    def update(self):
        super(Tickets, self).update()
        if interfaces.IMilestoneContainerHolder.providedBy(self.context) and \
           not len(interfaces.IMilestoneContainer(self.context)):
            self.caption = _(u'Tickets')

    @ram.cache(row_factory_cache_key)
    def row_factory(self, object, columns, request):
        row = super(Tickets, self).row_factory(object, columns, request)
        responsible = object.responsible
        user = getUser(responsible)
        url = user is not None and queryAdapter(user, IUserURL) or None
        row['responsible'] = user and (url is not None and '<a href="%s">%s</a>' % (url(), user.name) or user.name) or responsible
        return row

    def query(self):
        return query.And(query.set.AnyOf(('catalog', 'implements'), [self.interface.__identifier__, ]),
                         query.set.AnyOf(('catalog', 'path'), [ILocationInfo(self.context).getPath(), ]),
                         query.Eq(('catalog', 'milestone'), u'None'))

    def filterable(self):
        filterable = super(Tickets, self).filterable()
        filterable['responsible'] = vocabulary.getVocabularyRegistry().get(self.context, 'horae.auth.vocabulary.usernames')
        return filterable

    def createTable(self):
        table = super(Tickets, self).createTable()
        if table is not None:
            table.columns.insert(2, ('responsible', _(u'Responsible')))
            table.sortable['responsible'] = 'responsible'
        return table


class Milestones(NestedList):
    """ Renders a nested list of milestones and their associated tickets
    """
    grok.viewletmanager(ContentAfterManager)
    grok.view(IViewView)
    grok.context(interfaces.IMilestoneContainerHolder)
    grok.template('nestedlist')
    grok.order(30)
    types = (interfaces.IMilestone,)
    renderers = ()

    def update(self):
        self.renderers = (self.render_milestone,)
        super(Milestones, self).update()

    def render_milestone(self, milestone, childs):
        viewlet = getMultiAdapter((milestone, self.request, self.view, self.manager), name='milestonetickets')
        viewlet.current_context = self.context
        viewlet.current_view = self.view
        viewlet.update()
        return self.render_item(milestone, 2) + viewlet.render()


class MilestoneTickets(Tickets):
    """ Renders a list of tickets associated with the milestone
    """
    grok.viewletmanager(ContentAfterManager)
    grok.view(IViewView)
    grok.context(interfaces.IMilestone)
    grok.order(30)
    caption = None
    interface = interfaces.ITicket
    css_class = None

    def query(self):
        return query.And(query.set.AnyOf(('catalog', 'implements'), [self.interface.__identifier__, ]),
                         query.Eq(('catalog', 'milestone'), self.context.id))
