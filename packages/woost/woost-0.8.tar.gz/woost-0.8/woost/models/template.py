#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			June 2008
"""
import buffet
from cocktail import schema
from woost.models import Item

class Template(Item):

    members_order = [
        "title",
        "identifier",
        "engine",
        "documents"
    ]

    title = schema.String(
        required = True,
        unique = True,
        indexed = True,
        normalized_index = True,
        full_text_indexed = True,
        descriptive = True,
        translated = True
    )

    identifier = schema.String(
        required = True,
        unique = True,
        indexed = True,
        max = 255,
        text_search = False
    )

    engine = schema.String(
        enumeration = buffet.available_engines.keys(),
        text_search = False
    )

    documents = schema.Collection(
        items = "woost.models.Document",
        bidirectional = True,
        editable = False
    )

