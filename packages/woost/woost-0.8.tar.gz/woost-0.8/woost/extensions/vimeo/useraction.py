#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			February 2010
"""
from woost.models import (
    CreatePermission,
    ModifyPermission,
    DeletePermission
)
from woost.controllers.backoffice.useractions import UserAction
from woost.extensions.vimeo.video import VimeoVideo


class SynchronizeVimeoAction(UserAction):

    ignores_selection = True
    min = None
    max = None
    included = frozenset(["toolbar"])
    excluded = frozenset(["collection"])
    content_type = VimeoVideo

    def is_permitted(self, user, target):

        # Must be able to create, update or delete videos (any of those
        # permissions will enable the button; the controller will later
        # limit which actions are actually allowed)
        return any(
            user.has_permission(permission_type, target = target)
            for permission_type in (
                CreatePermission,
                ModifyPermission,
                DeletePermission
            )
        )

SynchronizeVimeoAction("sync_vimeo").register()

