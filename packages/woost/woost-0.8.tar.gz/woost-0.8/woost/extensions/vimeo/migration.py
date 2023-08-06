#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.persistence import MigrationStep

step = MigrationStep(
    "rename VimeoVideo.tags to VimeoVideo.vimeo_tags"
)

step.rename_member(
    "woost.extensions.vimeo.video.VimeoVideo",
    "tags",
    "vimeo_tags"
)

