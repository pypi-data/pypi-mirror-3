#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail import schema
from woost.models import Publishable, Controller


class TextFile(Publishable):

    instantiable = True
    per_language_publication = False
    default_mime_type = "text/plain"
    default_hidden = True

    default_controller = schema.DynamicDefault(
        lambda: Controller.get_instance(
            qname = "woost.extensions.textfile.TextFileController"
        )
    )

    members_order = ["title", "content"]

    title = schema.String(
        translated = True,
        descriptive = True,
        listed_by_default = False,
        member_group = "content"
    )

    content = schema.String(
        edit_control = "cocktail.html.TextArea",
        listed_by_default = False,
        member_group = "content"
    )

