#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""
import cherrypy
from simplejson import dumps
from cocktail.pkgutils import resolve
from cocktail.modeling import cached_getter
from cocktail.translations import (
    translations,
    get_language,
    set_language
)
from cocktail.html import Element
from cocktail import schema
from woost.models import (
    get_current_user,
    ReadPermission
)
from woost.controllers.backoffice.basebackofficecontroller \
    import BaseBackOfficeController

class RenderPreviewController(BaseBackOfficeController):    
    
    def __init__(self, *args, **kwargs):
        BaseBackOfficeController.__init__(self, *args, **kwargs)
        
    def __call__(self, *args, **kwargs):

        preview_language = self.params.read(                                                                                                                                                                            
            schema.String("preview_language", default = get_language())
        )
        if preview_language:
            set_language(preview_language)

        node = self.stack_node
        
        get_current_user().require_permission(
            ReadPermission,
            target = node.item
        )
        
        node.import_form_data(
            node.form_data,
            node.item
        )
        
        errors = list(node.item.__class__.get_errors(node.item))

        if errors:
            message = Element("div",
                class_name = "preview-error-box",
                children = [
                    translations(
                        "woost.backoffice invalid item preview", 
                        preview_language
                    ),
                    Element("ul", children = [
                        Element("li", children = [translations(error)])
                        for error in errors
                    ])
                ]
            )
            message.add_resource("/resources/styles/backoffice.css")           
            return message.render_page()        
        else:
            
            self.context.update(
                original_publishable = self.context["publishable"],
                publishable = node.item
            )
            
            controller = node.item.resolve_controller()

            if controller is None:
                raise cherrypy.NotFound()

            if isinstance(controller, type):
                controller = controller()

            return controller()
