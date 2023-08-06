#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			February 2010
"""
from woost.models.rendering import (
    content_renderers,
    ImageURIRenderer,
    HTMLRenderer
)
from woost.extensions.vimeo.video import VimeoVideo


class VimeoVideoRenderer(ImageURIRenderer):

    def can_render(self, item):
        return isinstance(item, VimeoVideo)

    def get_item_uri(self, item):
        return item.large_thumbnail_uri

content_renderers.register(VimeoVideoRenderer(), before = HTMLRenderer)

