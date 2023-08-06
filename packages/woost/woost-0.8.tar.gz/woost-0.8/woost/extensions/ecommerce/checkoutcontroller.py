#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.controllers import (
    request_property,    
    Form,
    FormProcessor
)
from woost.models import get_current_user, ModifyMemberPermission
from woost.controllers.documentcontroller import DocumentController
from woost.extensions.ecommerce import ECommerceExtension
from woost.extensions.ecommerce.ecommerceorder import ECommerceOrder
from woost.extensions.ecommerce.basket import Basket
from woost.extensions.ecommerce.orderstepcontroller import (
    ProceedForm,
    BackForm
)


class CheckoutController(FormProcessor, DocumentController):

    class CheckoutForm(ProceedForm):
        
        model = Basket.get().get_public_schema()

        @request_property
        def source_instance(self):
            return Basket.get()

        @request_property
        def schema(self):
            schema = ProceedForm.schema(self)
            payment_type = schema.get_member("payment_type")
            if payment_type:
                payment_type.enumeration = \
                    ECommerceExtension.instance.payment_types
            return schema

        def submit(self):
            Form.submit(self)
            Basket.store()
            self.proceed()

    class PreviousStepForm(BackForm):
        pass

