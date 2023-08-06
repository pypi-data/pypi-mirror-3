#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2009
"""
import cherrypy
from cocktail.modeling import cached_getter
from cocktail.events import event_handler

from woost.controllers.backoffice.contentcontroller \
    import ContentController

from woost.controllers.backoffice.itemfieldscontroller \
    import ItemFieldsController


class ContentPermissionFieldsController(ItemFieldsController, ContentController):

    @cached_getter
    def persistence_prefix(self):
        return "ContentPermission%s" % self.stack_node.item.id
    
    def _handle_form_data(self):
        ItemFieldsController._handle_form_data(self)
        form_data = self.stack_node.form_data
        form_data["matching_items"] = self.get_permission_parameters()
 
    @cached_getter
    def permission_parameters_source(self):
        source = self.stack_node.form_data["matching_items"].copy()
        source.update(cherrypy.request.params)
        return source

    def get_permission_parameters(self):
        source = self.permission_parameters_source
        params = {
            "type": source.get("type"),
            "filter": source.get("filter")
        }
        for key, value in source.iteritems():
            if key.startswith("filter_"):
                params[key] = value
        
        return params

    @cached_getter
    def user_collection(self):
        user_collection = ContentController.user_collection(self)
        user_collection.__class__.type.clear(user_collection)
        user_collection.params.source = self.permission_parameters_source.get
        return user_collection

    @cached_getter
    def output(self):
        output = ContentController.output(self)
        output.update(ItemFieldsController.output(self))
        return output

