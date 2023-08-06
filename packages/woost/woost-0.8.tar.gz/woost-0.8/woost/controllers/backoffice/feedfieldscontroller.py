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

from woost.models import Item
from woost.controllers.backoffice.contentviews import ContentViewsRegistry

from woost.controllers.backoffice.contentcontroller \
    import ContentController

from woost.controllers.backoffice.itemfieldscontroller \
    import ItemFieldsController


class FeedFieldsController(ItemFieldsController, ContentController):

    @cached_getter
    def persistence_prefix(self):
        return "Feed%s" % self.stack_node.item.id
    
    def _handle_form_data(self):

        form_data = self.stack_node.form_data
        query_parameters = form_data["query_parameters"]        
        ItemFieldsController._handle_form_data(self)                
        form_data["query_parameters"] = query_parameters

        source = self.query_parameters_source
        query_parameters.update(
            type = source.get("type"),
            order = source.get("order"),
            filter = source.get("filter")
        )
        for key, value in source.iteritems():
            if key.startswith("filter_"):
                query_parameters[key] = value
        
    @cached_getter
    def query_parameters_source(self):
        source = self.stack_node.form_data["query_parameters"].copy()
        source.update(cherrypy.request.params)
        return source

    @cached_getter
    def user_collection(self):
        user_collection = ContentController.user_collection(self)
        user_collection.__class__.type.clear(user_collection)
        user_collection.params.source = self.query_parameters_source.get
        user_collection.content_views_registry = ContentViewsRegistry()
        user_collection.content_views_registry.add(
            Item,
            "woost.views.FlatContentView",
            is_default = True
        )
        return user_collection

    @cached_getter
    def output(self):
        output = ContentController.output(self)
        output.update(ItemFieldsController.output(self))
        return output

