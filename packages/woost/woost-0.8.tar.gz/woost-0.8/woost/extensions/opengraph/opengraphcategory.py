#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail import schema
from woost.models import Item


class OpenGraphCategory(Item):

    visible_from_root = False

    members_order = [
        "title",
        "code",
        "types"
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

    types = schema.Collection(
        items = "woost.extensions.opengraph.opengraphtype.OpenGraphType",
        bidirectional = True,
        cascade_delete = True
    )

