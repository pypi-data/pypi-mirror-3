#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			February 2009
"""
from cocktail.html import templates
from woost.models import get_current_user, ReadPermission

List = templates.get_class("cocktail.html.List")


class ContentList(List):

    referer = None

    def _fill_entries(self):
        
        user = get_current_user()
        items = self.items

        if items is not None:
            items = [
                item
                for item in self.items
                if user.has_permission(ReadPermission, target = item)
            ]

        if items:            
            List._fill_entries(self)
        else:
            self.tag = "div"
            self.append(u"-")

    def create_entry_content(self, item):
        link = templates.new("woost.views.ContentLink")
        link.item = item
        link.referer = self.referer
        link.member = self.member
        return link

