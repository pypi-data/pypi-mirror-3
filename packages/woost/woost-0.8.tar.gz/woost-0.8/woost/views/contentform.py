#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2008
"""
from cocktail.schema import Collection, Reference
from cocktail.html import Element, templates

Form = templates.get_class("cocktail.html.Form")


class ContentForm(Form):

    table_layout = False

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.set_member_type_display(Reference, self._get_reference_display)

    def _resolve_member_display(self, obj, member):

        display = getattr(member, "edit_control", None)
        
        if display is None:
            display = Form._resolve_member_display(self, obj, member)

        return display

    def _get_reference_display(self, obj, member):
        if member.class_family is not None:
            display = templates.new("woost.views.ContentTypePickerDropdown")
            display.content_type_picker.root = member.class_family
        else:
            display = "woost.views.ItemSelector"
    
        return display

