#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			February 2010
"""
import cherrypy
from cocktail.modeling import cached_getter
from cocktail.events import event_handler
from cocktail import schema
from cocktail.schema.expressions import NegativeExpression
from cocktail.controllers.parameters import SessionParameterSource
from woost.models import (
    Item,
    ChangeSet,
    Language,
    get_current_user,
    ReadHistoryPermission,
    ChangeSetPermissionExpression
)
from woost.models.userfilter import (
    ChangeSetActionFilter,
    ChangeSetTargetFilter
)
from woost.controllers.backoffice.editstack import SelectionNode
from woost.controllers.backoffice.basebackofficecontroller \
    import BaseBackOfficeController
from woost.controllers.backoffice.usercollection \
        import BackOfficeUserCollection


class ChangeLogController(BaseBackOfficeController):

    view_class = "woost.views.BackOfficeChangeLogView"

    def __call__(self, *args, **kwargs):

        rel = cherrypy.request.params.get("ItemSelector-select")

        # Open the item selector
        if rel:

            # Load persistent collection parameters before redirecting
            self.user_collection

            pos = rel.find("-")
            root_content_type_name = rel[:pos]
            selection_parameter = str(rel[pos + 1:])

            for content_type in Item.schema_tree():
                if content_type.full_name == root_content_type_name:

                    edit_stacks_manager = self.context["edit_stacks_manager"]
                    edit_stack = edit_stacks_manager.current_edit_stack

                    if edit_stack is None:
                        edit_stack = edit_stacks_manager.create_edit_stack()
                        edit_stacks_manager.current_edit_stack = edit_stack
                    
                    node = SelectionNode()                    
                    node.content_type = content_type
                    node.selection_parameter = selection_parameter
                    edit_stack.push(node)
                    raise cherrypy.HTTPRedirect(node.uri(
                        selection = self.params.read(
                            schema.String(selection_parameter)
                        ),
                        client_side_scripting = self.client_side_scripting
                    ))
                
        return BaseBackOfficeController.__call__(self, *args, **kwargs)

    @event_handler
    def handle_traversed(cls, event):
        get_current_user().require_permission(ReadHistoryPermission)

    @cached_getter
    def user_collection(self):

        class ChangeLogUserCollection(BackOfficeUserCollection):
            persistence_prefix = "changelog"
            schema = self.content_schema
            default_order = [NegativeExpression(ChangeSet.id)]
            allow_sorting = False
            allow_type_selection = False
            allow_language_selection = False
            available_languages = Language.codes

            @cached_getter
            def available_user_filters(self):
                filters = BackOfficeUserCollection.available_user_filters(self)
                cs_action_filter = ChangeSetActionFilter()
                cs_action_filter.id = "member-action"
                cs_target_filter = ChangeSetTargetFilter()
                cs_target_filter.id = "member-changes"
                filters.append(cs_action_filter)
                filters.append(cs_target_filter)
                return filters

        user_collection = ChangeLogUserCollection(ChangeSet)
        user_collection.params.source = SessionParameterSource(
            key_prefix = user_collection.persistence_prefix
        )
        user_collection.add_base_filter(
            ChangeSetPermissionExpression(get_current_user())
        )
        return user_collection

    @cached_getter
    def content_adapter(self):
        return schema.Adapter()

    @cached_getter
    def content_schema(self):
        content_schema = schema.Schema("Changelog")
        content_schema = self.content_adapter.export_schema(
            ChangeSet,
            content_schema
        )
        content_schema.add_member(
            schema.Member("action"),
            before = "changes"
        )
        
        changes = content_schema["changes"]
        changes.listed_by_default = True
        changes.searchable = True
        return content_schema

    @cached_getter
    def search_expanded(self):
        return bool(
            self.user_collection.user_filters
            or self.params.read(schema.Boolean("search_expanded"))
        )

    @cached_getter
    def output(self):
        output = BaseBackOfficeController.output(self)
        output.update(
            user_collection = self.user_collection,
            search_expanded = self.search_expanded
        )
        return output

    @cached_getter
    def action(self):
        """The user action selected by the current HTTP request.
        @type: L{UserAction<woost.controllers.backoffice.useractions.UserAction>}
        """
        return self._get_user_action()

    @cached_getter
    def ready(self):
        return self.action is not None

    def submit(self):
        self._invoke_user_action(self.action, [])

