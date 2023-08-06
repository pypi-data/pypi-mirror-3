#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			January 2010
"""
from datetime import datetime
from cocktail.modeling import getter
from cocktail.events import event_handler
from cocktail.pkgutils import import_object
from cocktail.translations import (
    translations,
    get_language,
    require_language
)
from cocktail import schema
from cocktail.schema.expressions import Expression
from cocktail.controllers import (
    make_uri, 
    percent_encode_uri,
    Location
)
from woost.models.item import Item
from woost.models.usersession import get_current_user
from woost.models.permission import ReadPermission, PermissionExpression
from woost.models.caching import CachingPolicy


class Publishable(Item):
    """Base class for all site elements suitable for publication."""
    
    instantiable = False

    # Backoffice customization
    preview_view = "woost.views.BackOfficePreviewView"
    preview_controller = "woost.controllers.backoffice." \
        "previewcontroller.PreviewController"
    edit_node_class = "woost.controllers.backoffice.publishableeditnode." \
        "PublishableEditNode"
 
    groups_order = ["navigation", "presentation", "publication"]

    members_order = [
        "inherit_resources",
        "mime_type",
        "resource_type",
        "encoding",
        "controller",
        "parent",
        "path",
        "full_path",
        "hidden",
        "login_page",
        "enabled",
        "translation_enabled",
        "start_date",
        "end_date",
        "requires_https",
        "caching_policies"
    ]

    mime_type = schema.String(
        required = True,
        default = "text/html",
        text_search = False,
        format = r"^[^/]+/[^/]+$",
        listed_by_default = False,
        member_group = "presentation"
    )

    resource_type = schema.String(
        indexed = True,
        text_search = False,
        editable = False,
        enumeration = (
            "document",
            "image",
            "audio",
            "video",
            "package",
            "html_resource",
            "other"
        ),
        translate_value = lambda value, language = None, **kwargs:
            u"" if not value else translations(
                "woost.models.Publishable.resource_type " + value,
                 language,
                **kwargs
            ),
        listed_by_default = False,
        member_group = "presentation"
    )

    encoding = schema.String(
        listed_by_default = False,
        text_search = False,
        member_group = "presentation",
        default = "utf-8"
    )

    controller = schema.Reference(
        type = "woost.models.Controller",
        indexed = True,
        bidirectional = True,
        listed_by_default = False,
        member_group = "presentation"
    )

    inherit_resources = schema.Boolean(
        listed_by_default = False,
        member_group = "presentation",
        default = True
    )

    def resolve_controller(self):
        if self.controller and self.controller.python_name:
            return import_object(self.controller.python_name)

    parent = schema.Reference(
        type = "woost.models.Document",
        bidirectional = True,
        related_key = "children",
        listed_by_default = False,
        member_group = "navigation"
    )

    path = schema.String(
        max = 1024,
        indexed = True,
        listed_by_default = False,
        text_search = False,
        member_group = "navigation"
    )

    full_path = schema.String(
        indexed = True,
        unique = True,
        editable = False,
        text_search = False,
        member_group = "navigation"
    )
    
    hidden = schema.Boolean(
        required = True,
        default = False,
        listed_by_default = False,
        member_group = "navigation"
    )

    login_page = schema.Reference(        
        listed_by_default = False,
        member_group = "navigation"
    )

    per_language_publication = schema.Boolean(
        required = True,
        default = False,
        indexed = True,
        visible = False,
        member_group = "publication"
    )

    enabled = schema.Boolean(
        required = True,
        default = True,
        indexed = True,
        listed_by_default = False,
        member_group = "publication"
    )

    translation_enabled = schema.Boolean(
        required = True,
        default = True,
        translated = True,
        indexed = True,
        listed_by_default = False,
        member_group = "publication"
    )

    start_date = schema.DateTime(
        indexed = True,
        listed_by_default = False,
        member_group = "publication"
    )

    end_date = schema.DateTime(
        indexed = True,
        min = start_date,
        listed_by_default = False,
        member_group = "publication"
    )

    requires_https = schema.Boolean(
        required = True,
        default = False,
        listed_by_default = False,
        member_group = "publication"
    )

    caching_policies = schema.Collection(
        items = schema.Reference(type = CachingPolicy),
        bidirectional = True,
        integral = True,
        related_end = schema.Reference(),
        member_group = "publication"
    )

    def get_effective_caching_policy(self, **context):
        
        from woost.models import Site

        policies = [
            ((-policy.important, 1), policy)
            for policy in self.caching_policies
        ]
        policies.extend(
            ((-policy.important, 2), policy)
            for policy in Site.main.caching_policies
        )
        policies.sort()

        for criteria, policy in policies:
            if policy.applies_to(self, **context):
                return policy

    @event_handler
    def handle_changed(cls, event):

        member = event.member
        publishable = event.source

        if member.name == "path":
            publishable._update_path(publishable.parent, event.value)

        elif member.name == "parent":
            publishable._update_path(event.value, publishable.path)

        elif member.name == "mime_type":
            if event.value is None:
                publishable.resource_type = None
            else:
                publishable.resource_type = \
                    get_category_from_mime_type(event.value)

    def _update_path(self, parent, path):

        parent_path = parent and parent.full_path

        if parent_path and path:
            self.full_path = parent_path + "/" + path
        else:
            self.full_path = path

    def ascend_tree(self, include_self = False):
        """Iterate over the item's ancestors, moving towards the root of the
        document tree.

        @param include_self: Indicates if the object itself should be included
            in the iteration.
        @type include_self: bool

        @return: An iterable sequence of pages.
        @rtype: L{Document} iterable sequence
        """
        publishable = self if include_self else self.parent
        while publishable is not None:
            yield publishable
            publishable = publishable.parent

    def descends_from(self, page):
        """Indicates if the object descends from the given document.

        @param page: The hypothetical ancestor of the page.
        @type page: L{Document<woost.models.document.Document>}

        @return: True if the object is contained inside the given document or
            one of its descendants, or if it *is* the given document. False in
            any other case.
        @rtype: bool
        """
        ancestor = self

        while ancestor is not None:
            if ancestor is page:
                return True
            ancestor = ancestor.parent

        return False

    @getter
    def resources(self):
        """Iterates over all the resources that apply to the item.
        @type: L{Publishable}
        """
        return self.inherited_resources

    @getter
    def inherited_resources(self):
        """Iterates over all the inherited resources that apply to the item.
        @type: L{Publishable}
        """
        ancestry = []
        publishable = self
        
        while publishable.parent is not None and publishable.inherit_resources:
            ancestry.append(publishable.parent)
            publishable = publishable.parent

        ancestry.reverse()

        for publishable in ancestry:
            for resource in publishable.branch_resources:
                yield resource

    def is_current(self):
        now = datetime.now()
        return (self.start_date is None or self.start_date <= now) \
            and (self.end_date is None or self.end_date > now)
    
    def is_published(self, language = None):
        return (
            not self.is_draft
            and (
                self.get("translation_enabled", language)                
                if self.per_language_publication
                else self.enabled
            )
            and self.is_current()
        )

    def is_accessible(self, user = None, language = None):
        return self.is_published(language) \
            and (user or get_current_user()).has_permission(
                ReadPermission,
                target = self
            )

    @classmethod
    def select_accessible(cls, *args, **kwargs):
        return cls.select(filters = [
            IsAccessibleExpression(get_current_user())
        ]).select(*args, **kwargs)

    def get_uri(self, 
        path = None, 
        parameters = None,
        language = None,
        host = None,
        encode = True):
        
        from woost.models import Site
        uri = Site.main.get_path(self, language = language)

        if uri is not None:
            if self.per_language_publication:
                uri = make_uri(require_language(language), uri)
            
            if path:
                uri = make_uri(uri, *path)

            if parameters:
                uri = make_uri(uri, **parameters)

            uri = self.__fix_uri(uri, host, encode)

        return uri

    def get_image_uri(self,
        image_factory = None,
        parameters = None,
        encode = True,
        include_extension = True,
        host = None,):
                
        uri = make_uri("/images", self.id)

        if image_factory:
            uri = make_uri(uri, image_factory)

        if include_extension:
            from woost.models.rendering.formats import (
                formats_by_extension,
                extensions_by_format,
                default_format
            )
            ext = getattr(self, "file_extension", None)
            if ext is not None:
                ext = ext.lower()
            if ext is None \
            or ext.lstrip(".") not in formats_by_extension:
                ext = "." + extensions_by_format[default_format]
            uri += ext

        if parameters:
            uri = make_uri(uri, **parameters)

        return self.__fix_uri(uri, host, encode)

    def __fix_uri(self, uri, host, encode):

        if encode:
            uri = percent_encode_uri(uri)

        if host:
            if host == ".":
                location = Location.get_current_host()

                from woost.models import Site
                site = Site.main
                policy = site.https_policy

                if (
                    policy == "always"
                    or (
                        policy == "per_page" and (
                            self.requires_https
                            or not get_current_user().anonymous
                        )
                    )
                ):
                    location.scheme = "https"
                else:
                    location.scheme = "http"

                host = str(location)
            elif not "://" in host:
                host = "http://" + host

            uri = make_uri(host, uri)
        else:
            uri = make_uri("/", uri)

        return uri

Publishable.login_page.type = Publishable
Publishable.related_end = schema.Collection()


class IsPublishedExpression(Expression):
    """An expression that tests if items are published."""

    def eval(self, context, accessor = None):
        return context.is_published()

    def resolve_filter(self, query):

        def impl(dataset):

            # Exclude disabled items
            simple_pub = set(
                Publishable.per_language_publication.index.values(key = False)
            ).intersection(Publishable.enabled.index.values(key = True))
            per_language_pub = set(
                Publishable.per_language_publication.index.values(key = True)
            ).intersection(Publishable.translation_enabled.index.values(
                    key = (get_language(), True)
                )
            )
            dataset.intersection_update(simple_pub | per_language_pub)

            # Exclude drafts
            dataset.difference_update(Item.is_draft.index.values(key = True))
            
            # Remove items outside their publication window
            now = datetime.now()
            dataset.difference_update(
                Publishable.start_date.index.values(
                    min = Publishable.start_date.get_index_value(now),
                    exclude_min = True
                )
            )
            dataset.difference_update(
                Publishable.end_date.index.values(
                    min = None,
                    exclude_min = True,
                    max = Publishable.end_date.get_index_value(now),
                    exclude_max = True
                )
            )
            
            return dataset
        
        return ((-1, 1), impl)


class IsAccessibleExpression(Expression):
    """An expression that tests that items can be accessed by a user.
    
    The expression checks both the publication state of the item and the
    read permissions for the specified user.

    @ivar user: The user that accesses the items.
    @type user: L{User<woost.models.user.User>}
    """
    def __init__(self, user = None):
        Expression.__init__(self)
        self.user = user

    def eval(self, context, accessor = None):
        return context.is_accessible(user = self.user)

    def resolve_filter(self, query):

        def impl(dataset):
            access_expr = PermissionExpression(
                self.user or get_current_user(),
                ReadPermission
            )
            published_expr = IsPublishedExpression()
            dataset = access_expr.resolve_filter(query)[1](dataset)
            dataset = published_expr.resolve_filter(query)[1](dataset)
            return dataset
        
        return ((-1, 1), impl)


mime_type_categories = {}

for category, mime_types in (
    ("text/plain", ("text",)),
    ("html_resource", (
        "text/css",
        "text/javascript",
        "text/ecmascript",
        "application/javascript",
        "application/ecmascript"
    )),
    ("document", (
        "application/vnd.oasis.opendocument.text",
        "application/vnd.oasis.opendocument.spreadsheet",
        "application/vnd.oasis.opendocument.presentation",
        "application/msword",
        "application/msexcel",
        "application/msaccess",
        "application/mspowerpoint",
        "application/mswrite",
        "application/vnd.ms-excel",
        "application/vnd.ms-access",
        "application/vnd.ms-powerpoint",
        "application/vnd.ms-project",
        "application/vnd.ms-works",
        "application/vnd.ms-xpsdocument",
        "application/rtf",
        "application/pdf",
        "application/x-pdf",
        "application/postscript",
        "application/x-latex",
        "application/vnd.oasis.opendocument.database"
    )),
    ("package", (
        "application/zip",
        "application/x-rar-compressed",
        "application/x-tar",
        "application/x-gtar",
        "application/x-gzip",
        "application/x-bzip",
        "application/x-stuffit",
        "vnd.ms-cab-compressed"
    ))
):
    for mime_type in mime_types:
        mime_type_categories[mime_type] = category

def get_category_from_mime_type(mime_type):
    """Obtains the file category that best matches the indicated MIME type.
    
    @param mime_type: The MIME type to get the category for.
    @type mime_type: str

    @return: A string identifier with the category matching the indicated
        MIME type (one of 'document', 'image', 'audio', 'video', 'package',
        'html_resource' or 'other').
    @rtype: str
    """
    pos = mime_type.find("/")

    if pos != -1:
        prefix = mime_type[:pos]

        if prefix in ("image", "audio", "video"):
            return prefix
    
    return mime_type_categories.get(mime_type, "other")

