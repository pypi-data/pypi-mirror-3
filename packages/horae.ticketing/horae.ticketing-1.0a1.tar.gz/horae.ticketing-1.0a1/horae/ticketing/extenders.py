import grok

from zope import component
from zope.i18n import translate
from zope.location.interfaces import ILocationInfo

from hurry import query

from horae.properties.interfaces import IPropertiedDisplayWidgetsProvider
from horae.properties import views
from horae.properties import properties

from horae.ticketing.interfaces import IClient, IProject, IMilestone, ITicket
from horae.ticketing import _

try:
    from hurry.workflow.interfaces import IWorkflowState
    from horae.workflow.utils import stateName
    WORKFLOW = True
except:
    WORKFLOW = False


class NumberOfTicketsWidgetProvider(grok.Adapter):
    """ Base implementation of a widget provider rendering the
        number of tickets and their workflow state
    """
    grok.baseclass()
    grok.implements(IPropertiedDisplayWidgetsProvider)

    def query(self):
        return query.And(query.set.AnyOf(('catalog', 'implements'), [ITicket.__identifier__, ]),
                         query.set.AnyOf(('catalog', 'path'), [ILocationInfo(self.context).getPath(), ]))

    def widgets(self, widgets, request):
        tickets = component.getUtility(query.interfaces.IQuery).searchResults(self.query())
        if not len(tickets):
            return widgets
        value = str(len(tickets))
        property = properties.TextLineProperty()
        property.id = 'number_of_tickets'
        property.name = _(u'Number of tickets')
        if WORKFLOW:
            states = {}
            for ticket in tickets:
                info = IWorkflowState(ticket)
                state = info.getState()
                if state in states:
                    states[state]['no'] += 1
                else:
                    states[state] = {'no': 1, 'name': stateName(ticket, state)}
            value = '%s <small>(%s)</small>' % (value, ', '.join(['%s: %s' % (translate(state['name'], context=request), state['no']) for state in states.values()]))
        widgets.insert(0, views.PropertyDisplayWidget(property, value, self.context, request))
        return widgets


class ClientNumberOfTicketsWidgetProvider(NumberOfTicketsWidgetProvider):
    """ Widget provider rendering the number of tickets for clients
    """
    grok.name('horae.ticketing.client.tickets')
    grok.context(IClient)


class ProjectNumberOfTicketsWidgetProvider(NumberOfTicketsWidgetProvider):
    """ Widget provider rendering the number of tickets for projects
    """
    grok.name('horae.ticketing.project.tickets')
    grok.context(IProject)


class MilestoneNumberOfTicketsWidgetProvider(NumberOfTicketsWidgetProvider):
    """ Widget provider rendering the number of tickets for milestones
    """
    grok.name('horae.ticketing.milestone.tickets')
    grok.context(IMilestone)

    def query(self):
        return query.And(query.set.AnyOf(('catalog', 'implements'), [ITicket.__identifier__, ]),
                         query.set.AnyOf(('catalog', 'path'), [ILocationInfo(self.context).getPath(), ]),
                         query.Eq(('catalog', 'milestone'), self.context.id))
