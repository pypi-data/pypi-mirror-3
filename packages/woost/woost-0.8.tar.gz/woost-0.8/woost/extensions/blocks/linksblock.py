#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail import schema
from woost.models import Publishable
from woost.extensions.blocks.block import Block


class LinksBlock(Block):

    instantiable = True
    view_class = "woost.extensions.blocks.LinksBox"

    links = schema.Collection(
        items = schema.Reference(type = Publishable),
        related_end = schema.Collection(),
        member_group = "content"
    )

    def init_view(self, view):
        Block.init_view(self, view)
        view.links = self.links

