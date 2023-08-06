#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""

class TwitterAPIError(Exception):
    """An exception raised if an error is reported by Twitter's REST API."""

    def __init__(self, response):
        Exception.__init__(self, response)
        self.response = response

