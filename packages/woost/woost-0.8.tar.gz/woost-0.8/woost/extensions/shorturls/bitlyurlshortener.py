#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from simplejson import loads
from urllib import urlopen, quote
from cocktail import schema
from woost.extensions.shorturls.urlshortener import (
    URLShortener,
    URLShortenerServiceError
)


class BitlyURLShortener(URLShortener):

    instantiable = True

    members_order = [
        "login",
        "api_key"
    ]

    login = schema.String(
        required = True        
    )

    api_key = schema.String(
        required = True,
        text_search = False,
        listed_by_default = False
    )

    def shorten_url(self, url):
        response = urlopen(
            "http://api.bitly.com/v3/shorten?"
            "login=%s"
            "&apiKey=%s"
            "&longUrl=%s"
            "&format=json"
            % (
                self.login,
                self.api_key,
                quote(url)
            )
        )
        status = response.getcode()
        body = response.read()

        if status < 200 or status > 299:
            raise URLShortenerServiceError(body)

        return loads(body)["data"]["url"]

