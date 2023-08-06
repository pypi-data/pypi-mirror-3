#-*- coding: utf-8 -*-
u"""

@author:		Javier Marrero
@contact:		javier.marrero@whads.com
@organization:	Whads/Accent SL
@since:			March 2009
"""
from cocktail.html import templates, Element
from cocktail.controllers import context
from woost.models import Site

TreeView = templates.get_class("cocktail.html.TreeView")


class Menu(TreeView):
    """A visual component used to render navigation menus and site maps.
    
    @var emphasized_selection: When set to True, adds a <strong> tag to
        highlight the selected item.
    @type emphasized_selection: bool

    @var linked_selection: Indicates if the entry for the selected item should
        behave as a link or not.
    @type linked_selection: bool
    
    @var linked_containers: Indicates if entries that contain other entries
        should behave as links.
    @type linked_containers: bool
    """
    root_visibility = TreeView.HIDDEN_ROOT
    expanded = False
    emphasized_selection = True
    linked_selection = True
    linked_containers = True
    display_filtered_containers = False
    validate_permissions = True

    def _ready(self):

        if self.root is None:
            self.root = Site.main.home

        if self.selection is None:
            self.selection = context["publishable"]
       
        TreeView._ready(self)
    
    def filter_item(self, item):
        return not item.hidden and (
            item.is_accessible()
            if self.validate_permissions
            else item.is_published()
        )

    def get_item_uri(self, item):
        return item.get_uri(host = ".")

    def create_label(self, item):
        
        if self.should_link(item):
            label = Element("a")
            label["href"] = self.get_item_uri(item)
        else:
            label = Element("span")
        
        label.append(self.get_item_label(item))

        if self.emphasized_selection and item is self.selection:
            if label.tag == "a":
                label = Element("strong", children = [label])
            else:
                label.tag = "strong"

        return label

    def should_link(self, item):
        return (self.linked_selection or item is not self.selection) \
            and (self.linked_containers or not item.children)

