#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			August 2009
"""
from cocktail.modeling import getter, cached_getter
from cocktail.schema.expressions import (
    Self,
    Constant,
    InclusionExpression,
    ExclusionExpression,
    IsInstanceExpression,
    IsNotInstanceExpression
)
from cocktail import schema
from cocktail.translations import translations
from cocktail.html import templates
from cocktail.html.datadisplay import MULTIPLE_SELECTION
from cocktail.controllers.userfilter import (
    UserFilter,
    CollectionFilter,
    user_filters_registry,
    DescendsFromFilter
)
from woost.models.item import Item
from woost.models.action import Action
from woost.models.changesets import (
    ChangeSet,
    ChangeSetHasActionExpression,
    ChangeSetHasTargetExpression,
    ChangeSetHasTargetTypeExpression
)
from woost.models.publishable import Publishable, IsPublishedExpression
from woost.models.document import Document
from woost.models.usersession import get_current_user
from woost.models.expressions import OwnershipExpression


class OwnItemsFilter(UserFilter):

    id = "owned-items"

    @cached_getter
    def schema(self):
        return schema.Schema()

    @cached_getter
    def expression(self):
        return OwnershipExpression()

user_filters_registry.add(Item, OwnItemsFilter)


class IsPublishedFilter(UserFilter):

    id = "published"

    @cached_getter
    def schema(self):
        return schema.Schema()

    @cached_getter
    def expression(self):
        return IsPublishedExpression(get_current_user())

user_filters_registry.add(Publishable, IsPublishedFilter)


class TypeFilter(UserFilter):
    id = "type"
    operators = ["eq", "ne"]

    @cached_getter
    def schema(self):
        
        def types_search_control(parent, obj, member):
            selector = templates.new("woost.views.ContentTypePicker")
            selector.root = self.content_type
            selector.selection_mode = MULTIPLE_SELECTION
            return selector

        return schema.Schema("UserFilter", members = [
            schema.String(
                "operator",
                required = True,
                enumeration = self.operators
            ),
            schema.Collection(
                "types",
                items = schema.Reference("item_type", class_family = Item),
                search_control = types_search_control
            ),
            schema.Boolean(
                "is_inherited"
            )
        ])

    @cached_getter
    def expression(self):

        if self.operator == "eq":
            return IsInstanceExpression(Self, tuple(self.types), self.is_inherited)
        elif self.operator == "ne":
            return IsNotInstanceExpression(Self, tuple(self.types), self.is_inherited)

user_filters_registry.add(Item, TypeFilter)

class ItemSelectorFilter(schema.Reference.user_filter):
    
    def search_control(self, parent, obj, member):
        control = templates.new("woost.views.ItemSelector")
        control.existing_items_only = True
        return control

schema.Reference.user_filter = ItemSelectorFilter

def _collection_search_control(self, parent, obj, member):
    control = templates.new("woost.views.ItemSelector")
    control.existing_items_only = True
    return control

CollectionFilter.search_control = _collection_search_control


class ChangeSetActionFilter(UserFilter):

    @cached_getter
    def schema(self):
        return schema.Schema("UserFilter", members = [
            schema.String(
                "value",
                required = True,
                enumeration = ["create", "modify", "delete"],
                translate_value = lambda value:
                    "" if not value
                    else translations("woost %s action" % value)
            )
        ])

    @getter
    def expression(self):
        return ChangeSetHasActionExpression(
            Self,
            Action.get_instance(identifier = self.value)
        )


class ChangeSetTargetFilter(UserFilter):

    @cached_getter
    def schema(self):
        return schema.Schema("UserFilter", members = [
            schema.Reference(
                "value",
                type = Item,
                required = True
            )
        ])

    def search_control(self, parent, obj, member):
        control = templates.new("woost.views.ItemSelector")
        control.existing_items_only = True
        return control

    @getter
    def expression(self):
        return ChangeSetHasTargetExpression(Self, self.value)


class ChangeSetTargetTypeFilter(UserFilter):

    id = "target-type"

    @cached_getter
    def schema(self):
        return schema.Schema("UserFilter", members = [
            schema.Reference(
                "value",
                class_family = Item,
                required = True
            )
        ])

    @getter
    def expression(self):
        return ChangeSetHasTargetTypeExpression(Self, Constant(self.value))

user_filters_registry.add(ChangeSet, ChangeSetTargetTypeFilter)

user_filters_registry.add(Publishable, DescendsFromFilter)
user_filters_registry.set_filter_parameter(
    Publishable, 
    DescendsFromFilter,
    "relation", Document.children
)

