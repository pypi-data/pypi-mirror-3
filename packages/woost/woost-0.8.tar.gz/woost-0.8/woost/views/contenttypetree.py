#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			August 2008
"""
from cocktail.translations import translations
from cocktail.html import Element, templates
from cocktail.controllers import context
from woost.models import Item

TreeView = templates.get_class("cocktail.html.TreeView")


class ContentTypeTree(TreeView):

    root = Item
    root_visible = True
    plural_labels = False
    icon_image_factory = "icon16.png"

    def create_label(self, content_type):
        
        label = TreeView.create_label(self, content_type)

        for schema in content_type.descend_inheritance(True):
            label.add_class(schema.name)

        img = Element("img")
        img["src"] = context["cms"].image_uri(
            content_type, self.icon_image_factory
        )
        img.add_class("icon")
        label.insert(0, img)

        return label

    def get_item_label(self, content_type):
        if self.plural_labels:
            return translations(content_type.__name__ + "-plural")
        else:
            return translations(content_type.__name__)

    def get_child_items(self, content_type):
        return sorted(
            content_type.derived_schemas(recursive = False),
            key = lambda ct: translations(ct.__name__)
        )

    def filter_item(self, content_type):
        return content_type.visible


