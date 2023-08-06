#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2009
"""
from cocktail.modeling import cached_getter, ListWrapper
from cocktail import schema
from cocktail.controllers import UserCollection
from cocktail.controllers.userfilter import GlobalSearchFilter
from woost.models import (
    ReadMemberPermission,
    get_current_user
)
from woost.controllers.backoffice.contentviews import global_content_views


class BackOfficeUserCollection(UserCollection):
    """An extended user collection that adds support for backoffice specific
    parameters.

    @var content_views_registry: A registry listing the different content views
        available to content types.
    @type: L{ContentViewsRegistry
             <woost.controllers.contentviews.ContentViewsRegistry>}
    """
    content_views_registry = global_content_views    

    # Content view dependant capabilities
    #--------------------------------------------------------------------------
    @cached_getter
    def allow_member_selection(self):
        return self.content_view.allow_member_selection

    @cached_getter
    def allow_language_selection(self):
        return self.content_view.allow_language_selection
    
    @cached_getter
    def allow_filters(self):
        return self.content_view.allow_filters

    @cached_getter
    def allow_sorting(self):
        return self.content_view.allow_sorting

    @cached_getter
    def allow_grouping(self):
        return self.content_view.allow_grouping

    @cached_getter
    def allow_paging(self):
        return self.content_view.allow_paging

    # Type
    #--------------------------------------------------------------------------    
    @cached_getter
    def type(self):
        type = UserCollection.type(self)

        if not type.visible:
            type = self.root_type

        return type

    @cached_getter
    def adapter(self):
        """The schema adapter used to produce data suitable for listing.
        @type: L{SchemaAdapter<cocktail.schema.adapter.SchemaAdapter>}
        """
        user = get_current_user()
        adapter = schema.Adapter()
        adapter.exclude([
            member.name
            for member in self.type.members().itervalues()
            if not member.visible
            or not user.has_permission(
                ReadMemberPermission,
                member = member
            )
        ])
        return adapter

    @cached_getter
    def schema(self):
        """The schema used by the produced listing of persistent items.
        @type: L{Schema<cocktail.schema.schema.Schema>}
        """
        content_schema = UserCollection.schema(self)
        
        if content_schema is not self.type:
            
            # Descriptive column
            content_schema.name = "BackOfficeContentView"
            content_schema.add_member(
                schema.Member(name = "element", searchable = False)
            )
            content_schema.members_order.insert(0, "element")
        
            # Type column
            if any(cls.visible for cls in self.type.derived_schemas()):
                content_schema.add_member(
                    schema.Member(name = "class", searchable = False)
                )
                content_schema.members_order.insert(1, "class")

        return content_schema

    # Content view
    #--------------------------------------------------------------------------    
    @cached_getter
    def content_view(self):
        """The selected content view for the current request (flat view, tree
        view, thumbnails view, etc).
        @type: L{ContentView<woost.views.ContentView>}
        """ 
        content_view_type = None
        content_view_param = self.params.read(
            schema.String("content_view")
        )
        
        # Explicitly chosen content view
        if content_view_param is not None:
            for content_view_type in self.available_content_views:
                if content_view_type.content_view_id == content_view_param:
                    break
            else:
                content_view_type = None

        # Default content view
        if content_view_type is None:
            content_view_type = (
                self.content_views_registry.get_default(self.type)
                or self.available_content_views[0]
            )
        
        # Instantiate and initialize the content view
        content_view = content_view_type()

        params = self.content_views_registry.get_params(
            self.type,
            content_view_type
        )

        for key, value in params.iteritems():
            setattr(content_view, key, value)

        content_view._init_user_collection(self)        
        return content_view
    
    @cached_getter
    def available_content_views(self):
        """The list of all content view classes available to the selected
        content type.
        @type: sequence of L{Element<cocktail.html.element.Element>} subclasses
        """        
        return ListWrapper([
            content_view
            for content_view
                in self.content_views_registry.get(self.type)
            if content_view.compatible_with(self)
        ])

    # Members
    #--------------------------------------------------------------------------    
    @cached_getter
    def default_members(self):
        content_schema = self.schema
        return set([member
                for member in UserCollection.default_members(self)
                if content_schema.get_member(member).listed_by_default])

    # Filters
    #--------------------------------------------------------------------------    
    def should_ignore_filter(self, filter):
        return isinstance(filter, GlobalSearchFilter) and not filter.value
    
    # Tree expansion
    #--------------------------------------------------------------------------
    @cached_getter
    def expanded_items(self):
        if self.params.read(schema.String("expanded")) == "all":
            return "all"
        else:
            return self.params.read(
                schema.Collection(
                    "expanded",
                    type = set,
                    items = schema.Integer(),
                    default = set()
                )
            )

