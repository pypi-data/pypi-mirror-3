#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			February 2010
"""
import os
import cherrypy
from cocktail.controllers import serve_file
from woost.models import (
    Item,
    get_current_user,
    RenderPermission
)
from woost.models.rendering.cache import require_rendering, BadRenderingRequest
from woost.models.rendering.formats import formats_by_extension
from woost.controllers.basecmscontroller import BaseCMSController


class ImagesController(BaseCMSController):
    """A controller that produces, caches and serves images representing the
    different kinds of content managed by the CMS.
    """

    def __call__(self, id, processing, *args, **kwargs):

        # Get the requested element or content type
        item = None

        try:
            item_id = int(id)
        except ValueError:
            for cls in Item.schema_tree():
                if cls.full_name == id:
                    item = cls
                    break            
        else:
            item = Item.get_instance(item_id)

        # Make sure the selected element exists
        if item is None:
            raise cherrypy.NotFound()

        # Handle legacy image requests (woost < 0.8)
        if args or kwargs or "(" in processing:
            raise cherrypy.HTTPError(410)

        # Parse the given processing string, splitting the image factory from
        # the image format (ie. "home_thumbnail.png" -> ("home_thumbnail", "PNG"))
        parts = processing.rsplit(".", 1)
        parameters = None

        if len(parts) == 2:
            factory_string, ext = parts
            factory_parts = factory_string.split(".", 1)
            if len(factory_parts) == 1:
                factory_name = factory_string
            else:
                factory_name, parameters = factory_parts
            format = formats_by_extension.get(ext)
            if format is None:
                raise cherrypy.HTTPError(
                    400,
                    "Invalid image extension: %s" % ext
                )
        else:
            factory_name = processing
            format = None
    
        # Deny access to unauthorized elements
        get_current_user().require_permission(
            RenderPermission,
            target = item,
            image_factory = factory_name
        )
 
        try:
            image_cache_file = require_rendering(
                item, 
                factory_name, 
                format,
                parameters
            )
        except BadRenderingRequest, ex:
            raise cherrypy.HTTPError(400, ex.message)

        return serve_file(image_cache_file)

