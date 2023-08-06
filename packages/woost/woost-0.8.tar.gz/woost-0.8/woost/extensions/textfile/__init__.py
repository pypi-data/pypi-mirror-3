#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.translations import translations
from woost.models import Extension

translations.define("TextFileExtension",
    ca = u"Fitxers de text",
    es = u"Ficheros de texto",
    en = u"Text files"
)


class TextFileExtension(Extension):

    def __init__(self, **values):
        Extension.__init__(self, **values)
        self.extension_author = u"Whads/Accent SL"
        self.set("description",
            u"Permet editar fitxers de text directament des del gestor.",
            "ca"
        )
        self.set("description",            
            u"Permite editar ficheros de texto directamente desde el gestor.",
            "es"
        )
        self.set("description",
            u"Makes it possible to edit text files from the backoffice.",
            "en"
        )
    
    def _load(self):
        from woost.extensions.textfile import textfile, strings
        self.install()

    def _install(self):

        from woost.models import Controller, extension_translations

        controller = self._create_asset(
            Controller,
            "controller",
            title = extension_translations,
            python_name = "woost.extensions.textfile.textfilecontroller."
                          "TextFileController"
        )

