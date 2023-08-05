import zope.event

from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from Products.statusmessages.interfaces import IStatusMessage

from collective.topicitemsevent.event import TopicItemEvent

class FireEventsView(BrowserView):
    """For each item in the Topic, fire an event. Redirect to Topic's view
    afterward. Set status message so we can see in the browser which items
    events were fired for.
    """

    def __call__(self, *args, **kwargs):
        brains = self.context.queryCatalog()

        # Status message
        status_txt = 'Firing TopicItemEvent for: '
        status_txt += ', '.join(
                        ["%s (%s)" % (b.Title, b.getURL()) for b in brains])
        messages = IStatusMessage(self.request)
        messages.addStatusMessage(status_txt, type="info")

        # Fire events
        for brain in brains:
            obj = brain.getObject()
            event = TopicItemEvent(obj)
            zope.event.notify(event)

        # Redirect to Topic view.
        return self.request.RESPONSE.redirect(self.context.absolute_url())
