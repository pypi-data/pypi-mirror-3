#-*- coding: utf-8 -*-
"""

@author:		Jordi Fernández
@contact:		jordi.fernandez@whads.com
@organization:	Whads/Accent SL
@since:			March 2010
"""
from woost.models import (
    CreatePermission,
    ModifyPermission,
    DeletePermission
)
from woost.controllers.backoffice.useractions import UserAction
from woost.extensions.campaignmonitor.campaignmonitorlist import \
    CampaignMonitorList


class SynchronizeCampaignMonitorListAction(UserAction):

    ignores_selection = True
    min = None
    max = None
    included = frozenset(["toolbar"])
    content_type = CampaignMonitorList

    def is_permitted(self, user, target):
        # Must be able to create, update or delete lists (any of those
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

SynchronizeCampaignMonitorListAction("sync_campaign_monitor_lists").register()

