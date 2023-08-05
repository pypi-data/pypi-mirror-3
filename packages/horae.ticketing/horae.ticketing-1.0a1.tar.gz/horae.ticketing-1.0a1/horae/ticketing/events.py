from zope.component.interfaces import ObjectEvent
from zope.interface import implements

from horae.ticketing import interfaces


class TicketChangedEvent(ObjectEvent):
    """ A ticket has been changed
    """
    implements(interfaces.ITicketChangedEvent)

    def __init__(self, object, change, previous):
        super(TicketChangedEvent, self).__init__(object)
        self.change = change
        self.previous = previous
