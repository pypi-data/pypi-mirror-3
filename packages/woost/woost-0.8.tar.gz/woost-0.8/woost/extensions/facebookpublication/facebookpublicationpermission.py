#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail import schema
from woost.models.permission import (
    ContentPermission,
    permission_doesnt_match_style
)
from woost.extensions.facebookpublication.facebookpublicationtarget \
    import FacebookPublicationTarget


class FacebookPublicationPermission(ContentPermission):

    instantiable = True

    publication_targets = schema.Collection(
        items = schema.Reference(type = FacebookPublicationTarget),
        related_end = schema.Collection(),
        edit_inline = True,
        after_member = "matching_items"
    )

    def match(self, target, publication_target = None, verbose = False):

        if not ContentPermission.match(self, target, verbose = verbose):
            return False

        if publication_target is not None \
        and self.publication_targets \
        and publication_target not in self.publication_targets:
            print permission_doesnt_match_style(
                "publication target doesn't match"
            ),

        return True

