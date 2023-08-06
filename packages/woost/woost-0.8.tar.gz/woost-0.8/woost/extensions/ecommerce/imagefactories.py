#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from woost.models.rendering import image_factory, content_renderers

@image_factory
def ecommerce_basket_thumbnail(item):
    return content_renderers.render(item, effects = "thumbnail(75,75)")

