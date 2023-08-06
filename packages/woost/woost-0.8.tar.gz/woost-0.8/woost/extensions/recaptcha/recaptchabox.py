#-*- coding: utf-8 -*-
u"""

@author:		Jordi Fernández
@contact:		jordi.fernandez@whads.com
@organization:	Whads/Accent SL
@since:			December 2009
"""
from simplejson import dumps
from cocktail.translations import get_language
from cocktail.html import Element, templates
from woost.models import Template
from woost.extensions.recaptcha import ReCaptchaExtension


class ReCaptchaBox(Element):
    
    API_SSL_SERVER = "https://api-secure.recaptcha.net"
    API_SERVER = "http://api.recaptcha.net"
    
    tag = None

    def __init__(self, *args, **kwargs):
        Element.__init__(self, *args, **kwargs)
        self.recaptcha_params = {
            "public_key": ReCaptchaExtension.instance.public_key,
            "api_server": self.API_SSL_SERVER if ReCaptchaExtension.instance.ssl 
                          else self.API_SERVER,
            "error_param": "&amp;error=%s" % ("",)
        }
        self.recaptcha_options = {}

    def _ready(self):

        Element._ready(self)

        options = self.recaptcha_options.copy()

        language = get_language()
        
        options["lang"] = language
        if language == "ca":
            options["lang"] = "es"
            options["custom_translations"] = {
                "instructions_visual": "Escriu les 2 paraules:",
                "instructions_audio": "Escriu el que sentis:",
                "play_again": "Tornar a escoltar",
                "cant_hear_this": "Descarregar so en MP3",
                "visual_challenge": "Obtindre un repte visual",
                "audio_challenge": "Obtindre un repte audible",
                "refresh_btn": "Obtindre un nou repte",
                "help_btn": "Ajuda",
                "incorrect_try_again": "Incorrecte. Torna a provar-ho."
            }
        elif language not in ("en", "nl", "fr", "de", "pt", "ru", "es", "tr"):
            options["lang"] = "en"

        if ReCaptchaExtension.instance.theme == "custom":
            options.setdefault(
                    "custom_theme_widget",
                    ReCaptchaExtension.instance.custom_theme_widget
            )
            
        options.setdefault("theme", ReCaptchaExtension.instance.theme)

        init_options = Element("script")
        init_options["type"] = "text/javascript"
        init_options.append("var RecaptchaOptions = %s;" % dumps(options))

        init_script = Element()
        init_script.append("""<script type="text/javascript" src="%(api_server)s/challenge?k=%(public_key)s%(error_param)s"></script>

        <noscript>
          <iframe src="%(api_server)s/noscript?k=%(public_key)s%(error_param)s" style="height: 300px; width: 500px; border: 0;" ></iframe><br />
          <textarea name="recaptcha_challenge_field" rows="3" cols="40"></textarea>
          <input type='hidden' name='recaptcha_response_field' value='manual_challenge' />
        </noscript>
        """ % self.recaptcha_params)

        self.append(init_options)

        if ReCaptchaExtension.instance.theme == "custom":
            custom_container = templates.new(
                ReCaptchaExtension.instance.custom_template
            )
            custom_container.widgetid = ReCaptchaExtension.instance.custom_theme_widget
            self.append(custom_container.render())

        self.append(init_script)
    
