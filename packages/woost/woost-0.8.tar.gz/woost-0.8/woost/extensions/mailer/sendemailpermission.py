#-*- coding: utf-8 -*-
"""

@author:		Jordi Fernández
@contact:		jordi.fernandez@whads.com
@organization:	Whads/Accent SL
@since:			September 2010
"""
from cocktail import schema
from woost.models import Permission, Role
from woost.models.messagestyles import permission_doesnt_match_style


class SendEmailPermission(Permission):
    """Permission to send an email."""

    instantiable = True

    roles = schema.Collection(
        items = schema.Reference(
            type = Role,
        ),
        related_end = schema.Collection(),
        relation_constraints = [Role.implicit.equal(False)],
        edit_inline = True
    )

    def match(self, role = None, verbose = False):

        if role and self.roles and role not in self.roles:

            if verbose:
                print permission_doesnt_match_style("Role doesn't match")
            
            return False

        return Permission.match(self, verbose)

