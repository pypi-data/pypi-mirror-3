#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail import schema
from woost.extensions.blocks.containerblock import ContainerBlock


class SlideShowBlock(ContainerBlock):

    instantiable = True
    view_class = "cocktail.html.SlideShow"

    groups_order = ["content", "transition_settings"]

    members_order = [
        "autoplay",
        "interval",
        "transition_duration",
        "navigation_controls"
    ]
    
    autoplay = schema.Boolean(
        required = True,
        default = True,
        member_group = "transition_settings"
    )

    interval = schema.Integer(
        required = autoplay,
        default = 3000,
        min = 0,
        member_group = "transition_settings"
    )

    transition_duration = schema.Integer(
        required = True,
        default = 500,
        min = 0,
        member_group = "transition_settings"
    )

    navigation_controls = schema.Boolean(
        required = True,
        default = False,
        member_group = "content"
    )

    def init_view(self, view):
        ContainerBlock.init_view(self, view)
        view.block_content = view.slides
        view.autoplay = self.autoplay
        view.interval = self.interval
        view.transition_duration = self.transition_duration
        view.navigation_controls = self.navigation_controls

