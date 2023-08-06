#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import os
from shutil import rmtree, copy
from cocktail.events import when
from cocktail.persistence import datastore
from woost import app
from woost.models.item import Item
from woost.models.user import User
from woost.models.permission import RenderPermission
from woost.models.rendering.formats import (
    mime_types_by_format,
    extensions_by_format,
    formats_by_extension,
    default_format
)
from woost.models.rendering.factories import (
    image_factories,
    parse_image_factory_parameters
)

debug = False

def _remove_dir_contents(path):
    
    # os.path.lexists is not supported on windows
    from cocktail.styled import styled
    exists = getattr(os.path, "lexists", os.path.exists)

    if exists(path):
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            if debug:
                print styled(" " * 4 + item_path, "red")
            try:
                if os.path.isdir(item_path):
                    rmtree(item_path)
                else:
                    os.remove(item_path)
            except OSError, ex:
                if debug:
                    print styled(ex, "red")

def clear_image_cache(item = None):
    
    if debug:
        from cocktail.styled import styled
        if item is None:
            print styled("Clearing image cache", "red")
        else:
            print styled("Clearing image cache for", "red"),
            print styled(item, "red", style = "bold")

    # Remove the full cache
    if item is None:
        _remove_dir_contents(app.path("image-cache"))
        _remove_dir_contents(app.path("static", "images"))
    
    # Remove the cache for a single item
    else:
        from cocktail.styled import styled
        _remove_dir_contents(app.path("image-cache", str(item.id)))
        _remove_dir_contents(app.path("static", "images", str(item.id)))

@when(Item.changed)
@when(Item.deleted)
def _clear_image_cache_after_commit(event):
    item = event.source    
    if item.is_inserted:
        datastore.unique_after_commit_hook(
            "woost.models.clear_image_cache-%d" % item.id,
            _clear_image_cache_after_commit_callback,
            item
        )

def _clear_image_cache_after_commit_callback(commit_successful, item):
    if commit_successful:
        clear_image_cache(item)

def require_rendering(
    item,
    factory_name = "default",
    format = None,
    parameters = None):

    factory = image_factories.get(factory_name)
    
    if factory is None:
        raise BadRenderingRequest("Invalid image factory: %s" % factory_name)
    
    ext = None

    if format is None:        
        if not isinstance(item, type):
            ext = getattr(item, "file_extension", None)
            
            if ext is not None:
                format = formats_by_extension.get(ext.lstrip(".").lower())
                if format is None:
                    ext = None
    
    elif format not in mime_types_by_format:
        raise BadRenderingRequest("Invalid image format: %s" % format)

    if format is None:
        format = default_format

    if ext is None:
        ext = extensions_by_format[format]

    file_name = factory_name
    if parameters:
        file_name += "." + parameters
    file_name += "." + ext
    
    item_id = item.full_name if isinstance(item, type) else str(item.id)

    # If the image hasn't been generated yet, do so and store it in the
    # application's image cache
    image_cache_file = app.path("image-cache", item_id, file_name)

    if not os.path.exists(image_cache_file):

        # Generate the file
        values = parse_image_factory_parameters(factory.parameters, parameters)
        image = factory(item, *values)

        # Store the generated image in the image cache
        try:
            os.mkdir(app.path("image-cache", item_id))
        except OSError:
            pass

        if isinstance(image, basestring):
            try:
                os.remove(image_cache_file)
            except OSError:
                pass
            
            if hasattr(os, "symlink"):
                os.symlink(image, image_cache_file)
            else:
                copy(image, image_cache_file)
        else:
            if format == 'JPEG' and image.mode not in ('RGB', 'RGBA'):
                image = image.convert('RGBA')
            image.save(image_cache_file, format)

    # If the image is accessible to anonymous users, create a link in the
    # application's static content folder (further requests will be served
    # by the web server, no questions asked).
    if hasattr(os, "symlink"):
        static_publication_link = app.path("static", "images", item_id, file_name)

        if not os.path.lexists(static_publication_link):
            anonymous = User.require_instance(qname ="woost.anonymous_user")

            if anonymous.has_permission(
                RenderPermission, 
                target = item,
                image_factory = factory_name
            ):
                try:
                    os.mkdir(app.path("static", "images", item_id))
                except OSError:
                    pass
                os.symlink(image_cache_file, static_publication_link)

    return image_cache_file


class BadRenderingRequest(Exception):
    """An exception raised when trying to render a piece of content using
    invalid parameters (ie. an unknown image factory or image format).
    """

