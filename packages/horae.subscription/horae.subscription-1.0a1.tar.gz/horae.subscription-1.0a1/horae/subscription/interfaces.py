from zope import interface


class ISubscribeable(interface.Interface):
    """ Marker interface for subscribeable objects
    """


class ISubscriber(interface.Interface):
    """ A subscriber
    """

    id = interface.Attribute('id', 'The id of the subscriber')
    name = interface.Attribute('name', 'The name of the subscriber')
    url = interface.Attribute('url', 'The URL of the subscriber or None')

    def notify(message, subject):
        """ Sends the message to the subscriber
        """

    def available(context):
        """ Whether this subscriber is currently available or not
        """


class ISubscription(interface.Interface):
    """ Adapter handling subscription on an object
    """

    def subscribe(subscriber):
        """ Subscribes the subscriber to the object
        """

    def unsubscribe(id):
        """ Unsubscribes the subscriber
        """

    def subscribers():
        """ Returns the list of subscribers
        """

    def __getitem__(id):
        """ Returns the subscriber having the id specified
        """

    def __contains__(subscriber):
        """ Checks whether the provided subscriber is subscribed or not
        """

    def __iter__():
        """ Iterator over the contained subscribers
        """

    def notify(message):
        """ Sends the message to the registered subscribers and returns a
            tuple of two integers where the first is the number of successfully
            sent notifications and the second is the number of failed notifications
        """


class IMessage(interface.Interface):
    """ A message to be sent to subscribers
    """

    def subject():
        """ Returns the subject of the notification to be sent
        """

    def message(html=False):
        """ Returns the notification message to be sent
        """
