#-*- coding: utf-8 -*-
u"""

@author:		Javier Marrero
@contact:		javier.marrero@whads.com
@organization:	Whads/Accent SL
@since:			May 2010
"""

import cherrypy
from woost.controllers import BaseCMSController

class FirstChildRedirectionController(BaseCMSController):

    def __call__(self, *args, **kwargs):

        publishable = self.context["publishable"]

        if hasattr(publishable,"children"):

            for child in publishable.children:
                if child.is_accessible():
                    uri = self.context["cms"].uri(child)
                    raise cherrypy.HTTPRedirect(uri)

        raise cherrypy.HTTPError(404)
