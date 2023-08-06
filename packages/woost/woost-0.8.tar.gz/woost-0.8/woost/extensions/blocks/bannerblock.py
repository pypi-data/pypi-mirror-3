#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Jordi Fernández <jordi.fernandez@whads.com>
"""
from cocktail import schema
from woost.models import File, Publishable
from woost.models.rendering import ImageFactoryMember
from woost.extensions.blocks.block import Block


class BannerBlock(Block):

    instantiable = True
    tag = "a"
    view_class = "woost.extensions.blocks.Banner"

    members_order = [
        "target",
        "image",
        "image_factory",
        "text",
        "label_displayed"
    ]

    image = schema.Reference(
        type = File,
        integral = True,
        related_end = schema.Collection(),
        member_group = "content"
    )

    image_factory = ImageFactoryMember(
        member_group = "content"
    )

    target = schema.Reference(
        type = Publishable,
        required = True,
        related_end = schema.Collection(cascade_delete = True),
        member_group = "content"
    )

    text = schema.String(
        translated = True,
        member_group = "content"
    )

    label_displayed = schema.Boolean(
        default = False,
        required = True,
        member_group = "content"
    )

    def init_view(self, view):
        Block.init_view(self, view)
        view.image = self.image
        view.image_factory = self.image_factory
        view.target = self.target
        view.text = self.text
        view.label_displayed = self.label_displayed

