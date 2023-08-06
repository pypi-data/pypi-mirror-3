#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.translations import translations
from cocktail import schema
from cocktail.events import event_handler
from cocktail.controllers import (
    request_property,
    get_state,
    get_parameter,
    Pagination,
    session
)
from cocktail.controllers.formprocessor import Form
from woost.models import Publishable
from woost.extensions.ecommerce.ecommerceproduct import ECommerceProduct
from woost.extensions.ecommerce.productcontroller import ProductController

SESSION_KEY = "woost.extensions.ecommerce.catalog_state"

def catalog_current_state_uri():
    state = session.get(SESSION_KEY) or {}
    catalog = Publishable.require_instance(
        qname = "woost.extensions.ecommerce.catalog_page"
    )
    return catalog.get_uri(parameters = state)


class CatalogController(ProductController):

    @event_handler
    def handle_before_request(cls, event):
        session[SESSION_KEY] = get_state()

    class AddProductForm(ProductController.AddProductForm):

        @request_property
        def product(self):
            return get_parameter(
                schema.Reference(
                    "product", 
                    type = ECommerceProduct, 
                    required = True
                )
            )

        @request_property
        def model(self):
            return self.product \
                and self.product.purchase_model \
                or Form.model(self)

        @request_property
        def adapter(self):
            return self.product \
                and ProductController.AddProductForm.adapter(self) \
                or Form.adapter(self)

        def create_instance(self):
            return self.product \
                and ProductController.AddProductForm.create_instance(self) \
                or Form.create_instance(self)

    @request_property
    def products(self):
        return ECommerceProduct.select_accessible(order = [
            schema.expressions.CustomExpression(translations)
        ])

    @request_property
    def pagination(self):
        return get_parameter(
            Pagination.copy(**{
                "page_size.default": 20,
                "page_size.max": 100,
                "items": self.products
            }),
            errors = "set_default"
        )

    @request_property
    def output(self):
        output = ProductController.output(self)
        output.update(
            products = self.products,
            pagination = self.pagination
        )
        return output

