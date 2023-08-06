#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			November 2008
"""
import cherrypy
from simplejson import dumps
from cocktail.events import event_handler
from cocktail.translations import translations
from cocktail import schema
from cocktail.controllers import request_property, get_parameter
from woost.models import Item
from woost.controllers.backoffice.basebackofficecontroller \
    import BaseBackOfficeController, EditNode


class OrderController(BaseBackOfficeController):

    @request_property
    def handling_ajax_request(self):
        return self.rendering_format == "json"

    @request_property
    def content_type(self):
        return self.member.items.type
    
    @request_property
    def collection(self):
        return schema.get(self.edit_node.form_data, self.member)
    
    @request_property
    def member(self):
        key = get_parameter(schema.String("member"))
        return self.item.__class__.get_member(key) if key else None

    @request_property
    def item(self):
        return self.edit_node.item

    @request_property
    def selection(self):
        return get_parameter(
            schema.Collection("selection",
                items = schema.Reference(type = self.content_type)
            )
        )
    
    @request_property
    def position(self):
        return get_parameter(
            schema.Integer("position",
                min = 0,
                max = len(self.collection)
            )
        )

    @request_property
    def action(self):
        return get_parameter(schema.String("action"))

    @request_property
    def ready(self):
        return self.selection and self.position is not None

    def submit(self):
        
        collection = self.collection
        selection = self.selection
        position = self.position
        size = len(collection)
        selection_size = len(selection)

        if position < 0:
            position = size + position

        for item in selection:
            collection.remove(item)

        for item in selection:
            collection.insert(position, item)
            position += 1

    def handle_error(self, error):
        if self.handling_ajax_request:
            self.output["error"] = translations(error)
        else:
            BaseBackOfficeController.handle_error(self, error)
    
    @event_handler
    def handle_after_request(cls, event):
        
        controller = event.source

        if not controller.handling_ajax_request:
            if controller.action == "cancel" or controller.successful:
                if controller.edit_stack:
                    controller.edit_stack.go(-2)
                else:
                    raise cherrypy.HTTPRedirect(controller.relative_uri())

    view_class = "woost.views.BackOfficeOrderView"

    @request_property
    def output(self):
        if self.handling_ajax_request:
            return {}
        else:
            output = BaseBackOfficeController.output(self)
            output.update(
                content_type = self.content_type,
                collection = self.collection,
                selection = self.selection
            )
            return output

