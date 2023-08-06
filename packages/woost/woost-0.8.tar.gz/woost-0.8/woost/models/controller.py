#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			January 2010
"""
from cocktail import schema
from woost.models.item import Item


class Controller(Item):

    members_order = [
        "title",
        "python_name",
        "published_items"
    ]

    title = schema.String(
        unique = True,
        required = True,
        descriptive = True,
        translated = True
    )

    python_name = schema.String(
        required = True,
        text_search = False
    )

    published_items = schema.Collection(
        items = "woost.models.Publishable",
        bidirectional = True,
        editable = False
    )

