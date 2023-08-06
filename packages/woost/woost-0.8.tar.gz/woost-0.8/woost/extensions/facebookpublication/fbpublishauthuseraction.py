#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import cherrypy
from urllib import urlopen, quote_plus
from simplejson import loads
from cocktail.persistence import datastore
from cocktail.translations import translations
from cocktail.controllers import Location
from woost.controllers.notifications import notify_user
from woost.controllers.backoffice.useractions import UserAction
from woost.extensions.facebookpublication.facebookpublicationtarget \
    import FacebookPublicationTarget


class FBPublishAuthUserAction(UserAction):
 
    content_type = FacebookPublicationTarget

    included = frozenset(["item_buttons"])
    excluded = frozenset(["new_item"])
    min = 1
    max = 1

    def invoke(self, controller, selection):
        
        publication_target = selection[0]
        code = cherrypy.request.params.get("code")
        error = cherrypy.request.params.get("error")
        error_reason = cherrypy.request.params.get("error_reason")
        error_description = cherrypy.request.params.get("error_description")

        # Authorization failed
        if error:
            notify_user(
                translations(
                    "woost.extensions.facebookauthentication."
                    "fbpublish_auth.error",
                ),
                category = "error",
                transient = False
            )

        # Authorization successful
        elif code:
            location = Location.get_current(relative = False)
            del location.query_string["code"]

            auth_url = (
                "https://graph.facebook.com/oauth/access_token?"
                "client_id=%s"
                "&redirect_uri=%s"
                "&client_secret=%s"
                "&code=%s"
                % (
                    publication_target.app_id,
                    quote_plus(str(location)),
                    publication_target.app_secret,
                    code
                )
            )
            response = urlopen(auth_url)
            response_status = response.getcode()
            response_body = response.read()

            if response_status < 200 or response_status > 299:
                notify_user(
                    translations(
                        "woost.extensions.facebookauthentication."
                        "fbpublish_auth.oauth_error",
                        response = response_body
                    ),
                    category = "error",
                    transient = False
                )
                return

            auth_token = response_body.split("&")[0].split("=")[1]

            # Facebook pages require an additional authentication step
            fb_page_id = cherrypy.request.params.get("fb_page")

            if fb_page_id:
                accounts_url = (
                    "https://graph.facebook.com/%s/accounts?access_token=%s"
                    % (publication_target.administrator_id, auth_token)
                )
                response_data = urlopen(accounts_url).read()
                json = loads(response_data)

                for account in json["data"]:
                    if account["id"] == fb_page_id:
                        auth_token = account["access_token"]
                        break
                else:
                    auth_token = None

            publication_target.auth_token = auth_token
            datastore.commit()

            notify_user(
                translations(
                    "woost.extensions.facebookauthentication."
                    "fbpublish_auth.success"
                ),
                category = "success"
            )

        # Begin authorization request
        else:
            # Determine if the selected graph URL is a Facebook Page
            graph_url = "http://graph.facebook.com/%s?metadata=1" \
                      % publication_target.graph_object_id
            response_data = urlopen(graph_url).read()
            json = loads(response_data)
            fb_page_id = json["type"] == "page" and json["id"]
            
            location = Location.get_current(relative = False)
            location.query_string["item_action"] = self.id

            permissions = "publish_stream,offline_access,user_photos"

            if fb_page_id:
                location.query_string["fb_page"] = fb_page_id
                permissions += ",manage_pages"

            auth_url = (
                "https://www.facebook.com/dialog/oauth?"
                "client_id=%s"
                "&redirect_uri=%s"
                "&scope=%s"
                % (
                    publication_target.app_id,
                    quote_plus(str(location)),
                    permissions
                )
            )
            raise cherrypy.HTTPRedirect(auth_url)

FBPublishAuthUserAction("fbpublish_auth").register()

