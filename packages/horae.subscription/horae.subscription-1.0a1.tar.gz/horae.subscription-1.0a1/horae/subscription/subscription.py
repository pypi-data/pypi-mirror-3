import grok
from persistent.dict import PersistentDict

from zope.interface import classImplements
from zope.annotation import IAnnotations

from horae.core.utils import findParentByInterface
from horae.ticketing import ticketing

from horae.subscription import interfaces

ANNOTATIONS_KEY = 'horae.subscription'

classImplements(ticketing.Client, interfaces.ISubscribeable)
classImplements(ticketing.Project, interfaces.ISubscribeable)
classImplements(ticketing.Ticket, interfaces.ISubscribeable)


class Subscription(grok.Adapter):
    """ Adapter handling subscription on an object
    """
    grok.context(interfaces.ISubscribeable)
    grok.implements(interfaces.ISubscription)

    def __init__(self, context):
        super(Subscription, self).__init__(context)
        annotations = IAnnotations(self.context)
        if not ANNOTATIONS_KEY in annotations:
            annotations[ANNOTATIONS_KEY] = PersistentDict()
        self.storage = annotations[ANNOTATIONS_KEY]

    def subscribe(self, subscriber):
        """ Subscribes the subscriber to the object
        """
        self.storage[subscriber.id] = subscriber

    def unsubscribe(self, id):
        """ Unsubscribes the subscriber
        """
        if not id in self.storage:
            return
        del self.storage[id]

    def subscribers(self):
        """ Returns the list of subscribers
        """
        return [subscriber for subscriber in self.storage.values() if subscriber.available(self.context)]

    def __getitem__(self, id):
        """ Returns the subscriber having the id specified
        """
        return self.storage.get(id, None)

    def __contains__(self, subscriber):
        """ Checks whether the provided subscriber is subscribed or not
        """
        return subscriber.id in self.storage

    def __iter__(self):
        """ Iterator over the contained subscribers
        """
        return self.subscribers()

    def notify(self, message):
        """ Sends the message to the registered subscribers
        """
        sent = 0
        failed = 0
        subscribers = []
        context = self
        while context is not None:
            subscribers.extend(interfaces.ISubscription(context).subscribers())
            context = findParentByInterface(context, interfaces.ISubscribeable, 1)
        if subscribers:
            msg, subject = message.message(), message.subject()
        if msg is None:
            return
        for subscriber in subscribers:
            try:
                if subscriber.notify(msg, subject):
                    sent += 1
                else:
                    failed += 1
            except:
                failed += 1
        return sent, failed
