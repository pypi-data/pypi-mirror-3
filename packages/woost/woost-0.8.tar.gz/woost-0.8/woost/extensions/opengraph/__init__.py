#-*- coding: utf-8 -*-
u"""An extension that improves the integration with Facebook of documents
published with Woost.

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.translations import translations
from cocktail import schema
from cocktail.html import templates
from cocktail.persistence import datastore
from woost.models import Site, Extension, File


translations.define("OpenGraphExtension",
    ca = u"OpenGraph",
    es = u"OpenGraph",
    en = u"OpenGraph"
)

translations.define("OpenGraphExtension-plural",
    ca = u"OpenGraph",
    es = u"OpenGraph",
    en = u"OpenGraph"
)

translations.define("OpenGraphExtension.open_graph",
    ca = u"Integració amb OpenGraph/Facebook",
    es = u"Integración con OpenGraph/Facebook",
    en = u"OpenGraph/Facebook integration"
)

translations.define("OpenGraphExtension.facebook_administrators",
    ca = u"Comptes de Facebook dels administradors",
    es = u"Cuentas de Facebook de los administradores",
    en = u"Facebook administrator accounts"
)

translations.define("OpenGraphExtension.facebook_applications",
    ca = u"Comptes d'aplicació de Facebook",
    es = u"Cuentas de aplicación de Facebook",
    en = u"Facebook application accounts"
)


class OpenGraphExtension(Extension):

    members_order = [
        "facebook_administrators",
        "facebook_applications"
    ]

    facebook_administrators = schema.String(
        listed_by_default = False,
        searchable = False,
        member_group = "open_graph"
    )

    facebook_applications = schema.String(
        listed_by_default = False,
        searchable = False,
        member_group = "open_graph"
    )

    def __init__(self, **values):
        Extension.__init__(self, **values)
        self.extension_author = u"Whads/Accent SL"
        self.set("description",
            u"""Millora la integració dels documents del lloc web amb Facebook
            i altres serveis que implementin el protocol OpenGraph""",
            "ca"
        )
        self.set("description",            
            u"""Mejora la integración de los documentos del sitio web con
            Facebook y otros servicios que utilicen el protocolo OpenGraph""",
            "es"
        )
        self.set("description",
            u"""Improves the integration of the site's documents with Facebook
            and any other service that makes use of the OpenGraph protocol""",
            "en"
        )

    def _load(self):

        from woost.extensions.opengraph import (
            strings, 
            publishable,
            opengraphtype,
            opengraphcategory
        )

        OpenGraphExtension.add_member(
            schema.Collection("categories",
                items = schema.Reference(
                    type = opengraphcategory.OpenGraphCategory
                ),
                related_end = schema.Collection(),
                member_group = "open_graph"
            )
        )

        # Install an overlay to BaseView to automatically add OpenGraph
        # metadata to HTML documents
        templates.get_class("woost.extensions.opengraph.BaseViewOverlay")

        self.install()
        
    def _install(self):
        self.create_default_categories(verbose = True)

    def create_default_categories(self, verbose = False):
        
        from woost.extensions.opengraph.opengraphtype import OpenGraphType
        from woost.extensions.opengraph.opengraphcategory \
            import OpenGraphCategory

        for category_id, type_ids in (
            ("activities", (
                "activity",
                "sport"
            )),
            ("businesses", (
                "bar",
                "company",
                "cafe",
                "hotel",
                "restaurant"
            )),
            ("groups", (
                "cause",
                "sports_league",
                "sports_team"
            )),
            ("organizations", (
                "band",
                "government",
                "non_profit",
                "school",
                "university"
            )),
            ("people", (
                "actor",
                "athlete",
                "author",
                "director",
                "musician",
                "politician",
                "profile",
                "public_figure"
            )),
            ("places", (
                "city",
                "country",
                "landmark",
                "state_province"
            )),
            ("products_and_entertainment", (
                "album",
                "book",
                "drink",
                "food",
                "game",
                "movie",
                "product",
                "song",
                "tv_show"
            )),
            ("websites", (
                "article",
                "blog",
                "website"
            ))
        ):
            # Create the category
            og_category = OpenGraphCategory.get_instance(code = category_id)

            if og_category is None:
                
                if verbose:
                    print "Creating OpenGraph category '%s'" % category_id

                og_category = OpenGraphCategory()
                og_category.code = category_id
                og_category.insert()
                
                key = "opengraph.categories." + category_id
                
                for language in translations:
                    label = translations(key, language)
                    if label:
                        og_category.set("title", label, language)

            # Create all types in the category
            types = []

            for type_id in type_ids:
                og_type = OpenGraphType.get_instance(code = type_id)

                if og_type is None:
                    
                    if verbose:
                        print "Creating OpenGraph type '%s.%s'" % (
                            category_id,
                            type_id
                        )

                    og_type = OpenGraphType()
                    og_type.code = type_id
                    og_type.insert()
                    
                    key = "opengraph.types." + type_id

                    for language in translations:
                        label = translations(key, language)
                        if label:
                            og_type.set("title", label, language)

                types.append(og_type)

            og_category.types = types

    def get_global_properties(self):

        site = Site.main

        properties = {}

        if site.site_name:
            properties["og:site_name"] = site.site_name

        if site.logo:
            properties["og:image"] = site.logo.get_uri(host = ".")

        if site.email:
            properties["og:email"] = site.email

        if site.phone_number:
            properties["og:phone_number"] = site.phone_number

        if site.fax_number:
            properties["og:fax_number"] = site.fax_number

        if site.address:
            properties["og:street-address"] = site.address

        if site.town:
            properties["og:locality"] = site.town

        if site.region:
            properties["og:region"] = site.region

        if site.postal_code:
            properties["og:postal-code"] = site.postal_code

        if site.country:
            properties["og:country-name"] = site.country

        if self.facebook_administrators:
            properties["fb:admins"] = self.facebook_administrators

        if self.facebook_applications:
            properties["fb:app_id"] = self.facebook_applications

        return properties

    def get_properties(self, publishable):
        properties = self.get_global_properties()
        properties.update(publishable.get_open_graph_properties())
        return properties

