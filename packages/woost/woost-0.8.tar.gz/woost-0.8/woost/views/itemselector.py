#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			December 2008
"""
from cocktail.modeling import extend, call_base
from cocktail.translations import translations
from cocktail.html import Element, templates
from cocktail.html.databoundcontrol import data_bound
from woost.models import (
    Item,
    CreatePermission,
    ModifyPermission,
    DeletePermission,
    get_current_user
)


class ItemSelector(Element):

    value = None
    _empty_label = None    
    existing_items_only = False

    empty_label = ""

    def _build(self):
    
        Element._build(self)
        data_bound(self)

        self.add_resource("/resources/scripts/ItemSelector.js")
        self.set_client_param("emptyLabel", self.empty_label)

        self.input = templates.new("cocktail.html.HiddenInput")
        self.append(self.input)
        self.binding_delegate = self.input
        
        self.selection_label = templates.new("woost.views.ItemLabel")
        self.selection_label.tag = "span"
        self.selection_label.add_class("selection_label")
        self.append(self.selection_label)
    
        self.buttons = self.create_buttons()
        self.append(self.buttons)

    def _ready(self):

        Element._ready(self)

        if self.member:
 
            if self.data_display:
                self._param_name = self.data_display.get_member_name(
                    self.member,
                    self.language
                )
            else:
                self._param_name = self.member.name

            if self.existing_items_only or not self.member.integral:
                # Select
                self.select_button = self.create_select_button()
                self.buttons.append(self.select_button)
            
            if not self.existing_items_only:
                
                user = get_current_user()

                if self.member.integral:

                    if self.value is None:
                        # New
                        if any(
                            user.has_permission(CreatePermission, target = cls)
                            for cls in self.member.type.schema_tree()
                        ):
                            self.new_button = self.create_new_button()
                            self.buttons.append(self.new_button)
                    else:
                        # Edit
                        if any(
                            user.has_permission(ModifyPermission, target = cls)
                            for cls in self.member.type.schema_tree()
                        ):
                            self.edit_button = self.create_edit_button()
                            self.buttons.append(self.edit_button)

                        # Delete
                        if any(
                            user.has_permission(DeletePermission, target = cls)
                            for cls in self.member.type.schema_tree()
                        ):
                            self.delete_button = self.create_delete_button()
                            self.buttons.append(self.delete_button)

                elif self.value is not None:

                    # Edit
                    if any(
                        user.has_permission(ModifyPermission, target = cls)
                        for cls in self.member.type.schema_tree()
                    ):
                        self.edit_button = self.create_edit_button()
                        self.buttons.append(self.edit_button)

                    # Unlink
                    self.unlink_button = self.create_unlink_button()
                    self.buttons.append(self.unlink_button)

        if self.value is None:
            self.selection_label.add_class("empty_selection")
            self.selection_label.append(self.empty_label)
        else:
            self.input["value"] = self.value.id
            self.selection_label.item = self.value

    def create_buttons(self):
        buttons = Element()
        buttons.add_class("ItemSelector-buttons")
        return buttons

    def create_select_button(self):

        select_button = Element("button",
            name = "ItemSelector-select",
            type = "submit",
            class_name = "ItemSelector-button select",
            value = self.member.type.full_name + "-" + self._param_name
        )
        select_button.append(
            translations("woost.views.ItemSelector select")
        )
        return select_button

    def create_unlink_button(self):
        
        unlink_button = Element("button",
            name = "ItemSelector-unlink",
            type = "submit",
            class_name = "ItemSelector-button unlink",
            value = self.member.name
        )
        unlink_button.append(
            translations("woost.views.ItemSelector unlink")
        )
        return unlink_button

    def create_new_button(self):

        new_button = Element(class_name = "ItemSelector-button new")
        
        instantiable_types = set(
            content_type
            for content_type in (
                [self.member.type] + list(self.member.type.derived_schemas())
            )
            if content_type.visible
            and content_type.instantiable
            and get_current_user().has_permission(
                CreatePermission,
                target = content_type
            )
        )

        if len(instantiable_types) > 1:
            
            new_button.add_class("selector")
            label = Element("span", class_name = "label")
            new_button.append(label)

            container = Element(class_name = "selector_content")
            new_button.append(container)
                        
            content_type_tree = templates.new("woost.views.ContentTypeTree")
            content_type_tree.root = self.member.type
            content_type_tree.filter_item = instantiable_types.__contains__

            @extend(content_type_tree)
            def create_label(tree, content_type):
                label = call_base(content_type)
                label.tag = "button"
                label["type"] = "submit"
                label["name"] = "ItemSelector-new"
                label["value"] = self.member.name + "-" + content_type.full_name
                return label
            
            container.append(content_type_tree)
        else:
            new_button.tag = "button"
            new_button["type"] = "submit"
            new_button["name"] = "ItemSelector-new"
            new_button["value"] = \
                self.member.name + "-" + list(instantiable_types)[0].full_name
            label = new_button

        label.append(translations("woost.views.ItemSelector new"))

        return new_button

    def create_edit_button(self):

        edit_button = Element("button",
            name = "ItemSelector-edit",
            type = "submit",
            class_name = "ItemSelector-button edit",
            value = self.member.name
        )
        edit_button.append(
            translations("woost.views.ItemSelector edit")
        )
        return edit_button

    def create_delete_button(self):

        delete_button = Element("button",
            name = "ItemSelector-unlink",
            type = "submit",
            class_name = "ItemSelector-button delete",
            value = self.member.name
        )
        delete_button.append(
            translations("woost.views.ItemSelector delete")
        )
        return delete_button

