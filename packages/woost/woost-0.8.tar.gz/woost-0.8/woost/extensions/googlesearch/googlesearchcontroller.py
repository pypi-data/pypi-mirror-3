#-*- coding: utf-8 -*-
"""

@author:		Marc Pérez
@contact:		marc.perez@whads.com
@organization:	Whads/Accent SL
@since:			December 2009
"""
import cherrypy
from cocktail.modeling import cached_getter
from woost.controllers.documentcontroller import DocumentController
from woost.extensions.googlesearch import GoogleSearchExtension


class GoogleSearchController(DocumentController):

    @cached_getter
    def output(self):
        query = cherrypy.request.params.get("query") or u""
        page = cherrypy.request.params.get("page") or 0
        results = GoogleSearchExtension.instance.search(query, int(page))

        output = DocumentController.output(self)
        output["query"] = query
        output["results"] = results
        return output

