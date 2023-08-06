#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2008
"""
from cocktail import schema
from woost.models.document import Document


class Event(Document):

    members_order = [
        "event_start",
        "event_end",
        "event_location",
        "body"
    ]

    event_start = schema.DateTime(
        member_group = "content"
    )

    event_end = schema.DateTime(
        member_group = "content",
        min = event_start
    )

    event_location = schema.String(
        edit_control = "cocktail.html.TextArea",
        translated = True,
        member_group = "content"
    )

    body = schema.String(
        edit_control = "woost.views.RichTextEditor",
        translated = True,
        member_group = "content"
    )

