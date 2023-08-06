#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			November 2008
"""
from __future__ import with_statement
from ZODB.POSException import ConflictError
import cherrypy
from simplejson import dumps
from cocktail.modeling import cached_getter
from cocktail.events import event_handler
from cocktail.iteration import first
from cocktail.translations import translations
from cocktail.schema import Reference, String, Integer, Collection, Reference
from cocktail.persistence import datastore
from woost.models import Item, changeset_context, get_current_user
from woost.controllers.backoffice.basebackofficecontroller \
    import BaseBackOfficeController


class MoveController(BaseBackOfficeController):

    MAX_TRANSACTION_ATTEMPTS = 3

    @cached_getter
    def handling_ajax_request(self):
        return self.rendering_format == "json"

    @cached_getter
    def root(self):
        return self.params.read(Reference("root", type = Item))

    @cached_getter
    def member(self):
        key = self.params.read(String("member"))
        return self.item.__class__[key] if key and self.item else None

    @cached_getter
    def collection(self):
        return self.item.get(self.member)

    @cached_getter
    def selection(self):
        return self.params.read(
            Collection("selection", items = Reference(type = Item))
        )

    @cached_getter
    def slot(self):
        param = self.params.read(String("slot", format = r"\d+-\d+"))
        return map(int, param.split("-")) if param else None

    @cached_getter
    def item(self):
        return self.slot and Item.index[self.slot[0]]

    @cached_getter
    def position(self):
        return self.slot and self.slot[1]
       
    @cached_getter
    def action(self):
        return self.params.read(String("action"))

    @cached_getter
    def ready(self):
        return self.member and self.slot and self.selection

    def submit(self):

        collection = self.collection
        selection = self.selection
        parent = self.item
        position = self.position
        related_end = self.member.related_end

        size = len(collection)

        if position < 0:
            position = size + position

        position = min(position, size)

        if any(parent.descends_from(item) for item in selection):
            raise TreeCycleError()

        for i in range(self.MAX_TRANSACTION_ATTEMPTS):
            with changeset_context(get_current_user()):
                for item in reversed(selection):

                    if isinstance(related_end, Reference) \
                    and item.get(related_end) is parent:
                        collection.remove(item)

                    collection.insert(position, item)            
            try:
                datastore.commit()
            except ConflictError:
                datastore.abort()
                datastore.sync()
            else:
                break

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
                raise cherrypy.HTTPRedirect(controller.contextual_uri())

    view_class = "woost.views.BackOfficeMoveView"

    @cached_getter
    def output(self):
        if self.handling_ajax_request:
            return {}
        else:
            output = BaseBackOfficeController.output(self)
            output.update(
                root = self.root,
                item = self.item,
                position = self.position,
                selection = self.selection
            )
            return output


class TreeCycleError(Exception):
    """An exception raised when trying to move an element to a position that
    would turn the tree into a graph."""

