#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			February 2009
"""
from cocktail.modeling import classgetter, DictWrapper
import cherrypy
from cocktail.controllers import serve_file
from woost.models.rendering import require_rendering
from woost.controllers.publishablecontroller import PublishableController


class FileController(PublishableController):
    """A controller that serves the files managed by the CMS."""

    def _produce_content(self, disposition = "inline"):
        file = self.context["publishable"]
        
        if file.image_effects:
            file_path = require_rendering(file)        
        else:
            file_path = file.file_path
            
        return serve_file(
            file_path,
            name = file.file_name,
            content_type = file.mime_type,
            disposition = disposition)

