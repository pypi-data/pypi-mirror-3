#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import os
from woost.models.file import File
from woost.models.rendering.contentrenderer import ContentRenderer
from woost.models.rendering.contentrenderersregistry import content_renderers
from woost.models.rendering.formats import formats_by_mime_type


class ImageFileRenderer(ContentRenderer):
    """A content renderer that handles image files."""

    def can_render(self, item):
        return isinstance(item, File) \
        and item.resource_type == "image" \
        and item.mime_type in formats_by_mime_type

    def render(self, item):
        return item.file_path

    def last_change_in_appearence(self, item):
        return max(
            os.stat(item.file_path).st_mtime,
            ContentRenderer.last_change_in_appearence(self, item)
        )

content_renderers.register(ImageFileRenderer())

