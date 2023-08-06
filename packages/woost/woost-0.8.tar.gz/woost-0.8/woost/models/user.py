#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from hashlib import sha1
from cocktail.events import event_handler
from cocktail.translations import translations
from cocktail import schema
from woost.models.site import Site
from woost.models.item import Item
from woost.models.role import Role
from woost.models.messagestyles import (
    role_style,
    permission_style,
    permission_check_style,
    permission_param_style,
    authorized_style,
    unauthorized_style
)

verbose = False

CMS_TRANSLATIONS = "en", "es", "ca"


class User(Item):
    """An application user.

    @ivar anonymous: Indicates if this is the user that represents
        anonymous users.

        To handle anonymous access to the application, an instance of the
        User class is designated to represent anonymous users. This allows
        uniform treatment of both anonymous and authenticated access (ie.
        authorization checks).
        
        This property indicates if the user it is invoked on is the
        instance used to represent anonymous users.

    @type anonymous: bool

    @ivar encryption_method: The hashing algorithm used to encrypt user
        passwords. Should be a reference to one of the algorithms provided
        by the L{hashlib} module.
    """    
    edit_form = "woost.views.UserForm"
    edit_node_class = \
        "woost.controllers.backoffice.usereditnode.UserEditNode"

    encryption_method = sha1

    anonymous = False
    
    members_order = [
        "enabled",
        "email",
        "password",
        "prefered_language"
    ]

    email = schema.String(
        required = True,
        unique = True,
        descriptive = True,
        max = 255,
        indexed = True,
        format = "^.+@.+$"
    )   

    password = schema.String(
        required = True,
        listable = False,
        listed_by_default = False,
        searchable = False,
        text_search = False,
        min = 8,
        visible_in_detail_view = False,
        edit_control = "cocktail.html.PasswordBox"
    )

    prefered_language = schema.String(
        required = True,
        default = schema.DynamicDefault(
            lambda: Site.main.backoffice_language
        ),
        enumeration = lambda ctx: Site.backoffice_language.enumeration,
        translate_value = lambda value, language = None, **kwargs:
            "" if value is None else translations(value, language, **kwargs),
        text_search = False
    )

    roles = schema.Collection(
        items = "woost.models.Role",
        bidirectional = True
    )

    enabled = schema.Boolean(
        required = True,
        default = True
    )

    def encryption(self, data):

        if self.encryption_method:

            if isinstance(data, unicode):
                data = data.encode("utf-8")

            data = self.encryption_method(data).digest()

        return data

    @event_handler
    def handle_changing(cls, event):

        if event.member is cls.password \
        and event.value is not None:
            event.value = event.source.encryption(event.value)

    def test_password(self, password):
        """Indicates if the user's password matches the given string.
        
        @param password: An unencrypted string to tests against the user's
            encrypted password.
        @type password: str

        @return: True if the passwords match, False otherwise.
        @rtype: bool
        """
        if password:
            return self.encryption(password) == self.password
        else:
            return not self.password

    def iter_roles(self, recursive = True):
        """Obtains all the roles that apply to the user.

        The following roles can be yielded:
        
            * The user's L{explicit roles<roles>} will be yielded if defined
            * An 'authenticated' role will be yielded if the user is not
              L{anonymous}
            * An 'everybody' role that applies to all users will always be
              yielded

        Roles are sorted in descending relevancy order.

        @return: An iterable sequence of roles that apply to the user.
        @rtype: L{Role}
        """
        explicit_roles = self.roles        
        if explicit_roles:
            if recursive:
                for role in explicit_roles:
                    for ancestor_role in role.iter_roles():
                        yield ancestor_role
            else:
                for role in explicit_roles:
                    yield role

        for role in self.iter_implicit_roles():
            yield role

    def iter_implicit_roles(self):

        if not self.anonymous:
            yield Role.require_instance(qname = "woost.authenticated")

        yield Role.require_instance(qname = "woost.everybody")

    def has_role(self, role):
        """Determines if the user has been granted the indicated role.

        This takes into account inherited and implicit roles.

        @return: True if the user possesses the given role, False otherwise.
        @rtype: bool
        """
        for user_role in self.iter_roles():
            if user_role is role:
                return True

        return False

    def iter_permissions(self, permission_type = None):
        """Iterates over the permissions granted to the user's roles.

        This method yields all permissions that are granted to any of the
        user's roles.

        @param permission_type: If given, restricts the list of returned
            permissions to those of the given type (or a subclass of that
            type). By default, all permissions are yielded, regardless of their
            type.
        @type permission_type: L{Permission} subclass

        @return: An iterable sequence of permissions granted to any of the
            user's roles.
        @rtype: L{Permission} sequence
        """
        for role in self.iter_roles(False):
            for permission in role.iter_permissions(permission_type):
                yield permission

    def has_permission(self,
        permission_type,
        verbose = None,        
        **context):
        """Determines if the user is given permission to perform an action.

        @param permission_type: The kind of permission to assert.
        @type permission_type: L{Permission} subclass

        @param verbose: A boolean flag that enables or disables on screen
            reporting of the checks executed by this method. Can help debugging
            authorization issues. When set, overrides the value of the module
            L{verbose} flag.
        @type verbose: bool

        @param context: Keyword parameters to supply to each tested permission.
            Each parameter will be forwarded to the permission's
            L{match<woost.models.permission.Permission.match>} method. Each
            subclass or L{Permission<woost.models.permission.Permission>}
            can define its set of required parameters, and all of its
            subclasses must implement exactly that set.

        @return: True if the user is granted permission, else False.
        @rtype: bool
        """
        if verbose is None:
            verbose = globals()["verbose"]
            
        if verbose:
            role = None
            print permission_check_style(translations(permission_type.name))
            print permission_param_style("user", translations(self))

            for key, value in context.iteritems():
                if isinstance(value, type):
                    value = translations(value.name)
                else:
                    trans = translations(value)
                    if trans and isinstance(value, Item):
                        value = u"%s (%s)" % (unicode(value), trans)
                    else:
                        value = trans or unicode(value)

                print permission_param_style(key, value)

        permissions = self.iter_permissions(permission_type)

        for permission in permissions:
            
            if verbose:
                new_role = permission.role
                if new_role is not role:
                    role = new_role
                    print role_style(translations(role))

                print permission_style(
                    "#%d. %s" % (permission.id, translations(permission))
                )

            if permission.match(verbose = verbose, **context):

                if permission.authorized:
                    if verbose:
                        print authorized_style("authorized")
                    return True
                else:
                    break                

        return permission_type.permission_not_found(
            self,
            verbose = verbose,
            **context
        )

    def require_permission(self, permission_type, verbose = None, **context):
        """Asserts the user has permission to perform an action.

        This method is similar to L{has_permission}, but instead of returning a
        boolean value, it will raise an exception if the permission is not
        granted.

        @param permission_type: The kind of permission to assert.
        @type permission_type: L{Permission} subclass

        @param verbose: A boolean flag that enables or disables on screen
            reporting of the checks executed by this method. Can help debugging
            authorization issues. When set, overrides the value of the module
            L{verbose} flag.
        @type verbose: bool

        @param context: Keyword parameters to supply to each tested permission.
            Each parameter will be forwarded to the permission's
            L{match<woost.models.permission.Permission.match>} method. Each
            subclass or L{Permission<woost.models.permission.Permission>}
            can define its set of required parameters, and all of its
            subclasses must implement exactly that set.

        @raise L{AuthorizationError}: Raised if the user doesn't have the
            specified permission.
        """
        if not self.has_permission(
            permission_type,
            verbose = verbose,
            **context
        ):
            raise AuthorizationError(
                user = self,
                permission_type = permission_type,
                context = context
            )


class AuthorizationError(Exception):
    """An exception raised when a user attempts an unauthorized action.

    @ivar user: The user that attempted the action.
    @type user: L{User}

    @ivar permission_type: The kind of permission lacked by the user.
    @type permission_type:
        L{Permission<woost.models.permission.Permission>} subclass

    @ivar context: A mapping with additional parameters providing context to
        the attempted action.
    @type context: dict
    """
    user = None
    permission_type = None
    context = None

    def __init__(self, user = None, permission_type = None, context = None):
        self.user = user
        self.permission_type = permission_type
        self.context = context

