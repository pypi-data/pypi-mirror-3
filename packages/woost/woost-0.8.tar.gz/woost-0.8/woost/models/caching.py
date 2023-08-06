#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import os
from datetime import datetime
from cocktail import schema
from cocktail.translations import get_language
from cocktail.controllers import Location
from cocktail.persistence import datastore, PersistentMapping
from woost.models.item import Item


class CachingPolicy(Item):

    # TODO: combine per type filtering with a per item condition

    visible_from_root = False
    edit_form = "woost.views.CachingPolicyForm"

    groups_order = ["cache"]
    members_order = [
        "description",
        "important",
        "cache_enabled",
        "server_side_cache",
        "cache_expiration",
        "last_update_expression",
        "cache_key_expression",
        "condition"
    ]

    description = schema.String(
        descriptive = True,
        translated = True,
        listed_by_default = False
    )

    important = schema.Boolean(
        required = True,
        default = False
    )

    cache_enabled = schema.Boolean(
        required = True,
        default = True
    )

    server_side_cache = schema.Boolean(
        required = True,
        default = False,
        listed_by_default = False
    )

    cache_expiration = schema.Integer(
        min = 1,
        listed_by_default = False
    )

    condition = schema.CodeBlock(
        language = "python"        
    )

    cache_key_expression = schema.CodeBlock(
        language = "python"
    )

    last_update_expression = schema.CodeBlock(
        language = "python"
    )

    def applies_to(self, publishable, **context):
        expression = self.condition
        if expression:
            expression = expression.replace("\r", "")
            context["publishable"] = publishable
            exec expression in context
            return context.get("applies", False)

        return True

    def get_content_cache_key(self, publishable, **context):

        cache_key = (str(Location.get_current()),)

        key_qualifier = None
        
        expression = self.cache_key_expression

        if expression:
            expression = expression.replace("\r", "")
            context["publishable"] = publishable
            exec expression in context
            key_qualifier = context.get("cache_key")
        else:
            request = context.get("request")
            if request:
                key_qualifier = tuple(request.params.items())

        if key_qualifier:
            cache_key = cache_key + (key_qualifier,)

        return cache_key

    def get_content_last_update(self, publishable, **context):
        
        context["publishable"] = publishable    
        context["latest"] = latest
        
        # Per model cache invalidation
        cache_expiration = datastore.root.get("woost.cache_expiration")
        dates = []
        
        if cache_expiration:
            for cls in publishable.__class__.__mro__:
                if cls is Item:
                    break
                dates.append(cache_expiration.get(cls.full_name))

        # Custom expression
        expression = self.last_update_expression
        if expression:
            expression = expression.replace("\r", "")
            exec expression in context
            dates.append(context.get("last_update"))

        # By default, only check the item's own last update date
        else:
            dates.append(publishable.last_update_time)

        return normalize_invalidation_date(dates)

# Utility functions for last update expressions
#------------------------------------------------------------------------------

def normalize_invalidation_date(value):

    if isinstance(value, Item):
        value = value.last_update_time

    elif hasattr(value, "__iter__"):
        max_date = None
        for item in value:
            date = normalize_invalidation_date(item)
            if date is None:
                continue
            if max_date is None or date > max_date:
                max_date = date

        value = max_date
    
    return value

def expire_cache(cls = None):

    if cls is None:
        from woost.models.publishable import Publishable as cls

    cache_expiration = datastore.root.get("woost.cache_expiration")

    if cache_expiration is None:
        cache_expiration = PersistentMapping()
        datastore.root["woost.cache_expiration"] = cache_expiration

    cache_expiration[cls.full_name] = datetime.now()

def latest(selectable, *args, **kwargs):

    if not args and not kwargs \
    and hasattr(selectable, "get_last_instance_change"):
        return selectable.get_last_instance_change()

    return (
        selectable.select(
            order = Item.last_update_time.negative(),
            range = (0, 1)
        )
        .select(*args, **kwargs)
    )

def menu_items(publishable):
    items = []
    
    while publishable is not None:
        if hasattr(publishable, "children"):
            items.extend(publishable.children)
        if publishable.parent is None:
            items.append(publishable)
        publishable = publishable.parent
    
    return items

def file_date(publishable):
    try:
        ts = os.stat(publishable.file_path).st_mtime
    except IOError, OSError:
        return None

    return datetime.fromtimestamp(ts)

