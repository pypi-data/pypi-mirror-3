#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""
from cocktail.html import Element, templates
from woost.models import Item

ContentTypeSelector = \
    templates.get_class("woost.views.ContentTypeSelector")


class ContentTypePath(Element):
    
    tag = "ul"
    value = None
    root = Item

    Entry = Element
    Selector = ContentTypeSelector
    
    def _ready(self):
        
        inheritance_line = []
        
        for content_type in self.value.ascend_inheritance(True):
            inheritance_line.insert(0, content_type)
            if content_type is self.root:
                break
        
        for content_type in inheritance_line:
            entry = self.create_entry(content_type)
            self.append(entry)

        self._last_entry = entry
        Element._ready(self)

    def _content_ready(self):

        Element._content_ready(self)

        for derived_content_type in self.value.derived_schemas():
            break
        else:
            self._last_entry.selector.tree.visible = False
            self._last_entry.add_class("leaf")

    def create_entry(self, content_type):        
        entry = self.Entry()
        entry.tag = "li"
        entry.selector = self.create_selector(content_type)
        entry.append(entry.selector)        
        return entry

    def create_selector(self, content_type):
        selector = self.Selector()
        selector.root = content_type
        selector.value = content_type

        if content_type is self.value:
            selector.add_class("selected")
    
        return selector

