#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Jordi Fernández <jordi.fernandez@whads.com>
"""
from cocktail import schema
from woost.models import Publishable
from woost.extensions.blocks.block import Block


class RichTextBlock(Block):

    instantiable = True
    view_class = "cocktail.html.Element"

    text = schema.String(
        required = True,
        edit_control = "woost.views.RichTextEditor",
        member_group = "content"
    )

    attachments = schema.Collection(
        items = schema.Reference(type = Publishable),
        related_end = schema.Collection(),
        member_group = "content"
    )

    def init_view(self, view):
        Block.init_view(self, view)        
        view.append(self.text)

