#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.translations import translations
from cocktail import schema
from woost.models import Extension


translations.define("TwitterPublicationExtension",
    ca = u"Publicació a Twitter",
    es = u"Publicación en Twitter",
    en = u"Publish to Twitter"
)

translations.define("TwitterPublicationExtension-plural",
    ca = u"Publicació a Twitter",
    es = u"Publicación en Twitter",
    en = u"Publish to Twitter"
)


class TwitterPublicationExtension(Extension):

    def __init__(self, **values):
        Extension.__init__(self, **values)
        self.extension_author = u"Whads/Accent SL"
        self.set("description",
            u"""Publica continguts del lloc web al Twitter""",
            "ca"
        )
        self.set("description",            
            u"""Publica contenidos del sitio web en Twitter""",
            "es"
        )
        self.set("description",
            u"""Publish content from the website to Twitter""",
            "en"
        )

    def _load(self):
        
        from woost.extensions.twitterpublication import (
            strings,
            tweetuseraction,
            twitterauthuseraction,
            tweetpermission
        )
        
        from woost.extensions.twitterpublication.twitterpublicationtarget \
            import TwitterPublicationTarget

        TwitterPublicationExtension.add_member(
            schema.Collection("targets",
                items = schema.Reference(type = TwitterPublicationTarget),
                integral = True,
                bidirectional = True,
                related_end = schema.Collection()
            )
        )

        from woost.controllers.backoffice.backofficecontroller \
            import BackOfficeController
        from woost.extensions.twitterpublication.tweetcontroller \
            import TweetController

        BackOfficeController.tweet = TweetController

        self.install()

    def _install(self):

        from woost.models import Role
        from woost.extensions.twitterpublication.tweetpermission \
            import TweetPermission
        
        # By default, only administrator users can tweet content
        permission = TweetPermission()
        permission.matching_items = {
            "type": "woost.models.publishable.Publishable"
        }
        permission.insert()
        
        admins = Role.require_instance(qname = "woost.administrators")
        admins.permissions.append(permission)

