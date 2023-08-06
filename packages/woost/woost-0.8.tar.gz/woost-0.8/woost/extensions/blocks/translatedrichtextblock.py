#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Jordi Fernández <jordi.fernandez@whads.com>
"""
from cocktail import schema
from cocktail.html import Element, templates
from woost.models import Publishable, File
from woost.models.rendering import ImageFactoryMember
from woost.extensions.blocks.block import Block


class TranslatedRichTextBlock(Block):

    instantiable = True
    view_class = "cocktail.html.Element"

    members_order = ["text", "image", "image_factory", "attachments"]

    text = schema.String(
        required = True,
        edit_control = "woost.views.RichTextEditor",
        translated = True,
        member_group = "content"
    )

    image = schema.Reference(
        type = File,
        related_end = schema.Collection(),
        relation_constraints = [File.resource_type.equal("image")],
        member_group = "content"
    )

    image_factory = ImageFactoryMember(
        member_group = "content"
    )

    attachments = schema.Collection(
        items = schema.Reference(type = Publishable),
        related_end = schema.Collection(),
        member_group = "content"
    )

    def init_view(self, view):

        Block.init_view(self, view)

        if self.image is None:
            view.append(self.text)
        else:
            view.add_class("text_with_image")

            image = templates.new("woost.views.Image")
            image.image = self.image
            image.image_factory = self.image_factory
            view.append(image)

            text_container = Element()
            text_container.append(self.text)
            view.append(text_container)

