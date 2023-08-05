from plone.memoize import ram

from horae.ticketing import _
from horae.ticketing import interfaces


@ram.cache(lambda method, *args, **kwargs: (method.__module__, method.__name__, args[0]))
def getObjectType(obj):
    """ Returns the user readable object type for the given object
    """
    if obj is interfaces.IClient or interfaces.IClient.providedBy(obj):
        return _(u'Client')
    if obj is interfaces.IProject or interfaces.IProject.providedBy(obj):
        return _(u'Project')
    if obj is interfaces.IMilestone or interfaces.IMilestone.providedBy(obj):
        return _(u'Milestone')
    if obj is interfaces.ITicket or interfaces.ITicket.providedBy(obj):
        return _(u'Ticket')
    return None
