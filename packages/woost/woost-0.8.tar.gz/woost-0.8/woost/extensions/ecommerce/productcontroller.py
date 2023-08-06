#-*- coding: utf-8 -*-
u"""Defines the `ProductController` class.

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import cherrypy
from cocktail.translations import translations
from cocktail.controllers import request_property, Location
from cocktail.controllers.formprocessor import FormProcessor, Form
from woost.models import Publishable
from woost.controllers.notifications import notify_user
from woost.controllers.documentcontroller import DocumentController
from woost.extensions.ecommerce.ecommerceproduct import ECommerceProduct
from woost.extensions.ecommerce.ecommercepurchase import ECommercePurchase
from woost.extensions.ecommerce.basket import Basket


class ProductController(FormProcessor, DocumentController):

    class AddProductForm(Form):

        actions = ("add_product",)
        redirect_to_basket = False

        @request_property
        def product(self):
            return self.controller.context["publishable"]

        @request_property
        def model(self):
            return self.product.purchase_model

        @request_property
        def adapter(self):
            
            adapter = Form.adapter(self)
            adapter.implicit_copy = False

            for member in self.model.get_options():
                adapter.copy(member.name)

            return adapter

        def create_instance(self):
            instance = Form.create_instance(self)
            instance.product = self.product
            return instance

        def submit(self):
            Form.submit(self)
            Basket.get().add_purchase(self.instance)
            Basket.store()

            notify_user(
                translations(
                    "woost.extensions.ecommerce.product_added_notice",
                    product = self.product
                ),
                "product_added",
                transient = False
            )

            if self.redirect_to_basket:
                raise cherrypy.HTTPRedirect(
                    Publishable.require_instance(
                        qname = "woost.extensions.ecommerce.basket_page"
                    ).get_uri()
                )
            else:
                Location.get_current().go("GET")

