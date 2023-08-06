#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""
import cherrypy
from cocktail.modeling import cached_getter
from cocktail.controllers.renderingengines import get_rendering_engine
from woost.controllers.publishablecontroller import PublishableController


class DocumentController(PublishableController):
    """A controller that serves rendered pages."""

    @cached_getter
    def page_template(self):
        template = self.context["publishable"].template

        if template is None:
            raise cherrypy.NotFound()

        return template

    @cached_getter
    def rendering_engine(self):
        engine_name = self.page_template.engine

        if engine_name:
            return get_rendering_engine(
                engine_name,
                cherrypy.request.config.get("rendering.engine_options")
            )
        else:
            return PublishableController.rendering_engine(self)

    @cached_getter
    def view_class(self):
        return self.page_template.identifier

