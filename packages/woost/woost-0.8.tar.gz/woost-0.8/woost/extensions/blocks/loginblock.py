#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail import schema
from woost.models import Publishable
from woost.extensions.blocks.block import Block


class LoginBlock(Block):

    instantiable = True
    view_class = "woost.extensions.blocks.LoginBlockView"

    login_target = schema.Reference(
        type = Publishable,
        related_end = schema.Collection(),
        member_group = "content"
    )

    def init_view(self, view):
        Block.init_view(self, view)
        if self.login_target is not None:
            view["action"] = self.login_target.get_uri()

