#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Jordi Fernández <jordi.fernandez@whads.com>
"""
from cocktail.translations import translations
from cocktail.persistence import datastore
from cocktail.html import templates
from woost.models import Extension


translations.define("BlocksExtension",
    ca = u"Blocs de contingut",
    es = u"Bloques de contenido",
    en = u"Content blocks"
)

translations.define("BlocksExtension-plural",
    ca = u"Blocs de contingut",
    es = u"Bloques de contenido",
    en = u"Content blocks"
)


class BlocksExtension(Extension):

    def __init__(self, **values):
        Extension.__init__(self, **values)
        self.extension_author = u"Whads/Accent SL"
        self.set("description",
            u"""Permet la creació de contingut utilitzant blocs""",
            "ca"
        )
        self.set("description",            
            u"""Permite la creación de contenido usando bloques""",
            "es"
        )
        self.set("description",
            u"""Allows the creation of content using blocs""",
            "en"
        )

    def _load(self):

        from woost.extensions.blocks import (
            strings, 
            block, 
            containerblock,
            slideshowblock,
            imagegalleryblock,
            bannerblock,
            menublock,
            richtextblock,
            translatedrichtextblock,
            twittertimelineblock,
            linksblock,
            folderblock,
            loginblock,
            iframeblock,
            blockspage,
            migration
        )

        from woost.extensions.vimeo import VimeoExtension

        if VimeoExtension.instance.enabled:
            from woost.extensions.blocks import vimeoblock

        # Install an overlay for the frontend edit panel
        templates.get_class("woost.extensions.blocks.EditPanelOverlay")

        self.install()

    def _install(self):
        from woost.models import Template, extension_translations

        self._create_asset(
            Template,
            "blocks_page_template",
            title = extension_translations,
            engine = "cocktail",
            identifier = "woost.extensions.blocks.BlocksPageView"
        )

