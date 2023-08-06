#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2009
"""
import cherrypy
from cocktail.modeling import extend, call_base
from cocktail.translations import translations
from cocktail import schema
from cocktail.controllers import (
    get_parameter,
    request_property,
    FormProcessor,
    Form,
    Location
)
from woost.models import Publishable
from woost.controllers.documentcontroller import DocumentController
from woost.controllers.notifications import notify_user
from woost.extensions.ecommerce.ecommerceproduct import ECommerceProduct
from woost.extensions.ecommerce.ecommercepurchase import ECommercePurchase
from woost.extensions.ecommerce.basket import Basket
from woost.extensions.ecommerce.orderstepcontroller import (
    ProceedForm,
    BackForm
)


class BasketController(FormProcessor, DocumentController):

    @request_property
    def action(self):

        delete_purchase = cherrypy.request.params.get("delete_purchase", None)

        if delete_purchase:
            cherrypy.request.params["purchase"] = delete_purchase
            return "delete_purchase"

        return FormProcessor.action(self)

    class SetQuantitiesForm(Form):
        """Update the number of units for each purchase."""

        actions = "set_quantities", "proceed"

        @request_property
        def model(self):
            model = schema.Schema("SetQuantitiesForm", members = [
                schema.Collection("quantity",
                    items = schema.Integer(min = 1),
                    length = len(Basket.get().purchases)
                )
            ])

            @extend(model["quantity"].items)
            def translate_error(member, error, language = None, **kwargs):
                if isinstance(error, schema.exceptions.MinValueError):
                    return translations(
                        "SetQuantitiesForm-MinValueError",
                        language,
                        **kwargs
                    )
                else:
                    return call_base(error, language, **kwargs)

            return model

        def submit(self):
            Form.submit(self)
            
            for purchase, quantity in zip(
                Basket.get().purchases,
                self.instance["quantity"]
            ):
                purchase.quantity = quantity

            Basket.store()
            notify_user(
                translations("woost.extensions.ecommerce."
                             "set_quantities_notice"),
                category = "success"
            )
            
            if self.controller.action != "proceed":
                Location.get_current().go("GET")
    
    class NextStepForm(ProceedForm):
        process_after = "set_quantities_form",

    class PreviousStepForm(BackForm):
        pass

    class DeletePurchaseForm(Form):
        """A form that removes a product from the shopping basket."""

        actions = "delete_purchase",

        @request_property
        def model(self):
            return schema.Schema("DeletePurchaseForm", members = [
                schema.Reference("purchase", 
                    type = ECommercePurchase,
                    required = True,
                    enumeration = lambda ctx: Basket.get().purchases
                )
            ])

        def submit(self):
            Form.submit(self)
            purchase = self.instance["purchase"]
            product = purchase.product
            purchase.delete()
            Basket.store()
            notify_user(
                translations(
                    "woost.extensions.ecommerce.delete_purchase_notice",
                    product = product
                ),
                category = "success"
            )
            Location.get_current().go("GET")

    class EmptyBasketForm(Form):
        """A form that removes all products from the shopping basket."""

        actions = "empty_basket",

        def submit(self):
            Basket.empty()
            notify_user(
                translations("woost.extensions.ecommerce."
                             "empty_basket_notice"),
                category = "success"
            )
            Location.get_current().go("GET")

