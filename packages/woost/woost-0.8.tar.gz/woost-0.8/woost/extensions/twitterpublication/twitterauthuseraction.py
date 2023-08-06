#-*- coding: utf-8 -*-
u"""Declares a user action for granting access to a Twitter account.

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from oauth2 import Client, Consumer, Token
import cherrypy
from urllib import urlopen, quote_plus
from urlparse import parse_qsl
from simplejson import loads
from cocktail.persistence import datastore
from cocktail.translations import translations
from cocktail.controllers import Location, session
from woost.controllers.notifications import notify_user
from woost.controllers.backoffice.useractions import UserAction
from woost.extensions.twitterpublication.exceptions import TwitterAPIError
from woost.extensions.twitterpublication.twitterpublicationtarget \
    import TwitterPublicationTarget


class TwitterAuthUserAction(UserAction):
 
    content_type = TwitterPublicationTarget

    included = frozenset(["item_buttons"])
    excluded = frozenset(["new_item"])
    min = 1
    max = 1

    def invoke(self, controller, selection):
        
        target = selection[0]
        consumer = Consumer(target.app_id, target.app_secret)

        def request(client, *args, **kwargs):
            response, body = client.request(*args, **kwargs)
            if response["status"] != "200":
                raise TwitterAPIError(body)
            return body

        try:
            oauth_token = cherrypy.request.params.get("oauth_token")
            oauth_verifier = cherrypy.request.params.get("oauth_verifier")
            oauth_secret_session_key = "twitter_auth.%s.oauth_secret" % self.id

            if not oauth_token or not oauth_verifier:
                # Obtain a request token
                client = Client(consumer)

                location = Location.get_current(relative = False)
                location.query_string["item_action"] = self.id
                callback = quote_plus(str(location))

                body = request(
                    client,
                    "https://api.twitter.com/oauth/request_token"
                    "?oauth_callback=" + callback,
                    "GET"
                )
                data = dict(parse_qsl(body))
                session[oauth_secret_session_key] = data["oauth_token_secret"]

                # Redirect the user to the login form
                auth_url = (
                    "https://api.twitter.com/oauth/authorize?"
                    "oauth_token=%s"
                    "&oauth_callback=%s"
                    % (data["oauth_token"], callback)
                )
                raise cherrypy.HTTPRedirect(auth_url)
            else:
                token = Token(oauth_token, session[oauth_secret_session_key])
                token.set_verifier(oauth_verifier)
                client = Client(consumer, token)
                body = request(
                    client,
                    'https://api.twitter.com/oauth/access_token',
                    "POST"
                )
                data = dict(parse_qsl(body))
                target.auth_token = data["oauth_token"]
                target.auth_secret = data["oauth_token_secret"]
                datastore.commit()

        except TwitterAPIError, ex:
            notify_user(
                translations(ex),
                category = "error",
                transient = False
            )
        else:
            notify_user(
                translations(
                    "woost.extensions.twitterpublication."
                    "successful_authorization_notice"
                ),
                category = "success"
            )

TwitterAuthUserAction("twitter_auth").register()

