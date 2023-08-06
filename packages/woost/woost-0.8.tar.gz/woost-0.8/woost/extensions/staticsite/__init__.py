#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			December 2009
"""
from cocktail.events import when
from cocktail import schema
from cocktail.translations import translations
from cocktail.controllers import context
from woost.models import Extension


translations.define("StaticSiteExtension",
    ca = u"Lloc web estàtic",
    es = u"Sitio web estático",
    en = u"Static website"
)

translations.define("StaticSiteExtension-plural",
    ca = u"Lloc web estàtic",
    es = u"Sitio web estático",
    en = u"Static website"
)

translations.define("StaticSiteExtension.file_extension",
    ca = u"Extensió de fitxer",
    es = u"Extensión de fichero",
    en = u"File extension"
)


class StaticSiteExtension(Extension):

    def __init__(self, **values):
        Extension.__init__(self, **values)
        self.extension_author = u"Whads/Accent SL"
        self.set("description",
            u"""Permet exportar una versió estàtica del lloc web.""",
            "ca"
        )
        self.set("description",            
            u"""Permite exportar una versión estática del sitio web.""",
            "es"
        )
        self.set("description",
            u"""Exports the site using static HTML pages.""",
            "en"
        )

    def _load(self):

        from woost.controllers.backoffice.backofficecontroller \
            import BackOfficeController

        from woost.extensions.staticsite import (
            useraction,
            strings,
            staticsitesnapshoter,
            exportationpermission,
            exportstaticsitecontroller 
        )

        from woost.extensions.staticsite.staticsitesnapshoter \
            import StaticSiteSnapShoter
        from woost.extensions.staticsite.staticsitedestination \
            import StaticSiteDestination

        BackOfficeController.export_static = \
            exportstaticsitecontroller.ExportStaticSiteController
    
        StaticSiteExtension.add_member(
            schema.Collection(
                "snapshoters",
                items = schema.Reference(
                    type = StaticSiteSnapShoter,                    
                ),
                bidirectional = True,
                integral = True,
                related_end = schema.Reference(),
                min = 1
            )
        )

        StaticSiteExtension.add_member(
            schema.Collection(
                "destinations",
                items = schema.Reference(
                    type = StaticSiteDestination,                    
                ),
                bidirectional = True,
                integral = True,
                related_end = schema.Reference(),
                min = 1
            )
        )

        # Disable interactive features from rendered pages when rendering
        # static content
        from woost.controllers.cmscontroller import CMSController
    
        @when(CMSController.producing_output)
        def disable_user_controls(event):
            if context.get("exporting_static_site", False):
                event.output["show_user_controls"] = False

