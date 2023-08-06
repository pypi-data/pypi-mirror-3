#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail import schema
from woost.extensions.blocks.block import Block
from woost.models.rendering import ImageFactoryMember


class FolderBlock(Block):

    instantiable = True
    view_class = "woost.extensions.blocks.FolderBlockView"

    members_order = [
        "show_hidden_children",
        "show_thumbnails",
        "thumbnails_factory"
    ]

    show_hidden_children = schema.Boolean(
        required = True,
        default = False,
        member_group = "content"
    )

    show_thumbnails = schema.Boolean(
        required = True,
        default = False,
        member_group = "content"
    )

    thumbnails_factory = ImageFactoryMember(
        exclusive = show_thumbnails,
        default = False,
        member_group = "content"
    )

    def init_view(self, view):
        Block.init_view(self, view)
        view.show_hidden_children = self.show_hidden_children
        view.show_thumbnails = self.show_thumbnails
        view.thumbnails_factory = self.thumbnails_factory

