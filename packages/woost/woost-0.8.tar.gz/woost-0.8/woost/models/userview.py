#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			June 2009
"""
from cocktail import schema
from cocktail.controllers.viewstate import view_state
from woost.models.item import Item
from woost.models.role import Role


class UserView(Item):

    members_order = ["title", "parameters", "roles"]
    edit_controller = \
        "woost.controllers.backoffice.userviewfieldscontroller." \
        "UserViewFieldsController"
    edit_view = "woost.views.UserViewFields"

    title = schema.String(
        descriptive = True,
        translated = True,
        required = True,
        unique = True
    )

    def _parse_parameters(form_reader, data):

        if data is None:
            return None

        params = {}

        for param in data.split("\n"):
            param = param.strip()
            if param:
                parts = param.split("=")
                if len(parts) != 2:
                    return data # Parse error
                key, value = parts
                if key in params:
                    prev_value = params[key]
                    if isinstance(prev_value, basestring):
                        params[key] = [prev_value, value]
                    else:
                        prev_value.append(value)
                else:
                    params[key] = value
        
        return params

    def _serialize_parameters(value):
        if value:
            return "\n".join(
                "%s=%s" % (key, value)
                if isinstance(value, basestring)
                else ("\n".join("%s=%s" % (key, x) for x in value))
                for key, value in value.iteritems()
            )
        else:
            return ""

    parameters = schema.Mapping(
        keys = schema.String(),
        edit_inline = True
    )

    del _parse_parameters
    del _serialize_parameters

    roles = schema.Collection(
        items = "woost.models.Role",
        bidirectional = True
    )

    def uri(self, **kwargs):        
        params = self.parameters.copy()
        params.update(kwargs)
        params = dict((str(key), value) for key, value in params.iteritems())
        return "?" + view_state(**params)

