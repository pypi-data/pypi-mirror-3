#-*- coding: utf-8 -*-
"""

@author:		Jordi Fernández Camps
@contact:		jordi.fernandez@whads.com
@organization:	Whads/Accent SL
@since:			December 2009
"""
from cocktail.persistence import datastore
from cocktail.translations import translations
from cocktail import schema
from cocktail.html import templates
from woost.models import Extension, Template

translations.define("ReCaptchaExtension",
    ca = u"ReCaptcha",
    es = u"ReCaptcha",
    en = u"ReCaptcha"
)

translations.define("ReCaptchaExtension-plural",
    ca = u"ReCaptcha",
    es = u"ReCaptcha",
    en = u"ReCaptcha"
)

translations.define("ReCaptchaExtension.public_key",
    ca = u"Clau pública",
    es = u"Clave pública",
    en = u"Public key"
)

translations.define("ReCaptchaExtension.private_key",
    ca = u"Clau privada",
    es = u"Clave privada",
    en = u"Private key"
)

translations.define("ReCaptchaExtension.theme",
    ca = u"Tema",
    es = u"Tema",
    en = u"Theme"
)

translations.define("ReCaptchaExtension.ssl",
    ca = u"SSL",
    es = u"SSL",
    en = u"SSL"
)

translations.define("ReCaptchaExtension.custom_theme_widget",
    ca = u"Id de l'element DOM (només pel tema custom)",
    es = u"Id del elemento DOM (sólo para el tema custom)",
    en = u"DOM element Id (only for custom theme)"
)

translations.define("ReCaptchaExtension.custom_template",
    ca = u"Plantilla",
    es = u"Plantilla",
    en = u"Template"
)

translations.define("ReCaptchaExtension.custom_group",
    ca = u"Tema personalitzat",
    es = u"Tema personalizado",
    en = u"Custom Theme"
)


class ReCaptchaExtension(Extension):

    def __init__(self, **values):
        Extension.__init__(self, **values)
        self.extension_author = u"Whads/Accent SL"
        self.set("description",
            u"""Afegeix suport pel servei anti-bots reCAPTCHA.""",
            "ca"
        )
        self.set("description",            
            u"""Añade soporte para el servicio anti-bots reCAPTCA.""",
            "es"
        )
        self.set("description",
            u"""Adds support for anti-bot reCAPTCHA service.""",
            "en"
        )

    def _load(self):

        # Import the extension's models
        from woost.extensions.recaptcha import (
            strings,
            schemarecaptchas
        )

        # Append additional members to the extension
        ReCaptchaExtension.members_order = [
            "public_key",
            "private_key",
            "theme",
            "custom_theme_widget",
            "custom_template",
            "ssl"
        ]

        ReCaptchaExtension.add_member(
            schema.String(
                "public_key",
                required = True,
                text_search = False
            )   
        )

        ReCaptchaExtension.add_member(
            schema.String(
                "private_key",
                required = True,
                text_search = False
            )   
        )

        ReCaptchaExtension.add_member(
            schema.String(
                "theme",
                required = True,
                enumeration = (
                    "red", "white", "blackglass", "clean", "custom"
                ),
                default = "red",
                text_search = False
            )   
        )

        ReCaptchaExtension.add_member(
            schema.String(
                "custom_theme_widget",
                exclusive = ReCaptchaExtension.theme.equal("custom"),
                member_group = "custom_group",
                text_search = False
            )   
        )  

        ReCaptchaExtension.add_member(
            schema.String(
                "custom_template",
                exclusive = ReCaptchaExtension.theme.equal("custom"),
                member_group = "custom_group",
                default = "woost.extensions.recaptcha.RecaptchaCustomView",
                text_search = False
            )   
        )

        ReCaptchaExtension.add_member(
            schema.Boolean(
                "ssl",
                default = False
            )   
        )

