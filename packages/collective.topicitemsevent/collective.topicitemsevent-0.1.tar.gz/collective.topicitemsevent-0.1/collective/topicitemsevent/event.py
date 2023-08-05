from zope.component.interfaces import ObjectEvent, IObjectEvent
from zope.interface import implements

class ITopicItemEvent(IObjectEvent):
    """A Topic where this item is listed has had its '@@fire-events'-view
    called."""

class TopicItemEvent(ObjectEvent):
    """
    """
    implements(ITopicItemEvent)

