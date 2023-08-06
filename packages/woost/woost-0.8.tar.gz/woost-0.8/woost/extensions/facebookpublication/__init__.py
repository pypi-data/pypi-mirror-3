#-*- coding: utf-8 -*-
u"""Defines the `FacebookPublicationExtension` class.

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.translations import translations
from cocktail import schema
from woost.models import Extension


translations.define("FacebookPublicationExtension",
    ca = u"Publicació a Facebook",
    es = u"Publicación en Facebook",
    en = u"Publish to Facebook"
)

translations.define("FacebookPublicationExtension-plural",
    ca = u"Publicació a Facebook",
    es = u"Publicación en Facebook",
    en = u"Publish to Facebook"
)


class FacebookPublicationExtension(Extension):

    def __init__(self, **values):
        Extension.__init__(self, **values)
        self.extension_author = u"Whads/Accent SL"
        self.set("description",
            u"""Simplifica la publicació de continguts del lloc web al Facebook""",
            "ca"
        )
        self.set("description",            
            u"""Simplifica la publicación de contenidos del sitio web en
            Facebook""",
            "es"
        )
        self.set("description",
            u"""Makes it easy to publish content from the website to Facebook""",
            "en"
        )

    def _load(self):
        
        from woost.extensions.facebookpublication import (
            strings,
            fbpublishuseraction,
            fbpublishauthuseraction,
            facebookpublicationpermission
        )
        
        from woost.extensions.facebookpublication.facebookpublicationtarget \
            import FacebookPublicationTarget

        FacebookPublicationExtension.add_member(
            schema.Collection("targets",
                items = schema.Reference(type = FacebookPublicationTarget),
                integral = True,
                bidirectional = True,
                related_end = schema.Collection()
            )
        )

        from woost.controllers.backoffice.backofficecontroller \
            import BackOfficeController

        from woost.extensions.facebookpublication.facebookpublicationcontroller \
            import FacebookPublicationController

        BackOfficeController.fbpublish = FacebookPublicationController

        from woost.extensions.facebookpublication.facebookalbumscontroller \
            import FacebookAlbumsController

        BackOfficeController.fbpublish_albums = FacebookAlbumsController

