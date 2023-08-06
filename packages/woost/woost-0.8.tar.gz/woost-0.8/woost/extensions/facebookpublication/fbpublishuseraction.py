#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from woost.models import Document, File, User
from woost.controllers.backoffice.useractions import UserAction
from woost.extensions.facebookpublication.facebookpublicationpermission \
    import FacebookPublicationPermission


class BaseFBPublishUserAction(UserAction):

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
        return user.has_permission(FacebookPublicationPermission, target = target)


class FBPublishUserAction(BaseFBPublishUserAction):
    content_type = Document

FBPublishUserAction("fbpublish").register()


class FBPublishAlbumsUserAction(BaseFBPublishUserAction):

    content_type = File

    def is_available(self, context, target):
        
        if not BaseFBPublishUserAction.is_available(self, context, target):
            return False

        return isinstance(target, type) or target.resource_type == "image"

FBPublishAlbumsUserAction("fbpublish_albums").register()

