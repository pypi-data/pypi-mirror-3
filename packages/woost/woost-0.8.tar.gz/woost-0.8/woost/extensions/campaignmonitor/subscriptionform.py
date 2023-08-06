#-*- coding: utf-8 -*-
u"""

@author:        Jordi Fernández
@contact:       jordi.fernandez@whads.com
@organization:  Whads/Accent SL
@since:         March 2010
"""
from cocktail import schema

SubscriptionForm = schema.Schema("SubscriptionForm", members = [
    schema.String("email",
        required = True,
        format = r"([\w\-\.]+@(\w[\w\-]+\.)+[\w\-]+)"
    ),
    schema.String("name")
])

SubscriptionForm.members_order = "name", "email"
