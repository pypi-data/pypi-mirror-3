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


class UserViewFieldsController(ItemFieldsController, ContentController):

    @cached_getter
    def persistence_prefix(self):
        return "UserView%s" % self.stack_node.item.id
    
    def _handle_form_data(self):
        ItemFieldsController._handle_form_data(self)
        form_data = self.stack_node.form_data
        form_data["parameters"] = self.get_user_view_parameters()
 
    @cached_getter
    def user_view_parameters_source(self):
        source = self.stack_node.form_data["parameters"].copy()
        source.update(cherrypy.request.params)
        return source

    def get_user_view_parameters(self):
        source = self.user_view_parameters_source
        params = {
            "type": source.get("type"),
            "content_view": source.get("content_view"),
            "order": source.get("order"),
            "members": source.get("members"),
            "page_size": source.get("page_size"),
            "filter": source.get("filter"),
            "grouping": source.get("grouping")
        }
        for key, value in source.iteritems():
            if key.startswith("filter_"):
                params[key] = value
        
        return params

    @cached_getter
    def user_collection(self):
        user_collection = ContentController.user_collection(self)
        user_collection.__class__.type.clear(user_collection)
        user_collection.params.source = self.user_view_parameters_source.get
        return user_collection

    @cached_getter
    def output(self):
        output = ContentController.output(self)
        output.update(ItemFieldsController.output(self))
        return output

