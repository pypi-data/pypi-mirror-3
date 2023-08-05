import grok

from zope.component import queryAdapter
from zope.security import checkPermission

from horae.layout import layout
from horae.layout import viewlets

from horae.subscription import interfaces

grok.templatedir('viewlet_templates')
grok.context(interfaces.ISubscribeable)


class Subscribers(layout.Viewlet):
    """ Renders the available subscribers and provides buttons
        to subscribe or unsubscribe
    """
    grok.viewletmanager(viewlets.SidebarManager)
    grok.order(10)

    def update(self):
        subscription = interfaces.ISubscription(self.context)
        subscriber = queryAdapter(self.request, interfaces.ISubscriber)
        self.allowed = subscriber and checkPermission('horae.Subscribe', self.context)
        if subscriber and self.allowed and self.request.get('subscribe', None) is not None:
            subscription.subscribe(subscriber)
            subscriber.context = self.context
        self.subscribed = subscriber and subscriber in subscription
        if subscriber and self.subscribed and self.request.get('unsubscribe', None) is not None:
            subscription.unsubscribe(subscriber.id)
            self.subscribed = False
        self.subscribers = subscription.subscribers()
        self.available = self.allowed or self.subscribers
