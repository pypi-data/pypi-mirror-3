#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cStringIO import StringIO
import cherrypy
import Image
from woost.models import (
    Item,
    get_current_user,
    ModifyPermission
)
from woost.models.rendering import content_renderers
from woost.controllers.basecmscontroller import BaseCMSController


class ImageEffectsController(BaseCMSController):

    def __call__(self, id, *effects_chain, **kwargs):

        # Get the requested item or content type, validate access
        item = None

        try:
            id = int(id)
        except ValueError:
            for cls in Item.schema_tree():
                if cls.full_name == id:
                    item = cls
                    break
        else:
            item = Item.get_instance(int(id))

        if item is None:
            raise cherrypy.NotFound()

        get_current_user().require_permission(
            ModifyPermission,
            target = item
        )

        image = content_renderers.render(
            item,
            effects_chain,
            apply_item_effects = (kwargs.get("override") != "true")
        )

        if isinstance(image, basestring):
            image = Image.open(image)

        buffer = StringIO()        
        cherrypy.response.headers["Content-Type"] = "image/png"        
        image.save(buffer, "JPEG" if image.mode == "CMYK" else "PNG")
        return buffer.getvalue()

