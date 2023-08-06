#-*- coding: utf-8 -*-
"""

@author:		Jordi Fernández
@contact:		jordi.fernandez@whads.com
@organization:	Whads/Accent SL
@since:			October 2009
"""
from cocktail import schema
from woost.models import Item


class Comment(Item):

    members_order = ["publishable", "user_name", "user_email", "content"]

    publishable = schema.Reference(
        required = True,
        type = "woost.models.Publishable",
        bidirectional = True,
        related_key = "comments"
    )

    user_name = schema.String(
        required = True
    )

    user_email = schema.String(
        required = True,
        format = r"([\w\-\.]+@(\w[\w\-]+\.)+[\w\-]+)"
    )

    content = schema.String(
        required = True,
        edit_control = "cocktail.html.TextArea"
    )

