#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Jordi Fernández <jordi.fernandez@whads.com>
"""
import cherrypy
from cocktail.controllers import request_property
from woost.controllers.publishablecontroller import PublishableController
from woost.extensions.shop.basket import Basket


class ProductController(PublishableController):
    """A controller that serves rendered pages."""

    @request_property
    def view_class(self):
        view_class = self.context["publishable"].view_class

        if view_class is None:
            raise cherrypy.NotFound()

        return view_class

    @request_property
    def output(self):
        output = PublishableController.output(self)
        output["shop_order"] = Basket.get()
        return output

