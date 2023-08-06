#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Jordi Fernández <jordi.fernandez@whads.com>
"""
from cocktail.translations import translations
from cocktail import schema
from cocktail.modeling import getter
from cocktail.html import templates
from woost.models import File
from woost.models.rendering.factories import ImageFactoryMember
from woost.extensions.blocks.block import Block


class ImageGalleryBlock(Block):

    instantiable = True
    view_class = "woost.views.ImageGallery"

    members_order = [
        "images",
        "gallery_type",
        "thumbnail_factory",
        "close_up_factory",
        "close_up_preload",
        "auto_play"
    ]

    images = schema.Collection(
        items = schema.Reference(type = File),
        relation_constraints = [File.resource_type.equal("image")],
        related_end = schema.Collection(),
        member_group = "content"
    )

    gallery_type = schema.String(
        required = True,
        default = "thumbnails",
        enumeration = ["thumbnails", "slideshow"],
        edit_control = "cocktail.html.RadioSelector",
        translate_value = lambda value, language = None, **kwargs:
            "" if not value 
               else translations(
                   "ImageGalleryBlock.gallery_type-%s" % value,
                   language,
                   **kwargs
               ),
        member_group = "content"
    )

    thumbnail_factory = ImageFactoryMember(
        required = True,
        default = "image_gallery_thumbnail",
        enumeration = lambda ctx:
            templates.get_class("woost.views.ImageGallery")
            .thumbnail_sizes.keys(),
        member_group = "content"
    )

    close_up_factory = ImageFactoryMember(
        required = True,
        default = "image_gallery_close_up",
        enumeration = lambda ctx:
            templates.get_class("woost.views.ImageGallery")
            .close_up_sizes.keys(),
        member_group = "content"
    )

    close_up_preload = schema.Boolean(
        required = True,
        default = True,
        member_group = "content"
    )

    auto_play = schema.Boolean(
        required = True,
        default = False,
        member_group = "content"
    )

    labels_visible = schema.Boolean(
        required = True,
        default = True,
        member_group = "content"
    )

    footnotes_visible = schema.Boolean(
        required = True,
        default = True,
        member_group = "content"
    )

    original_link_visible = schema.Boolean(
        required = True,
        default = False,
        member_group = "content"
    )

    close_up_enabled = schema.Boolean(
        required = True,
        default = True,
        member_group = "content"
    )

    def init_view(self, view):
        Block.init_view(self, view)
        view.images = self.images
        view.gallery_type = self.gallery_type
        view.thumbnail_factory = self.thumbnail_factory
        view.close_up_factory = self.close_up_factory
        view.slider_options["auto"] = self.auto_play
        view.labels_visible = self.labels_visible
        view.footnotes_visible = self.footnotes_visible
        view.original_link_visible = self.original_link_visible
        view.close_up_enabled = self.close_up_enabled
        view.close_up_preload = self.close_up_preload

