#-*- coding: utf-8 -*-
"""Provides functions for dealing with user notifications.

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			February 2010
"""
from cocktail.controllers import session

def notify_user(message, category = None, transient = True):
    """Creates a new notification for the current user.
    
    Notifications are stored until a proper page is served to the user. It
    is up to the views to decide how these messages should be displayed.

    @param message: The message that will be shown to the user.
    @type message: unicode

    @param category: An optional free form string identifier that qualifies
        the message. Standard values include 'success' and 'error'.
    @type category: unicode

    @param transient: Indicates if the message should be hidden after a
        short lapse (True), or if it should remain visible until explicitly
        closed by the user (False).
    @type transient: bool
    """
    notifications = session.get("notifications")

    if notifications is None:
        session["notifications"] = notifications = []

    notifications.append((message, category, transient))

def pop_user_notifications(filter = None):
    """Retrieves pending notification messages that were stored through the
    L{notify_user} method.

    Retrieved messages are considered to be consumed, and therefore they
    are removed from the list of pending notifications.

    @param filter: If given, only those notifications matching the specified
        criteria will be retrieved. The criteria matches as follows:

            * If set to a string, it designates a single notification category
              to retrieve.
            * If set to a sequence (list, tuple, set), it designates a set of
              categories; notifications belonging to any of the specified
              categories will be retrieved.
            * If set to a callable, it will be used as filter function, taking
              a notification tuple as its single parameter, and returning True
              if the notification is to be retrieved, or False if it should be
              ignored.

    @return: The sequence of pending notification messages. Each message
        consists of a tuple with the message text, its category and wether
        or not it should be treated as a transient message.
    @rtype: sequence of (tuple of (unicode, unicode or None, bool))
    """
    notifications = session.get("notifications")

    if notifications is None:
        return []
    
    remaining = []

    if filter:
        matching = []

        if isinstance(filter, basestring):
            match = lambda notification: notification[1] == filter
        elif callable(filter):
            match = filter
        elif hasattr("__contains__", filter):
            match = lambda notification: notification[1] in filter
        else:
            raise TypeError(
                "The 'filter' parameter for the pop_user_notifications() "
                "function should be a string, a sequence or callable, got "
                "%s instead" % type(filter)
            )

        for notification in notifications:
            (matching if match(notification) else remaining).append(notification)

        notifications = matching    

    session["notifications"] = remaining
    return notifications

