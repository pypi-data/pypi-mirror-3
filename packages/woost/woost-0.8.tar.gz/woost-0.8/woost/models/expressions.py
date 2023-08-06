#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from cocktail.schema.expressions import Expression
from woost.models.item import Item
from woost.models.usersession import get_current_user


class OwnershipExpression(Expression):
    """An expression that checks that an item is owned by the active user."""

    def eval(self, context, accessor = None):
        return context.get("owner") is get_current_user()

    def resolve_filter(self, query):
        return Item.owner.equal(get_current_user()).resolve_filter(query)

