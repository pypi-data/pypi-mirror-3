#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Jordi Fernández <jordi.fernandez@whads.com>
"""
from cocktail import schema
from woost.extensions.blocks.block import Block
from woost.extensions.vimeo.video import VimeoVideo


class VimeoBlock(Block):

    instantiable = True
    view_class = "woost.extensions.vimeo.VimeoPlayer"

    members_order = "video", "video_width", "video_height"


    video = schema.Reference(
        required = True,
        type = VimeoVideo,
        related_end = schema.Collection(),
        member_group = "content",
    )

    video_width = schema.Integer(
        member_group = "content"
    )

    video_height = schema.Integer(
        member_group = "content"
    )

    def init_view(self, view):
        Block.init_view(self, view)
        view.video = self.video
        if self.video_width:
            view.flash_width = self.video_width
        if self.video_height:
            view.flash_height = self.video_height

