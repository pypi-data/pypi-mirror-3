#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			December 2008
"""
from urllib import urlencode
import cherrypy
from cocktail.modeling import getter
from cocktail.events import event_handler
from cocktail.controllers import Controller
from woost.models import Site


class BaseCMSController(Controller):
    """Base class for all CMS controllers."""

    def _render_template(self):

        # Pass the request context to the template
        cms = self.context["cms"]
        cms.producing_output(
            controller = self,
            output = self.output
        )

        return Controller._render_template(self)
 
    def application_uri(self, *args, **kwargs):
        """Builds an absolute URI from a set of path components and parameters.
        
        @param args: A set of path components, relative to the application
            root. Takes any object that can be expressed as an unicode string.

        @param kwargs: A set of query string parameters to be included on the
            generated URI.
        
        @return: The generated absolute URI.
        @rtype: unicode
        """
        path = (unicode(arg).strip("/") for arg in args)
        uri = (
            self.context["cms"].virtual_path
            + u"/".join(component for component in path if component)
        )

        if kwargs:
            uri += "?" + urlencode(
                dict(
                    (key, value)
                    for key, value in kwargs.iteritems()
                    if not value is None
                ),
                True
            )

        # Contextual URI prefix
        context_prefix = self.context.get("uri_prefix")

        if context_prefix:
            uri = context_prefix.rstrip("/") + "/" + uri.lstrip("/")

        if uri.startswith("./"):
            uri = uri[2:]

        return uri

    def contextual_uri(self, *args, **kwargs):
        """Builds an URI relative to the currently requested publishable item.
        
        @param args: A set of path components that will be appended to the
            publishable's URI. Accepts any object that can be expressed as an
            unicode string.

        @param kwargs: A set of query string parameters to be included on the
            generated URI.
        
        @return: The generated absolute URI.
        @rtype: unicode
        """
        publishable = self.context["publishable"]
        uri = Site.main.get_path(publishable)

        if uri is None:
            return None
        
        return self.application_uri(
            uri,
            *args,
            **kwargs
        )

