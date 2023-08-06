#-*- coding: utf-8 -*-
"""

@author:		Jordi Fernández
@contact:		jordi.fernandez@whads.com
@organization:	Whads/Accent SL
@since:			September 2010
"""
from woost.controllers.backoffice.useractions import UserAction
from woost.extensions.mailer.mailing import Mailing, MAILING_FINISHED
from woost.extensions.mailer.sendemailpermission import \
    SendEmailPermission


class SendEmailAction(UserAction):
    included = frozenset(["item_buttons"])
    content_type = Mailing

    def is_permitted(self, user, target):
        return target.is_inserted \
        and not target.status == MAILING_FINISHED \
        and user.has_permission(SendEmailPermission)

SendEmailAction("send_email").register()

