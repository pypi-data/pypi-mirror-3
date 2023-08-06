#-*- coding: utf-8 -*-
u"""Declares a user action for tweeting publishable items.

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from woost.models import Publishable
from woost.controllers.backoffice.useractions import UserAction
from woost.extensions.twitterpublication.tweetpermission import TweetPermission


class TweetUserAction(UserAction):
 
    content_type = Publishable

    included = frozenset([
        ("content", "toolbar_extra"),
        ("collection", "toolbar_extra", "integral"),
        "item_buttons_extra"
    ])

    excluded = frozenset([
        "selector",
        "new_item",
        "calendar_content_view",
        "workflow_graph_content_view",
        "changelog"
    ])

    max = None
    
    def is_permitted(self, user, target):
        return user.has_permission(TweetPermission, target = target)


TweetUserAction("tweet").register()

