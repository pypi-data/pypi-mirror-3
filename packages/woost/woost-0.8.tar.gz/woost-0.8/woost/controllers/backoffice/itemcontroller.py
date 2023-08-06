#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""
from threading import Lock
import cherrypy
from cocktail.modeling import cached_getter, getter
from cocktail.events import event_handler
from cocktail.pkgutils import resolve
from cocktail import schema
from cocktail.controllers import view_state, Location, get_parameter
from woost.models import (
    Item,
    ReadPermission,
    get_current_user
)

from woost.controllers.backoffice.basebackofficecontroller \
    import BaseBackOfficeController

from woost.controllers.backoffice.editstack import EditNode, RelationNode

from woost.controllers.backoffice.showdetailcontroller \
    import ShowDetailController

from woost.controllers.backoffice.differencescontroller \
    import DifferencesController


class ItemController(BaseBackOfficeController):

    default_section = "fields"
    
    diff = DifferencesController

    @cached_getter
    def preview(self):
        return resolve(self.stack_node.item.preview_controller)

    @cached_getter
    def show_detail(self):
        return resolve(self.stack_node.item.show_detail_controller)

    @cached_getter
    def fields(self):
        return resolve(self.stack_node.item.edit_controller)

    def resolve(self, path):

        if path:
            collection_name = path.pop(0)

            try:
                member = self.stack_node.content_type[collection_name]
            except KeyError:
                pass
            else:
                if any(
                    collection.name == member.name
                    for collection in self.collections
                ):
                    return self._get_collection_controller(member)

    def _get_collection_controller(self, member):
        controller_class = resolve(member.edit_controller)
        return controller_class(member)

    @cached_getter
    def collections(self):
        
        relation_node = self.relation_node
        stack_relation = relation_node and relation_node.member.related_end

        return [
            member
            for member in self.stack_node.form_schema.ordered_members()
            if isinstance(member, schema.Collection)
            and not member.edit_inline
        ]
    
    @event_handler
    def handle_traversed(cls, event):
        
        controller = event.source

        # Require an edit stack with an edit node on top
        controller._require_edit_node()

        # Disable access to invisible content types
        if not controller.stack_node.content_type.visible:
            raise cherrypy.NotFound()

        # Restrict access
        if controller.stack_node.item.is_inserted:
            get_current_user().require_permission(
                ReadPermission,
                target = controller.stack_node.item
            )
    
    def _require_edit_node(self):

        redirect = False
        context_item = self.context["cms_item"]
        edit_stacks_manager = self.context["edit_stacks_manager"]
        edit_stack = edit_stacks_manager.current_edit_stack

        # Spawn a new edit stack
        if edit_stack is None:
            edit_stack = edit_stacks_manager.create_edit_stack()
            edit_stacks_manager.current_edit_stack = edit_stack
            redirect = True
        else:
            # Integral part; add a new relation node (won't be shown to the
            # user)
            member_name = self.params.read(schema.String("member"))

            if member_name:
                node = RelationNode()
                node.member = edit_stack[-1].content_type[member_name]
                edit_stack.push(node)
                redirect = True

        # Make sure the top node of the stack is an edit node
        if not edit_stack \
        or not isinstance(edit_stack[-1], EditNode) \
        or (context_item and context_item.id != edit_stack[-1].item.id):
            
            # New item
            if context_item is None:
                content_type = get_parameter(
                    schema.Reference("item_type", class_family = Item)
                )
                item = content_type()
            # Existing item
            else:
                item = context_item
            
            node_class = resolve(item.edit_node_class)
            node = node_class(item)
            edit_stack.push(node)
            redirect = True
            
            if not item.is_inserted:
                node.initialize_new_item(
                    item,
                    get_current_user(),
                    self.visible_languages
                )
        
        # If the stack is modified a redirection is triggered so that any
        # further request mentions the new stack position in its parameters.
        # However, the redirection won't occur if the controller itself is the
        # final target of the current request - if that is the case, submit()
        # will end up redirecting the user to the default section anyway
        if redirect and self is not cherrypy.request.handler:
            location = Location.get_current()
            location.method = "GET"
            location.params["edit_stack"] = edit_stack.to_param()
            location.params.pop("member", None)
            location.go()

        return edit_stack

    def submit(self):
        self.section_redirection(self.default_section)

    def section_redirection(self, default = None):
        section = cherrypy.request.params.get("section", default)
        if section:
            self.switch_section(section)

    def switch_section(self, section):
        item = self.stack_node.item

        # Preserve form initialization parameters
        if cherrypy.request.method == "GET":
            params = dict(
                (key, value)
                for key, value in cherrypy.request.params.iteritems()
                if key.startswith("edited_item_")
            )
        else:
            params = {}
        
        raise cherrypy.HTTPRedirect(
            self.edit_uri(
                item if item.is_inserted else item.__class__,
                section,
                **params
            )
        )

