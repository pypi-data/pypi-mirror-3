#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""
from cocktail.html import Element, templates
from woost.models import Item

ContentTypeTree = \
    templates.get_class("woost.views.ContentTypeTree")


class ContentTypeSelector(Element):

    value = None
    Tree = ContentTypeTree
    root = Item
    root_visible = True

    def _build(self):
        self.add_class("selector")

    def _ready(self):        
        
        self.tree = self.create_tree()
        self.label = self.create_label()

        self.append(self.label)
        self.append(self.tree)

        Element._ready(self)

    def create_label(self):
        label = self.tree.create_label(self.value)
        label.tag = "span"
        label.add_class("label")
        return label

    def create_tree(self):
        tree = self.Tree()
        tree.add_class("selector_content")
        tree.root = self.root
        tree.root_visible = self.root_visible
        return tree

