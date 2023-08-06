#-*- coding: utf-8 -*-
"""

@author:		Javier Marrero
@contact:		javier.marrero@whads.com
@organization:	Whads/Accent SL
@since:			January 2010
"""

import random
import string
from cocktail import schema
from cocktail.translations import translations
from woost.models import Extension

translations.define("SignUpExtension",
    ca = u"Alta d'usuaris",
    es = u"Alta de usuarios",
    en = u"Sign Up"
)

translations.define("SignUpExtension-plural",
    ca = u"Altas d'usuaris",
    es = u"Altas de usuarios",
    en = u"Signs Up"
)

class SignUpExtension(Extension):

    # To indicate if the extension was loaded at least one time
    # will be set to True at the end of the first load
    initialized = False

    def __init__(self, **values):
        Extension.__init__(self, **values)
        self.extension_author = u"Whads/Accent SL"
        self.set("description",
            u"""Permet als usuaris registrar-se autònomament en el lloc web""",
            "ca"
        )
        self.set("description",            
            u"""Permite a los usuarios registrarse por si mismos en el sitio""",
            "es"
        )
        self.set("description",
            u"""Allows users to register themselves on the site""",
            "en"
        )
        self.secret_key = self._generate_secret_key()

    def _generate_secret_key(self):
        secret_key = ''
        for i in range(0,8):
            secret_key = secret_key + \
                random.choice(
                    string.letters + string.digits
                )
        return secret_key

    def _load(self):
        
        from woost.models import User
        from woost.extensions.signup import (
            signuppage,
            signupcontroller,
            strings
        )

        # Extend User model
        if not hasattr(User, "confirmed_email"):
            User.add_member(
                schema.Boolean(
                    "confirmed_email",
                    default = False,
                    Required = True
                )
            )
        
        self.install()

    def _install(self):

        from woost.models import (
            extension_translations,
            User,
            Controller,
            Document,
            StandardPage,
            Template,
            EmailTemplate
        )
        from woost.extensions.signup.signuppage import SignUpPage

        signup_controller = self._create_asset(
            Controller,
            "signup_controller",
            python_name =
                "woost.extensions.signup.signupcontroller.SignUpController",
            title = extension_translations
        )
        
        signup_confirmation_controller = self._create_asset(
            Controller,
            "signup_confirmation_controller",
            python_name = 
                "woost.extensions.signup.signupconfirmationcontroller."
                "SignUpConfirmationController",
            title = extension_translations
        )

        signup_view = self._create_asset(
            Template,
            "signup_template",
            identifier = "woost.extensions.signup.SignUpView",
            engine = u"cocktail",
            title = extension_translations
        )

        signup_confirmation_view = self._create_asset(
            Template,
            "signup_confirmation_template",
            identifier = u"woost.extensions.signup.SignUpConfirmationView",
            engine = u"cocktail",
            title = extension_translations
        )

        confirmation_email_template = self._create_asset(
            EmailTemplate,
            "signup_confirmation_email_template",
            python_name =
                u"woost.extensions.signup.signupconfirmationemailtemplate."
                "SignUpConfirmationEmailTemplate",
            template_engine = u"mako",
            sender = User.require_instance(qname="woost.administrator").email,
            receivers = u"[user.email]",
            title = extension_translations,
            subject = extension_translations,
            body = extension_translations
        )

        confirmation_target = self._create_asset(
            StandardPage,
            "signup_confirmation_target",
            title = extension_translations,
            controller = signup_confirmation_controller,
            template = signup_confirmation_view,
            hidden = True
        )

        signup_page = self._create_asset(
            SignUpPage,
            "signup_page",
            title = extension_translations,
            user_type = User,
            confirmation_target = confirmation_target,
            parent = Document.get_instance(qname="woost.home"),
        )

        signup_page.children.append(confirmation_target)

