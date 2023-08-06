#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from woost import app
from woost.models.rendering.contentrenderer import ContentRenderer
from woost.models.rendering.contentrenderersregistry import icon_renderers


class IconRenderer(ContentRenderer):

    def can_render(self, item):
        return True

    def render(self, item, size = 16):
        return app.icon_resolver.find_icon(item, size)


icon_renderers.register(IconRenderer())

