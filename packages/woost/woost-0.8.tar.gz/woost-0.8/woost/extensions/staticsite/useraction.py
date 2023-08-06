#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			December 2009
"""
from woost.models import Publishable
from woost.controllers.backoffice.useractions import UserAction
from woost.extensions.staticsite.staticsitedestination import \
    StaticSiteDestination
from woost.extensions.staticsite.exportationpermission import \
    ExportationPermission


class ExportStaticAction(UserAction):
    min = None
    max = None
    included = frozenset(["toolbar"])
    content_type = Publishable

    def is_permitted(self, user, target):
        return any([
            user.has_permission(
                ExportationPermission, 
                destination = destination
            )
            for destination in StaticSiteDestination.select()
        ])

ExportStaticAction("export_static").register()

