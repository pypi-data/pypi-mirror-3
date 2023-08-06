#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
import re
from cocktail.modeling import classgetter
from cocktail.translations import translations
from cocktail import schema
from cocktail.persistence import datastore
from woost.models.item import Item
from woost.models.language import Language
from woost.models.file import File
from woost.models.publicationschemes import PathResolution
from woost.models.caching import CachingPolicy


class Site(Item):

    indexed = True
    instantiable = False

    groups_order = ["language", "meta", "contact", "pages", "system"]

    members_order = [
        "default_language",
        "backoffice_language",
        "heed_client_language",
        "site_name",
        "logo",
        "icon",
        "keywords",
        "description",
        "organization_name",
        "organization_url",
        "address",
        "town",
        "region",
        "postal_code",
        "country",
        "phone_number",
        "fax_number",
        "email",
        "home",
        "login_page",
        "generic_error_page",
        "not_found_error_page",
        "forbidden_error_page",
        "https_policy",
        "https_persistence",
        "smtp_host",
        "smtp_user",
        "smtp_password",
        "publication_schemes",
        "caching_policies",
        "triggers"
    ]

    @classgetter
    def main(cls):
        return cls.get_instance(qname = "woost.main_site")

    default_language = schema.String(
        required = True,
        default = "en",
        enumeration = lambda ctx: Language.codes,
        listed_by_default = False,
        text_search = False,
        translate_value = lambda value, language = None, **kwargs:
            u"" if not value else translations(value, language, **kwargs),
        member_group = "language"
    )

    backoffice_language = schema.String(
        required = True,
        enumeration = ["en", "es", "ca"],        
        default = "en",
        text_search = False,
        translate_value = lambda value, language = None, **kwargs:
            u"" if not value else translations(value, language, **kwargs),
        member_group = "language"
    )
    
    heed_client_language = schema.Boolean(
        required = True,
        default = True,
        listed_by_default = False,
        member_group = "language"
    )

    organization_name = schema.String(
        translated = True,
        listed_by_default = False,
        member_group = "contact"
    )

    organization_url = schema.String(
        listed_by_default = False,
        member_group = "contact"
    )

    address = schema.String(
        edit_control = "cocktail.html.TextArea",
        member_group = "contact",
        listed_by_default = False
    )

    town = schema.String(
        member_group = "contact",
        listed_by_default = False
    )

    region = schema.String(
        member_group = "contact",
        listed_by_default = False
    )
    
    postal_code = schema.String(
        member_group = "contact",
        listed_by_default = False
    )

    country = schema.String(
        member_group = "contact",
        listed_by_default = False
    )

    phone_number = schema.String(
        member_group = "contact",
        listed_by_default = False
    )

    fax_number = schema.String(
        member_group = "contact",
        listed_by_default = False
    )

    email = schema.String(
        format = "^.+@.+$",
        member_group = "contact",
        listed_by_default = False
    )

    home = schema.Reference(
        type = "woost.models.Publishable",
        required = True,
        listed_by_default = False,
        member_group = "pages"
    )

    login_page = schema.Reference(
        type = "woost.models.Publishable",
        listed_by_default = False,
        member_group = "pages"
    )

    generic_error_page = schema.Reference(
        type = "woost.models.Publishable",
        listed_by_default = False,
        member_group = "pages"
    )

    not_found_error_page = schema.Reference(
        type = "woost.models.Publishable",
        listed_by_default = False,
        member_group = "pages"
    )

    forbidden_error_page = schema.Reference(
        type = "woost.models.Publishable",
        listed_by_default = False,
        member_group = "pages"
    )

    site_name = schema.String(
        translated = True,
        member_group = "meta",
        listed_by_default = False
    )

    icon = schema.Reference(
        type = File,
        relation_constraints = [File.resource_type.equal("image")],
        related_end = schema.Collection(),
        listed_by_default = False,
        member_group = "meta"
    )

    logo = schema.Reference(
        type = File,
        relation_constraints = [File.resource_type.equal("image")],
        related_end = schema.Collection(),
        listed_by_default = False,
        member_group = "meta"
    )

    keywords = schema.String(
        translated = True,
        listed_by_default = False,
        edit_control = "cocktail.html.TextArea",
        member_group = "meta"
    )

    description = schema.String(
        translated = True,
        listed_by_default = False,
        edit_control = "cocktail.html.TextArea",
        member_group = "meta"
    )

    https_policy = schema.String(
        required = True,
        default = "never",
        enumeration = [
            "always",
            "never",
            "per_page",
        ],
        translate_value = lambda value, language = None, **kwargs:
            "" if not value 
               else translations(
                        "Site.https_policy-%s" % value, 
                        language,
                        **kwargs
                    ),
        listed_by_default = False,
        member_group = "system"
    )

    https_persistence = schema.Boolean(
        required = True,
        default = False,
        listed_by_default = False,
        member_group = "system"
    )

    smtp_host = schema.String(
        default = "localhost",
        listed_by_default = False,
        text_search = False,
        member_group = "system"
    )

    smtp_user = schema.String(
        listed_by_default = False,
        text_search = False,
        member_group = "system"
    )

    smtp_password = schema.String(
        listed_by_default = False,
        text_search = False,
        member_group = "system"
    )

    timezone = schema.String(
        required = False,
        format = re.compile(r'^["GMT"|"UTC"|"PST"|"MST"|"CST"|"EST"]{3}$|^[+-]\d{4}$'),
        text_search = False,
        member_group = "system"
    )

    triggers = schema.Collection(
        items = "woost.models.Trigger",
        bidirectional = True,
        integral = True
    )

    publication_schemes = schema.Collection(
        items = "woost.models.PublicationScheme",
        bidirectional = True,
        integral = True,
        min = 1
    )

    caching_policies = schema.Collection(
        items = schema.Reference(type = CachingPolicy),
        bidirectional = True,
        integral = True,
        related_end = schema.Reference()
    )

    def __translate__(self, language, **kwargs):
        return translations(self.__class__.__name__, language, **kwargs)
    
    def resolve_path(self, path):
        """Determines the publishable item that matches the indicated path.

        This method identifies a matching publishable item by trying each
        publication scheme defined by the site, in order. Once a scheme finds a
        matching item, the search concludes.
        
        See L{PublicationScheme.resolve_path} for more details on the resolution
        process.
 
        @param path: The path to evaluate; A list-like object describing a
            a path relative to the application's root.
        @type path: str list

        @return: A structure containing the matching item and its publication
            details. If no matching item can be found, None is returned
            instead.
        @rtype: L{PathResolution}
        """
        if not path:
            return PathResolution(None, self.home)
        else:
            for pubscheme in self.publication_schemes:
                resolution = pubscheme.resolve_path(path)
                if resolution is not None:
                    return resolution

    def get_path(self, publishable, language = None):
        """Determines the canonical path of the indicated item.
        
        This method queries each publication scheme defined by the site, in
        order. Once a scheme yields a matching path, the search concludes. That
        first match will be considered the item's canonical path.

        See L{PublicationScheme.get_path} for more details on how paths for
        publishable items are determined.

        @param publishable: The item to get the canonical path for.
        @type publishable: L{Publishable<woost.models.publishable.Publishable>}

        @param language: The language to get the path in (some schemes produce
            different canonical paths for the same content in different
            languages).
        @type language: str

        @return: The publication path for the indicated item, relative to the
            application's root. If none of the site's publication schemes can
            produce a suitable path for the item, None is returned instead.
        @rtype: unicode
        """
        # The path to the home page is always the application root
        if publishable is self.home:
            return ""

        for pubscheme in self.publication_schemes:
            path = pubscheme.get_path(publishable, language)
            if path is not None:
                return path

