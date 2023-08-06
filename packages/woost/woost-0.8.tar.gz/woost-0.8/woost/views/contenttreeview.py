#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			March 2009
"""
from cocktail.html import templates
from woost.models import get_current_user, ReadPermission

TreeView = templates.get_class("cocktail.html.TreeView")


class ContentTreeView(TreeView):

    base_url = None
    edit_stack = None

    def filter(self, item):
        return get_current_user().has_permission(ReadPermission, target = item)

    def create_label(self, item):
        label = templates.new("woost.views.ContentLink")
        label.base_url = self.base_url
        label.item = item
        label.edit_stack = self.edit_stack
        return label

