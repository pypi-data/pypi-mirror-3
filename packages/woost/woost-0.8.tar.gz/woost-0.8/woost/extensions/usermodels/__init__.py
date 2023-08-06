#-*- coding: utf-8 -*-
u"""Defines an extension that allows end users to define their own data models.

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import cherrypy
from cocktail.translations import translations
from woost.models import Extension

translations.define("UserModelsExtension",
    ca = u"Models d'usuari",
    es = u"Modelos de usuario",
    en = u"User models"
)

translations.define("CountriesExtension-plural",
    ca = u"Models d'usuari",
    es = u"Modelos de usuario",
    en = u"User models"
)

models_access = None


class UserModelsExtension(Extension):

    def __init__(self, **values):
        Extension.__init__(self, **values)
        self.extension_author = u"Whads/Accent SL"
        self.set("description",
            u"""Permet als usuaris del gestor definir els seus propis models de
            dades.""",
            "ca"
        )
        self.set("description",
            u"""Permite a los usuarios del gestor definir sus propios modelos
            de datos.""",
            "es"
        )
        self.set("description",
            u"""Makes it possible to create custom data types from the
            backoffice.""",
            "en"
        )

    def _load(self):
        
        global models_access

        from woost.extensions.usermodels import strings, usermembers, userform
        from woost.extensions.usermodels.door import Door

        # Create extension objects the first time it is run
        self.install()

        # Make all existing user models available to the application
        for user_model in usermembers.UserModel.select():
            user_model.produce_member()

        # Serialize access to models
        models_access = Door()
        
        cherrypy.request.hooks.attach(
            "on_start_resource",
            models_access.enter,
            failsafe = True
        )
        
        cherrypy.request.hooks.attach(
            "on_end_request", 
            models_access.leave,
            failsafe = True
        )

    def _install(self):
        
        from woost.models import Controller, Template, extension_translations
        
        self._create_asset(
            Controller,
            "user_form_controller",
            python_name = "woost.extensions.usermodels.userform."
                          "UserFormController",
            title = extension_translations
        )

        self._create_asset(
            Template,
            "user_form_template",
            identifier = "woost.extensions.usermodels.UserFormView",
            title = extension_translations
        )

