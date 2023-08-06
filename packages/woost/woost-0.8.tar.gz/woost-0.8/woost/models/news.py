#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from cocktail import schema
from woost.models.document import Document

class News(Document):

    members_order = [
        "summary",
        "body"
    ]

    summary = schema.String(
        edit_control = "woost.views.RichTextEditor",
        listed_by_default = False,
        translated = True,
        member_group = "content"
    )

    body = schema.String(
        edit_control = "woost.views.RichTextEditor",
        listed_by_default = False,
        translated = True,
        member_group = "content"
    )

