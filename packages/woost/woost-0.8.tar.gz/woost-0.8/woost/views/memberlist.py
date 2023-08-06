#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2009
"""
from cocktail.translations import translations
from cocktail.html import Element
from cocktail.html.checkbox import CheckBox
from woost.models import Item


class MemberList(Element):

    root_type = Item
    name = None
    value = ()

    def _build(self):
        self.add_resource("/cocktail/scripts/autocomplete.js")
        self.add_resource("/resources/scripts/MemberList.js")

    def _ready(self):

        if not self.name and self.data_display:
            self.name = self.data_display.get_member_name(
                self.member,
                self.language
            )

        if self.root_type:            
            self.append(self.create_class_entry(self.root_type))

        Element._ready(self)

    def create_class_entry(self, cls):
        
        entry = Element()
        entry.add_class("content_type")

        entry.label = self.create_class_label(cls)
        entry.append(entry.label)

        entry.members_container = Element()
        entry.members_container.add_class("members")
        
        has_visible_members = False

        for member in cls.members(False).itervalues():
            if self.member_is_eligible(member):
                has_visible_members = True
                entry.members_container.append(
                    self.create_member_entry(member)
                )

        if has_visible_members:
            entry.append(entry.members_container)

        entry.derived_classes_container = Element()
        entry.derived_classes_container.add_class("derived_classes")
        entry.append(entry.derived_classes_container)

        for derived_schema in cls.derived_schemas(recursive = False):
            if derived_schema.visible:
                entry.derived_classes_container.append(
                    self.create_class_entry(derived_schema)
                )

        return entry

    def create_class_label(self, cls):
        label = Element("span")
        label.add_class("label")
        label.append(translations(cls.name))
        return label

    def member_is_eligible(self, member):
        return member.visible and member.name != "translations"

    def create_member_entry(self, member):

        value = member.schema.full_name + "." + member.name

        entry = Element()        

        entry.check = CheckBox()
        entry.check["name"] = self.name
        entry.check.require_id()        
        entry.check.value = value in self.value
        entry.check["value"] = value
        entry.append(entry.check)

        entry.label = Element("label")
        entry.label["for"] = entry.check["id"]
        entry.label.append(
            translations(member.schema.name + "." + member.name)
        )
        entry.append(entry.label)

        return entry

