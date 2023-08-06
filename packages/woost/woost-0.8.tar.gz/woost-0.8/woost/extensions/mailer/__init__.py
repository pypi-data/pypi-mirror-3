#-*- coding: utf-8 -*-
"""

@author:		Jordi Fernández
@contact:		jordi.fernandez@whads.com
@organization:	Whads/Accent SL
@since:			September 2010
"""
import cherrypy
from cocktail.events import when
from cocktail import schema
from cocktail.translations import translations
from cocktail.controllers import context
from woost.models import Extension, Document, Template, Role
from woost.models.permission import DeletePermission, ModifyPermission


translations.define("MailerExtension",
    ca = u"Enviament de documents per correu electrònic",
    es = u"Envio de documentos por correo electrónico",
    en = u"Sending documents by email"
)

translations.define("MailerExtension-plural",
    ca = u"Enviament de documents per correu electrònic",
    es = u"Envio de documentos por correo electrónico",
    en = u"Sending documents by email"
)


class MailerExtension(Extension):

    def __init__(self, **values):
        Extension.__init__(self, **values)
        self.extension_author = u"Whads/Accent SL"
        self.set("description",
            u"""Permet enviar documents per correu electrònic.""",
            "ca"
        )
        self.set("description",            
            u"""Permite enviar documents por correo electrónico.""",
            "es"
        )
        self.set("description",
            u"""Allows send documents by email.""",
            "en"
        )

    def _load(self):

        from woost.controllers.notifications import notify_user
        from woost.controllers.backoffice.basebackofficecontroller import \
            BaseBackOfficeController
        from woost.controllers.backoffice.itemcontroller import \
            ItemController

        from woost.extensions.mailer import (
            sendemailaction,
            createmailingaction,
            strings
        )
        from woost.extensions.mailer.mailing import Mailing, \
            RunningMailingError
        from woost.extensions.mailer.sendemailcontroller import \
            SendEmailController

        ItemController.send_email = SendEmailController

        Template.add_member(
            schema.Boolean(
                "per_user_customizable",
                default = False,
                listed_by_default = False
            )
        )
        Template.members_order.append("per_user_customizable")

        @when(BaseBackOfficeController.exception_raised)
        def handle_exception_raised(event):                                                                                                                                                                   
            if isinstance(
                event.exception,
                RunningMailingError
            ):  
                notify_user(translations(event.exception), "error")
                raise cherrypy.HTTPRedirect(event.source.contextual_uri())
    
        # Disable interactive features from rendered pages when rendering
        # static content
        from woost.controllers.cmscontroller import CMSController
    
        @when(CMSController.producing_output)
        def disable_user_controls(event):
            if context.get("sending_email", False):
                event.output["show_user_controls"] = False

