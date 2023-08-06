#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""
from __future__ import with_statement

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from itertools import chain
from os.path import join
from tempfile import mkdtemp
import cherrypy
import mimetypes
import pyExcelerator
from cocktail.modeling import (
    getter,
    cached_getter,
    ListWrapper,
    SetWrapper,
    OrderedSet
)
from cocktail.events import event_handler
from cocktail.translations import translations
from cocktail.pkgutils import resolve
from cocktail import schema
from cocktail.schema import ValidationContext
from cocktail.schema.expressions import (
    Expression,
    CustomExpression,
    ExclusionExpression,
    NegativeExpression,
    InclusionExpression,
    Self
)
from cocktail.persistence import datastore
from cocktail.html.datadisplay import (
    SINGLE_SELECTION,
    MULTIPLE_SELECTION
)
from cocktail.controllers import (
    view_state,
    get_parameter,
    CookieParameterSource,
    SessionParameterSource
)
from cocktail.controllers.userfilter import GlobalSearchFilter
from woost.models import (
    Site,
    Language,
    Item,
    UserView,
    changeset_context,
    get_current_user,
    PermissionExpression,
    ReadPermission,
    ReadTranslationPermission
)
from woost.controllers.backoffice.basebackofficecontroller \
    import BaseBackOfficeController
from woost.controllers.backoffice.editstack import (
    EditNode,
    RelationNode,
    SelectionNode
)
from woost.controllers.backoffice.itemcontroller import ItemController
from woost.controllers.backoffice.useractions import get_user_action
from woost.controllers.backoffice.usercollection \
    import BackOfficeUserCollection


class ContentController(BaseBackOfficeController):
    """A controller that handles listings of persistent items."""

    section = "content"
    _item_controller_class = ItemController

    @cached_getter
    def new(self):
        self.context["cms_item"] = None
        return self._item_controller_class()

    def resolve(self, path):
        
        if not path:
            return self
        else:
            component = path.pop(0)
            try:
                item_id = int(component)
            except ValueError:
                return None
            else:
                item = self.root_content_type.get_instance(item_id)

                if item is None:
                    return None

                self.context["cms_item"] = item
                return self._item_controller_class()

    def __call__(self, *args, **kwargs):

        rel = cherrypy.request.params.get("ItemSelector-select")

        # Open the item selector
        if rel:

            # Load persistent collection parameters before redirecting
            self.user_collection

            pos = rel.find("-")
            root_content_type_name = rel[:pos]
            selection_parameter = str(rel[pos + 1:])

            for content_type in chain([Item], Item.derived_schemas()):
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
                
        return BaseBackOfficeController.__call__(self, **kwargs)

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
        if self.user_collection.selection_mode == SINGLE_SELECTION:
            selection = [self.user_collection.selection]
        else:
            selection = self.user_collection.selection

        self._invoke_user_action(self.action, selection)
    
    # Content
    #--------------------------------------------------------------------------    
    @cached_getter
    def root_content_type(self):
        """The most basic possible content type for listed items.
        
        This property is used to constrain the set of eligible content types to
        all types that descend from the indicated type (inclusive).

        @type: L{Item<woost.models.Item>} subclass
        """        
        root_content_type = self.stack_content_type

        if root_content_type is None:
            root_content_type_param = self.params.read(
                schema.String("root_content_type")
            )
            root_content_type = resolve(root_content_type_param)
    
        return root_content_type or Item

    @cached_getter
    def stack_content_type(self):
        """The content type of listed items indicated by the active edit stack.        
        @type: L{Item<woost.models.Item>} subclass
        """
        node = self.stack_node

        if node:
            if isinstance(node, SelectionNode):
                return node.content_type

            elif isinstance(node, RelationNode):
                member = node.member

                if isinstance(member, schema.Reference):
                    return member.type
                else:
                    return member.items.type

        return None
        
    @cached_getter
    def available_languages(self):
        """The list of languages that items in the listing can be displayed in.

        Each language is represented using its two letter ISO code.

        @type: sequence of unicode
        """
        user = get_current_user()
        return [
            language
            for language in Language.codes
            if user.has_permission(
                ReadTranslationPermission,
                language = language
            )
        ]
    
    @cached_getter
    def user_collection(self):

        user_collection = BackOfficeUserCollection(self.root_content_type)

        if self.edit_stack and isinstance(self.stack_node, RelationNode):
            user_collection.default_type = \
                self.stack_node.member.selector_default_type

        user_collection.available_languages = self.available_languages
        user_collection.selection_mode = self.selection_mode
        user_collection.default_order = \
            [NegativeExpression(Item.last_update_time)]

        # Parameter persistence
        prefix = self.persistence_prefix
        duration = self.persistence_duration

        user_collection.set_parameter_source("type",
            SessionParameterSource(key_prefix = prefix)
        )

        type_prefix = user_collection.type.full_name
        if prefix:
            type_prefix += "-" + prefix
        
        user_collection.persistence_prefix = type_prefix
        user_collection.persistent_source = psource = SessionParameterSource(
            key_prefix = type_prefix
        )

        user_collection.set_parameter_source("content_view", psource)
        user_collection.set_parameter_source("members", psource)
        user_collection.set_parameter_source("order", psource)
        user_collection.set_parameter_source("grouping", psource)
        user_collection.set_parameter_source("filter", psource)
        user_collection.set_parameter_source("page", psource)
        user_collection.set_parameter_source("page_size", psource)
        user_collection.set_parameter_source("expanded", psource)
        user_collection.set_parameter_source("language",
            CookieParameterSource(
                cookie_naming = "visible_languages",
                cookie_duration = duration
            )
        )

        # Exclude instances of invisible types
        def hide_invisible_types(content_type):
            if not content_type.visible:
                exclusion = ExclusionExpression(Self, content_type.keys)
                exclusion.by_key = True
                user_collection.add_base_filter(exclusion)
            else:
                for descendant_type \
                in content_type.derived_schemas(recursive = False):
                    hide_invisible_types(descendant_type)

        hide_invisible_types(user_collection.type)

        # Exclude edit drafts
        user_collection.add_base_filter(Item.draft_source.equal(None))
        
        node = self.stack_node

        if node and isinstance(node, RelationNode):
            
            relation = node.member
            is_collection = isinstance(relation, schema.Collection)
            edit_node = self.edit_stack[-2]
            excluded_items = set()

            # Exclude items that are already contained on an edited collection
            if is_collection:
                excluded_items.update(
                    schema.get(edit_node.form_data, relation)
                )

            if excluded_items:
                user_collection.add_base_filter(
                    ExclusionExpression(Self, excluded_items)
                )

            # Add relation constraints
            if relation.enumeration:
                enumeration = relation.resolve_constraint(
                    relation.enumeration, 
                    ValidationContext(
                        edit_node.item.__class__, 
                        edit_node.item,
                        persistent_object = edit_node.item
                    )
                )
                user_collection.add_base_filter(
                    InclusionExpression(
                        Self, enumeration
                    )
                )

            for constraint in relation.get_constraint_filters(edit_node.item):
                user_collection.add_base_filter(constraint)

        # Filter unauthorized items
        user_collection.add_base_filter(
            PermissionExpression(get_current_user(), ReadPermission)
        )
       
        return user_collection

    @cached_getter
    def selection_mode(self):
        if self.edit_stack \
        and isinstance(self.stack_node, RelationNode) \
        and isinstance(self.stack_node.member, schema.Reference):
            return SINGLE_SELECTION
        else:
            return MULTIPLE_SELECTION

    @cached_getter
    def search_expanded(self):
        return bool(
            self.user_collection.user_filters
            or self.params.read(schema.Boolean("search_expanded"))
        )

    @cached_getter
    def user_views(self):
        
        user = get_current_user()
        views = OrderedSet()
        
        # Role views
        for role in user.iter_roles():
            views.extend(role.user_views)

        # User views
        views.extend(UserView.select(filters = [
            UserView.owner.equal(user)
        ]))

        return views

    # Parameter persistence
    #--------------------------------------------------------------------------    
    @cached_getter
    def persistence_prefix(self):
        stack = self.edit_stack
        return stack.to_param() if stack else ""

    @cached_getter
    def persistence_duration(self):
        node = self.stack_node
        return (
            None
            if node and isinstance(node, (RelationNode, SelectionNode))
            else self.settings_duration
        )

    # Rendering
    #--------------------------------------------------------------------------
    @cached_getter
    def view_class(self):
        if self.edit_stack:
            return "woost.views.BackOfficeItemSelectorView"
        else:
            return "woost.views.BackOfficeContentView"

    @cached_getter
    def output(self):
        output = BaseBackOfficeController.output(self)
        output.update(
            user_collection = self.user_collection,
            available_languages = self.available_languages,
            selection_mode = self.selection_mode,
            root_content_type = self.root_content_type,
            search_expanded = self.search_expanded,
            user_views = self.user_views            
        )
        return output
    
    # TODO: Move MS Excel rendering to an extension
    allowed_rendering_formats = (
        BaseBackOfficeController.allowed_rendering_formats
        | frozenset(["msexcel"])
    )

    def render_msexcel(self):
        
        content_type = mimetypes.types_map.get(".xls")
        cd = 'attachment; filename="%s"' % (
            translations(self.user_collection.type.name + "-plural") + ".xls"
        )
        languages = self.params.read(
            schema.Collection("language", items = schema.String())
        )

        cherrypy.response.headers['Content-Type'] = content_type
        cherrypy.response.headers["Content-Disposition"] = cd

        buffer = StringIO()
        self.user_collection.export_file(
            buffer, mime_type = content_type, languages = languages
        )
        return buffer.getvalue()

