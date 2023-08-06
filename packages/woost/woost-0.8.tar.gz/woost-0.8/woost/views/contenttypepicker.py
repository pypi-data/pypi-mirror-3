#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			November 2008
"""
from cocktail.translations import translations
from cocktail.html import Element
from cocktail.html.databoundcontrol import data_bound, bind_member
from cocktail.html.datadisplay import (
    NO_SELECTION,
    SINGLE_SELECTION,
    MULTIPLE_SELECTION
)
from woost.views.contenttypetree import ContentTypeTree


class ContentTypePicker(ContentTypeTree):
    
    name = None
    value = None

    selection_mode = SINGLE_SELECTION

    empty_option_displayed = True

    def _build(self):
        data_bound(self)
        ContentTypeTree._build(self)
        self.add_resource("/resources/scripts/ContentTypePicker.js")

    def _ready(self):
        
        self.set_client_param("selectionMode", self.selection_mode)
        self.add_client_translation("woost.views.ContentTypePicker select")
        self.add_client_translation("woost.views.ContentTypePicker accept")
        self.add_client_translation("woost.views.ContentTypePicker cancel")

        self.set_client_variable(
            "cocktail.NO_SELECTION", NO_SELECTION)
        self.set_client_variable(
            "cocktail.SINGLE_SELECTION", SINGLE_SELECTION)
        self.set_client_variable(
            "cocktail.MULTIPLE_SELECTION", MULTIPLE_SELECTION)

        if self.selection_mode == SINGLE_SELECTION:
            self._control_type = "radio"
        elif self.selection_mode == MULTIPLE_SELECTION:
            self._control_type = "checkbox"
            self.empty_option_displayed = False

        if self.member and self.name is None and self.member.name:
            self.name = self.member.name

        if self.empty_option_displayed:
            self.append(self.create_empty_option())

        ContentTypeTree._ready(self)

    def create_empty_option(self):
        
        entry = Element("li")

        entry.control = Element("input",
            type = self._control_type,
            name = self.name,
            value = "",
            checked = self.value is None
        )
        bind_member(self, entry.control)
        entry.append(entry.control)

        entry.label = Element("label")
        entry.label.add_class("entry_label")
        entry.label.add_class("empty_option")
        entry.label.append(translations("woost.views.ContentTypePicker.empty_label"))
        entry.append(entry.label)

        entry.label["for"] = entry.control.require_id()

        return entry

    def create_entry(self, content_type):
        
        entry = ContentTypeTree.create_entry(self, content_type)

        entry.control = Element("input",
            type = self._control_type,
            name = self.name,
            value = content_type.full_name,
            checked = self.value and (
                content_type is self.value
                if self.selection_mode == SINGLE_SELECTION
                else content_type in self.value
            )
        )

        bind_member(self, entry.control)
        entry.insert(0, entry.control)
        entry.label["for"] = entry.control.require_id()
        return entry

    def create_label(self, content_type):
        label = ContentTypeTree.create_label(self, content_type)
        label.tag = "label"
        return label

