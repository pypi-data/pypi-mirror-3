#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail import schema
from woost.extensions.blocks.block import Block


class TwitterTimelineBlock(Block):

    instantiable = True
    view_class = "cocktail.html.TwitterTimeline"

    members_order = [
        "account",
        "max_tweets"
    ]

    account = schema.String(
        required = True,
        member_group = "content"
    )

    max_tweets = schema.Integer(
        required = True,
        default = 5,
        min = 1,
        max = 20,
        member_group = "content"
    )

    def init_view(self, view):
        Block.init_view(self, view)
        view.account = self.account
        view.max_tweets = self.max_tweets

