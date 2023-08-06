#-*- coding: utf-8 -*-
u"""Defines the `URLShortener` model.

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.modeling import abstractmethod
from cocktail import schema
from woost.models import Item


class URLShortener(Item):
    """Base model for all URL shortening services."""

    visible_from_root = False
    instantiable = False

    title = schema.String(
        required = True,
        unique = True,
        indexed = True,
        normalized_index = True,
        descriptive = True
    )

    @abstractmethod
    def shorten_url(self, url):
        pass


class URLShortenerServiceError(Exception):
    """An exception raised if an error is reported during a request to an URL
    shortening service.
    """

    def __init__(self, response):
        Exception.__init__(self, response)
        self.response = response

