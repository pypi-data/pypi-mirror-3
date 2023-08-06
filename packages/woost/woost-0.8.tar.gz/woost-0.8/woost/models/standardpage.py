#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			June 2008
"""
from cocktail import schema
from woost.models.document import Document
from woost.models.template import Template


class StandardPage(Document):
    
    default_template = schema.DynamicDefault(
        lambda: Template.get_instance(qname = "woost.standard_template")
    )

    body = schema.String(
        translated = True,
        listed_by_default = False,        
        edit_control = "woost.views.RichTextEditor",
        member_group = "content"
    )

