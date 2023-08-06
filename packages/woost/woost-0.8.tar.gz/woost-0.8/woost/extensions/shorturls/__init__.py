#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.translations import translations
from cocktail import schema
from woost.models import Extension


translations.define("ShortURLsExtension",
    ca = u"URLs curtes",
    es = u"URLs cortas",
    en = u"Short URLs"
)

translations.define("ShortURLsPublicationExtension-plural",
    ca = u"URLs curtes",
    es = u"URLs cortas",
    en = u"Short URLs"
)


class ShortURLsExtension(Extension):

    def __init__(self, **values):
        Extension.__init__(self, **values)
        self.extension_author = u"Whads/Accent SL"
        self.set("description",
            u"""Integració amb serveis d'escurçat d'URLs""",
            "ca"
        )
        self.set("description",            
            u"""Integración con servicios de compactación de URLs""",
            "es"
        )
        self.set("description",
            u"""Integration with URL shortening services""",
            "en"
        )

    def _load(self):
        
        from woost.extensions.shorturls import (
            strings,
            urlshortener,
            bitlyurlshortener
        )

