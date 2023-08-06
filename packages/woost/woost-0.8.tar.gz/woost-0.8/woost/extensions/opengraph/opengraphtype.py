#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail import schema
from woost.models import Item


class OpenGraphType(Item):

    visible_from_root = False

    members_order = [
        "title",
        "code",
        "category"
    ]

    title = schema.String(
        required = True,
        unique = True,
        translated = True,
        descriptive = True
    )

    code = schema.String(
        required = True,
        unique = True,
        indexed = True
    )

    category = schema.Reference(
        type = "woost.extensions.opengraph"
                ".opengraphcategory.OpenGraphCategory",
        required = True,
        bidirectional = True
    )

