#-*- coding: utf-8 -*-
"""

@author:		Jordi Fernández
@contact:		jordi.fernandez@whads.com
@organization:	Whads/Accent SL
@since:			September 2010
"""
from woost.models import Document, CreatePermission
from woost.controllers.backoffice.useractions import UserAction
from woost.extensions.mailer.mailing import Mailing


class CreateMailingAction(UserAction):

    content_type = Document

    def is_permitted(self, user, target):
        return (
            target.is_inserted
            and user.has_permission(CreatePermission, target = Mailing)
        )

    def get_url(self, controller, selection):
        return controller.contextual_uri(
            'content', 'new', 
            item_type = Mailing.full_name,
            edited_item_document = selection[0].id
        )


CreateMailingAction("create_mailing").register()

