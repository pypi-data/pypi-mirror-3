#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			February 2009
"""
from cocktail.modeling import extend, call_base
from cocktail.translations import translations
from cocktail.schema import Member, Reference, Collection
from cocktail.html import templates, Element
from woost.models import (
    get_current_user,
    Item,
    ReadMemberPermission
)


class ContentDisplayMixin(object):

    base_url = None
    referer = None

    def __init__(self):

        @extend(self)
        def get_default_member_display(self, obj, member):

            if isinstance(member, Reference):
                if member.is_persistent_relation \
                and issubclass(member.type, Item):
                    return self.display_item_reference
            
            if isinstance(member, Collection):
                if member.is_persistent_relation \
                and issubclass(member.items.type, Item):
                    return self.display_item_collection

            return call_base(obj, member)

    def display_item_reference(self, obj, member):
        display = templates.new("woost.views.ContentLink")
        display.item = self.get_member_value(obj, member)
        display.base_url = self.base_url
        display.referer = obj
        display.member = member
        return display
    
    def display_item_collection(self, obj, member):
        display = templates.new("woost.views.ContentList")
        display.items = self.get_member_value(obj, member)
        display.base_url = self.base_url
        display.referer = obj
        display.member = member
        return display

