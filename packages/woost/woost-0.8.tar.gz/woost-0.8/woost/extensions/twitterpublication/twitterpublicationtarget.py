#-*- coding: utf-8 -*-
u"""Defines the `TwitterPublicationTarget`.

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from string import whitespace
from oauth2 import Client, Consumer, Token
from urllib import urlencode, urlopen
from simplejson import loads
from cocktail.events import when
from cocktail.iteration import first
from cocktail.translations import translations
from cocktail import schema
from woost.models import Item, Language
from woost.extensions.shorturls import ShortURLsExtension
from woost.extensions.shorturls.urlshortener import URLShortener
from woost.extensions.twitterpublication.exceptions import TwitterAPIError


class TwitterPublicationTarget(Item):

    visible_from_root = False

    tweet_max_length = 140

    members_order = [
        "title",
        "account",
        "app_id",
        "app_secret",
        "auth_token",
        "auth_secret",
        "languages"
    ]

    title = schema.String(
        required = True,
        unique = True,
        indexed = True,
        normalized_index = True,
        descriptive = True
    )

    account = schema.String(
        required = True
    )

    app_id = schema.String(
        required = True,
        text_search = False,
        listed_by_default = False
    )

    app_secret = schema.String(
        required = True,
        text_search = False,
        listed_by_default = False
    )

    auth_token = schema.String(
        editable = False,
        text_search = False,
        translate_value = lambda value, language = None, **kwargs:
            translations(
                "TwitterPublicationTarget.auth_token-%s"
                % ("conceded" if value else "pending"),
                language,
                **kwargs
            )
    )

    auth_secret = schema.String(
        visible = False
    )

    languages = schema.Collection(
        items = schema.String(
            enumeration = lambda ctx: Language.codes,
            translate_value = lambda value, language = None, **kwargs:
                "" if not value else translations(value)
        )
    )

    url_shortener = None

    def publish(self, publishable):
        
        if self.auth_token is None:
            raise ValueError(
                "Can't publish %s to %s: authorization token missing"
                % (publishable, self)
            )

        if self.auth_secret is None:
            raise ValueError(
                "Can't publish %s to %s: authorization secret missing"
                % (publishable, self)
            )

        consumer = Consumer(self.app_id, self.app_secret)
        token = Token(self.auth_token, self.auth_secret)
        client = Client(consumer, token)
        status = self.get_status(publishable)

        response, body = client.request(
            "https://api.twitter.com/1/statuses/update.json",
            "POST",
            urlencode({"status": status.encode("utf-8")})
        )

        if response["status"] != "200":
            raise TwitterAPIError(body)

    def find_post(self, publishable):
        
        query = "from:%s %s" % (self.account, self.get_uri(publishable))

        response = urlopen(
            "http://search.twitter.com/search.json?" + urlencode({
                "q": query,
                "result_type": "mixed"
            })
        )
        status = response.getcode()
        body = response.read()

        if status != 200:
            raise TwitterAPIError(body)
        
        posts = loads(body)["results"]
        return posts and posts[0] or None

    def get_status(self, publishable):
        uri = self.get_uri(publishable)
        title = self.get_title(publishable)
        title = self.trim(title, self.tweet_max_length - 1 - len(uri))
        return u"%s %s" % (title, uri)

    def get_title(self, publishable):
        return translations(publishable)

    def get_uri(self, publishable, *args, **kwargs):
        
        kwargs.setdefault("host", ".")
        url = publishable.get_uri(*args, **kwargs)
        
        if self.url_shortener:
            url = self.url_shortener.shorten_url(url)

        return url

    def trim(self, text, max_length, ellipsis = "..."):

        if len(text) > max_length:
            for i in range(max_length - len(ellipsis) - 1, -1, -1):
                print i, repr(text)
                if text[i] in whitespace:
                    text = text[:i].rstrip() + ellipsis
                    break

        return text


# If the 'shorturls' extension is enabled, add a member to define an URL
# shortening service for this target
@when(ShortURLsExtension.loading)
def add_url_shortener_reference(e):
    if e.source.enabled:
        TwitterPublicationTarget.add_member(
            schema.Reference("url_shortener",
                shadows_attribute = True,
                type = URLShortener,
                related_end = schema.Collection(),
                listed_by_default = False,
                
                # Default to the first defined service, if one exists
                default = schema.DynamicDefault(
                    lambda: first(URLShortener.select())
                )
            )
        )

