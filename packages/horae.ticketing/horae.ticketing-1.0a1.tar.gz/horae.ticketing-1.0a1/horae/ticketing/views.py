import grok
from datetime import datetime

from zope import component
from zope import schema
from zope.security import checkPermission
from zope.event import notify
from megrok import navigation

from horae.properties.interfaces import IClientPropertiesHolder, IClientProperties, \
    IProjectPropertiesHolder, IProjectProperties, \
    IMilestonePropertiesHolder, IMilestoneProperties, \
    ITicketPropertiesHolder, ITicketProperties, IComplete, IOffer
from horae.properties import views
from horae.timeaware.interfaces import ITimeEntryFactory
from horae.layout.interfaces import IAddMenu, IActionsMenu, IViewsMenu, IViewView, IDisplayView, IMainActionsMenu

from horae.ticketing.events import TicketChangedEvent
from horae.ticketing import _
from horae.ticketing import interfaces
from horae.ticketing import ticketing

grok.templatedir('templates')


class AddClient(views.PropertiedAddForm):
    """ Add form for clients
    """
    grok.context(interfaces.IClientContainerHolder)
    grok.name('add-client')
    grok.require('horae.AddClient')
    navigation.menuitem(IAddMenu, _(u'Client'))
    navigation.menuitem(IMainActionsMenu, _(u'Add client'))

    form_fields = grok.AutoFields(interfaces.IClient).omit('id')

    container_interface = interfaces.IClientContainer
    factory = ticketing.Client
    interfaces = (IClientPropertiesHolder, IClientProperties)

    def object_type(self):
        return _(u'Client')


class EditClient(views.PropertiedEditForm):
    """ Edit form of a client
    """
    grok.context(interfaces.IClient)
    grok.name('edit')
    grok.require('horae.Edit')
    navigation.menuitem(IActionsMenu, _(u'Edit'))

    form_fields = grok.AutoFields(interfaces.IClient).omit('id')

    interfaces = (IClientPropertiesHolder, IClientProperties)

    def object_type(self):
        return _(u'Client')


class ViewClient(views.PropertiedDisplayForm):
    """ View of a client
    """
    grok.context(interfaces.IClient)
    grok.implements(IViewView)
    grok.name('index')
    grok.require('horae.View')
    navigation.menuitem(IViewsMenu, _(u'Default view'))

    form_fields = grok.AutoFields(interfaces.IClient).omit('id')

    interfaces = (IClientPropertiesHolder, IClientProperties)


class HistoryClient(views.History):
    """ History of a client
    """
    grok.context(interfaces.IClient)
    interfaces = (IClientPropertiesHolder, IClientProperties)


class AddProject(views.PropertiedAddForm):
    """ Add form for projects
    """
    grok.context(interfaces.IProjectContainerHolder)
    grok.name('add-project')
    grok.require('horae.AddProject')
    navigation.menuitem(IAddMenu, _(u'Project'))
    navigation.menuitem(IMainActionsMenu, _(u'Add project'))

    form_fields = grok.AutoFields(interfaces.IProject).omit('id')

    container_interface = interfaces.IProjectContainer
    factory = ticketing.Project
    interfaces = (IProjectPropertiesHolder, IProjectProperties)

    def object_type(self):
        return _(u'Project')


class EditProject(views.PropertiedEditForm):
    """ Edit form of a project
    """
    grok.context(interfaces.IProject)
    grok.name('edit')
    grok.require('horae.Edit')
    navigation.menuitem(IActionsMenu, _(u'Edit'))

    form_fields = grok.AutoFields(interfaces.IProject).omit('id')

    interfaces = (IProjectPropertiesHolder, IProjectProperties)

    def object_type(self):
        return _(u'Project')


class ViewProject(views.PropertiedDisplayForm):
    """ View of a project
    """
    grok.context(interfaces.IProject)
    grok.implements(IViewView)
    grok.name('index')
    grok.require('horae.View')
    navigation.menuitem(IViewsMenu, _(u'Default view'))

    form_fields = grok.AutoFields(interfaces.IProject).omit('id')

    interfaces = (IProjectPropertiesHolder, IProjectProperties)


class HistoryProject(views.History):
    """ History of a project
    """
    grok.context(interfaces.IProject)
    interfaces = (IProjectPropertiesHolder, IProjectProperties)


class AddMilestone(views.PropertiedAddForm):
    """ Add form for milestones
    """
    grok.context(interfaces.IMilestoneContainerHolder)
    grok.name('add-milestone')
    grok.require('horae.AddMilestone')
    navigation.menuitem(IAddMenu, _(u'Milestone'))
    navigation.menuitem(IMainActionsMenu, _(u'Add milestone'))

    form_fields = grok.AutoFields(interfaces.IMilestone).omit('id')

    container_interface = interfaces.IMilestoneContainer
    factory = ticketing.Milestone
    interfaces = (IMilestonePropertiesHolder, IMilestoneProperties)

    def object_type(self):
        return _(u'Milestone')


class EditMilestone(views.PropertiedEditForm):
    """ Edit form of a milestone
    """
    grok.context(interfaces.IMilestone)
    grok.name('edit')
    grok.require('horae.Edit')
    navigation.menuitem(IActionsMenu, _(u'Edit'))

    label = _(u'Edit milestone')
    form_fields = grok.AutoFields(interfaces.IMilestone).omit('id')

    interfaces = (IMilestonePropertiesHolder, IMilestoneProperties)


class ViewMilestone(views.PropertiedDisplayForm):
    """ View of a milestone
    """
    grok.context(interfaces.IMilestone)
    grok.implements(IViewView)
    grok.require('horae.View')
    grok.name('index')
    navigation.menuitem(IViewsMenu, _(u'Default view'))

    form_fields = grok.AutoFields(interfaces.IMilestone).omit('id')

    interfaces = (IMilestonePropertiesHolder, IMilestoneProperties)


class HistoryMilestone(views.History):
    """ History of a milestone
    """
    grok.context(interfaces.IMilestone)
    interfaces = (IMilestonePropertiesHolder, IMilestoneProperties)


class AddTicket(views.PropertiedAddForm):
    """ Add form for tickets
    """
    grok.context(interfaces.ITicketContainerHolder)
    grok.name('add-ticket')
    grok.require('horae.AddTicket')
    navigation.menuitem(IAddMenu, _(u'Ticket'))
    navigation.menuitem(IMainActionsMenu, _(u'Add ticket'))

    form_fields = grok.AutoFields(interfaces.ITicket).omit('id')

    container_interface = interfaces.ITicketContainer
    factory = ticketing.Ticket
    interfaces = (ITicketPropertiesHolder, ITicketProperties)

    def object_type(self):
        return _(u'Ticket')

    def update_properties(self, context=None):
        milestone = ITicketProperties(self.context).get_property('milestone').default
        if milestone is not None:
            super(AddTicket, self).update_properties(milestone)
        else:
            super(AddTicket, self).update_properties()

    def apply(self, obj, **data):
        super(AddTicket, self).apply(obj, **data)
        notify(TicketChangedEvent(self.context, interfaces.IPropertied(self.context).current(), {}))


class AddMilestoneTicket(AddTicket):
    """ Add form for tickets created on a milestone
    """
    grok.context(interfaces.IMilestone)
    grok.name('add-ticket')
    grok.require('horae.AddTicket')
    navigation.menuitem(IAddMenu, _(u'Ticket'))

    def update(self):
        super(AddMilestoneTicket, self).update()
        self.form_fields['milestone'].field = self.form_fields['milestone'].field.bind(self.context)

    def setUpWidgets(self, ignore_request=False):
        super(AddMilestoneTicket, self).setUpWidgets(ignore_request)
        if not self.widgets['milestone'].hasInput():
            self.widgets['milestone'].setRenderedValue(self.context)


class TicketViewMixin(object):
    """ Mix in class for ticket views
    """

    def _collect_previous(self):
        previous = {}
        for change in interfaces.IPropertied(self.context).changelog():
            previous.update(dict(change.properties()))
        return previous

    def update_properties(self):
        super(TicketViewMixin, self).update_properties(self.context.milestone)

    def object_type(self):
        return _(u'Ticket')


class EditTicket(TicketViewMixin, views.PropertiedEditForm):
    """ Edit form of a ticket
    """
    grok.context(interfaces.ITicket)
    grok.name('edit')
    grok.require('horae.Edit')
    navigation.menuitem(IActionsMenu, _(u'Edit'))

    form_fields = grok.AutoFields(interfaces.ITicket).omit('id')

    interfaces = (ITicketPropertiesHolder, ITicketProperties)
    initial = True
    editable = False
    id = 'ticket-change'

    def apply(self, **data):
        previous = self._collect_previous()
        super(EditTicket, self).apply(**data)
        notify(TicketChangedEvent(self.context, interfaces.IPropertied(self.context).current(), previous))


class ViewTicket(TicketViewMixin, views.PropertiedDisplayForm):
    """ View of a ticket
    """
    grok.context(interfaces.ITicket)
    grok.implements(IViewView)
    grok.name('index')
    grok.require('horae.View')
    grok.template('ticket')
    navigation.menuitem(IViewsMenu, _(u'Default view'))

    form_fields = grok.AutoFields(interfaces.ITicket).omit('id')
    interfaces = (ITicketPropertiesHolder, ITicketProperties)

    def __call__(self, plain=False, form=True, history=True, change=None, previous=None):
        self.form = u''
        self.plain = plain
        if form and checkPermission('horae.ChangeTicket', self.context):
            self.form = component.getMultiAdapter((self.context, self.request), name=u'change')(plain=True)
        self.history = u''
        if history and checkPermission('horae.ViewHistory', self.context):
            self.history = component.getMultiAdapter((self.context, self.request), name=u'history')(plain=True, change=change, previous=previous)
        return super(ViewTicket, self).__call__(plain)


class HistoryTicket(TicketViewMixin, views.History):
    """ History of a ticket
    """
    grok.context(interfaces.ITicket)
    interfaces = (ITicketPropertiesHolder, ITicketProperties)


class ChangeTicket(TicketViewMixin, views.PropertiedEditForm):
    """ Change form of a ticket
    """
    grok.context(interfaces.ITicket)
    grok.name('change')
    grok.require('horae.ChangeTicket')
    grok.implements(IDisplayView)

    form_fields = grok.AutoFields(interfaces.ITicket).omit('id')

    interfaces = (ITicketPropertiesHolder, ITicketProperties)

    def update(self):
        completed = IComplete(self.context, lambda: False)()
        offer = IOffer(self.context, lambda: False)()
        if not completed and not offer:
            self.form_fields = self.form_fields + \
                               grok.Fields(date_hours=schema.Float(
                                   title=_(u'Hours'),
                                   required=False,
                                   default=0.0
                               )) + \
                               grok.AutoFields(ITimeEntryFactory).omit('repeat', 'repeat_until')
            self.form_fields['date_hours'].field.order = 120
            self.form_fields['date_start'].field.order = 121
            self.form_fields['date_end'].field.order = 122
        super(ChangeTicket, self).update()

    def setUpWidgets(self, ignore_request=False):
        super(ChangeTicket, self).setUpWidgets(ignore_request)
        if self.widgets.get('tags') is not None:
            self.widgets['tags'].form_url = self.url(self.context) + '/@@change'
        if self.widgets.get('date_start') is not None and not self.widgets['date_start'].hasInput():
            self.widgets['date_start'].setRenderedValue(datetime.now())
        if self.widgets.get('date_end') is not None and not self.widgets['date_end'].hasInput():
            self.widgets['date_end'].setRenderedValue(datetime.now())

    def apply(self, **data):
        previous = self._collect_previous()
        if 'date_hours' in data:
            del data['date_hours']
        super(ChangeTicket, self).apply(**data)
        ITimeEntryFactory(self.context).create()
        notify(TicketChangedEvent(self.context, interfaces.IPropertied(self.context).current(), previous))
