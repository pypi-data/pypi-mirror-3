#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.events import when
from cocktail.persistence import MigrationStep

step = MigrationStep(
    "rename Block.Container_blocks to Block.containers"
)

step.rename_member(
    "woost.extensions.blocks.block.Block",
    "Container_blocks",
    "containers"
)

