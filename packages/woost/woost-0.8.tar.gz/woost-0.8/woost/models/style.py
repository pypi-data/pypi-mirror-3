#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""
from cocktail import schema
from cocktail.modeling import getter
from woost.models import Item


class Style(Item):

    members_order = "title", "declarations", "admin_declarations"

    title = schema.String(
        required = True,
        unique = True,
        indexed = True,
        normalized_index = True,
        full_text_indexed = True,
        descriptive = True,
        translated = True
    )

    declarations = schema.String(
        required = True,
        text_search = False,
        edit_control = "cocktail.html.TextArea"
    )
    
    admin_declarations = schema.String(
        text_search = False,
        edit_control = "cocktail.html.TextArea"
    )
    
    @getter
    def class_name(self):
        return "woost_style_%d" % self.id

