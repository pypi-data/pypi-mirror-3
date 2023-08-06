#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			August 2008
"""
from cocktail import schema
from woost.models.item import Item
from cocktail.html.datadisplay import display_factory, MULTIPLE_SELECTION


class Role(Item):
    """A set of capabilities assigned to one or more users.
    
    Each role defines an access profile for a distinct set of application users
    (editors, moderators, administrators, etc.). By grouping users into roles,
    managing permissions and defining the access policy for a site becomes
    easier.

    Roles can also extend other roles. A derived role will inherit all
    permissions from its base roles, recursively. This ability makes it
    possible to grow a site's access policy by means of specialization.
    """
    members_order = [
        "title",
        "base_roles",
        "child_roles",
        "users",
        "permissions",
        "user_views",
        "hidden_content_types"
    ]

    title = schema.String(
        required = True,
        unique = True,
        indexed = True,
        normalized_index = True,
        full_text_indexed = True,
        descriptive = True,
        translated = True
    )
    
    base_roles = schema.Collection(
        items = "woost.models.Role",
        bidirectional = True
    )
    
    child_roles = schema.Collection(
        items = "woost.models.Role",
        bidirectional = True,
        editable = False
    )
    
    users = schema.Collection(
        items = "woost.models.User",
        bidirectional = True
    )

    permissions = schema.Collection(
        items = "woost.models.Permission",
        bidirectional = True,
        integral = True
    )

    user_views = schema.Collection(
        items = "woost.models.UserView",
        bidirectional = True
    )

    hidden_content_types = schema.Collection(
        items = schema.Reference(
            class_family = Item
        ),
        edit_inline = True,
        edit_control = display_factory(
            "woost.views.ContentTypePicker",
            selection_mode = MULTIPLE_SELECTION,
            filter_item = lambda content_type:
                content_type.visible and content_type.visible_from_root
        )
    )

    implicit = schema.Boolean(
        required = True,
        default = False,
        indexed = True,
        editable = False
    )

    def iter_roles(self, include_self = True, recursive = True):
        """Iterates over the role and its bases.

        Roles are sorted from most specific to most general.

        @param include_self: If True, the role itself will be included in the
            produced sequence. If False, the role will be excluded and only its
            bases (and their bases, depending on the value of L{recursive})
            will be yielded.
        @type: bool

        @param recursive: If True, the method will be called recursively on
            each base role, producing the whole inheritance tree.
        @type recursive: bool

        @return: An iterable sequence containing the role and its bases.
        @rtype: L{Role} sequence
        """
        if include_self:
            yield self

        if recursive:
            for base in self.base_roles:
                for ancestor in base.iter_roles():
                    yield ancestor
        else:
            for base in self.base_roles:
                yield base

    def iter_permissions(self, permission_type = None):
        """Iterates over the permissions granted to the role.

        Both the role's own permissions and those inherited from its bases are
        returned.

        @param permission_type: If given, restricts the list of returned
            permissions to those of the given type (or a subclass of that
            type). By default, all permissions are yielded, regardless of their
            type.
        @type permission_type: L{Permission} subclass

        @return: An iterable sequence of permissions granted to the role and
            its bases.
        @rtype: L{Permission} sequence
        """        
        for permission in self.permissions:
            if permission_type is None or isinstance(permission, permission_type):
                yield permission

        for base_role in self.base_roles:
            for permission in base_role.iter_permissions(permission_type):
                yield permission

