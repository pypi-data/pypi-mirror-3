#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			February 2010
"""
from cocktail.translations import translations
from woost.models import Extension

translations.define("SitemapExtension",
    ca = u"Refinament de l'indexat web",
    es = u"Refinamiento del indexado web",
    en = u"Web crawler hints"
)

translations.define("SitemapExtension-plural",
    ca = u"Refinament de l'indexat web",
    es = u"Refinamiento del indexado web",
    en = u"Web crawler hints"
)


class SitemapExtension(Extension):

    def __init__(self, **values):
        Extension.__init__(self, **values)
        self.extension_author = u"Whads/Accent SL"
        self.set("description",
            u"""Genera un mapa de documents per optimitzar l'indexat del lloc
            web, seguint l'estàndard sitemap.org.""",
            "ca"
        )
        self.set("description",            
            u"""Genera un mapa de documentos para optimizar el indexado del
            sitio, siguiendo el estándard sitemap.org.""",
            "es"
        )
        self.set("description",
            u"""Generates a document map to optimize the indexing of the site
            by web crawlers, following the sitemap.org standard.""",
            "en"
        )

    def _load(self):
        from woost.extensions.sitemap import publishable, strings
        self.install()

    def _install():
        
        from woost.models import (
            Site,
            Publishable,
            Document,
            Controller,
            extension_translations
        )
        
        # Sitemap controller
        sitemap_controller = self._create_asset(
            Controller,
            "sitemap_controller",
            title = extension_translations,
            python_name =
                "woost.extensions.sitemap.sitemapcontroller.SitemapController"
        )

        # Sitemap document
        sitemap_doc = self._create_asset(
            Document,
            "sitemap_document",
            title = extension_translations,
            parent = Site.main.home,
            path = "sitemap_xml",
            per_language_publication = False,
            mime_type = "text/xml",
            hidden = True,
            sitemap_indexable = False,
            controller = sitemap_controller
        )

        # Force indexing of the 'sitemap_indexable' member
        # (can't rely on defaults when executing queries)
        for item in Publishable.select():
            if not hasattr(item, "_sitemap_indexable"):
                item.sitemap_indexable = \
                    item.sitemap_indexable and not item.hidden

