#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2008
"""
from itertools import chain
from inspect import getmro
from cocktail.pkgutils import get_full_name
from cocktail.typemapping import TypeMapping
from cocktail.html import templates
from woost.models import (
    Item,
    Publishable,
    Document,
    Event,
    ChangeSet
)


class ContentViewsRegistry(object):

    def __init__(self):
        self.__views = {}
        self.__default_views = {}
        self.__inheritance = {}
        self.__params = {}

    def add(self,
        item_type,
        content_view,
        params = None,
        is_default = False,
        inherited = True):

        type_views = self.__views.get(item_type)

        if type_views is None:
            type_views = set()
            self.__views[item_type] = type_views
        
        type_views.add(content_view)
        self.__inheritance[(item_type, content_view)] = inherited
        
        if params:
            self.set_params(item_type, content_view, params)

        if is_default:
            self.set_default(item_type, content_view)

    def remove(self, item_type, content_view):
        self.__views[item_type].remove(content_view)

    def get(self, item_type):
        
        views = set()

        for cls in getmro(item_type):
            type_views = self.__views.get(cls)
            if type_views:
                views.update(
                    templates.get_class(content_view)
                    for content_view in type_views
                    if cls is item_type
                    or self.__inheritance[(cls, content_view)]
                )

        return views

    def get_default(self, item_type):
        for cls in getmro(item_type):
            default = self.__default_views.get(cls)
            
            if default is not None \
            and (cls is item_type or self.__inheritance.get((cls, default))):
                return templates.get_class(default)

        return None

    def set_default(self, item_type, content_view):
        self.__default_views[item_type] = content_view

    def is_inherited(self, item_type, content_view):
        return self.__inheritance[(item_type, content_view)]

    def set_inherited(self, item_type, content_view, inherited):
        self.__inheritance[(item_type, content_view)] = inherited

    def get_params(self, item_type, content_view):

        if isinstance(content_view, basestring):
            content_view = templates.get_class(content_view)

        content_view = get_full_name(content_view)

        params = None
        cv_params = self.__params.get(content_view)
        
        if cv_params is not None:
            params = cv_params.get(item_type)

        return params if params is not None else {}

    def set_params(self, item_type, content_view, params):

        if isinstance(content_view, basestring):
            content_view = templates.get_class(content_view)

        content_view = get_full_name(content_view)
        
        cv_params = self.__params.get(content_view)

        if cv_params is None:
            cv_params = TypeMapping()
            self.__params[content_view] = cv_params
        
        cv_params[item_type] = params


# Global content views
#------------------------------------------------------------------------------
global_content_views = ContentViewsRegistry()

global_content_views.add(
    Item,
    "woost.views.FlatContentView",
    is_default = True
)

global_content_views.add(
    Item,
    "woost.views.ThumbnailsContentView"
)

global_content_views.add(
    Publishable,
    "woost.views.PublishableTreeContentView",
    is_default = True,
    inherited = False
)

global_content_views.add(
    Document,
    "woost.views.PublishableTreeContentView",
    is_default = True,
    inherited = False
)

global_content_views.add(
    Event,
    "woost.views.CalendarContentView",
    params = {
        "date_members": (Event.event_start, Event.event_end)
    }
)

global_content_views.add(
    ChangeSet,
    "woost.views.ChangeSetFlatContentView",
    is_default = True
)

# Relation content views
#------------------------------------------------------------------------------
relation_content_views = ContentViewsRegistry()

relation_content_views.add(
    Item,
    "woost.views.OrderContentView",
    is_default = True
)

relation_content_views.add(
    Item,
    "woost.views.FlatContentView"
)

relation_content_views.add(
    Item,
    "woost.views.ThumbnailsContentView"
)

