#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from cocktail.modeling import classgetter
from cocktail.translations import translations, require_language
from cocktail import schema
from woost.models.item import Item


class Language(Item):
 
    members_order = ["iso_code", "fallback"]

    iso_code = schema.String(
        required = True,
        unique = True,
        max = 64,
        text_search = False
    )
    
    fallback = schema.Reference(
        type = "woost.models.Language",
        bidirectional = True,
        cycles_allowed = False
    )

    fallback_referrers = schema.Collection(
        items = "woost.models.Language",
        bidirectional = True,
        visible = False
    )

    @classgetter
    def codes(cls):
        return [language.iso_code for language in cls.select()]

    def __translate__(self, language, **kwargs):
        return (self.draft_source is None and translations(self.iso_code)) \
            or Item.__translate__(self, language, **kwargs)


def get_common_language(self, members, language = None):    

    language = require_language(language)

    if not all(self.get(m, language) for m in members):
        lang = Language.get_instance(iso_code = language)
        if lang is None:
            return lang
        if lang.fallback:
            fallback = lang.fallback.iso_code
            if all(self.get(m, fallback) for m in members):
                language = fallback

    return language

Item.get_common_language = get_common_language
del get_common_language

