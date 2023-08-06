#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2009
"""
from tpv.paymentgateway import PaymentGateway
from cocktail.translations import translations
from cocktail import schema
from cocktail.controllers import context
from woost.models import Document
from woost.extensions.payments.paymentgateway \
    import PaymentGateway as CMSPaymentGateway


class DummyPaymentGateway(CMSPaymentGateway, PaymentGateway):
    """A simulated payment gateway, useful for testing purposes."""
    
    instantiable = True
    members_order = [
        "payment_status",
        "payment_successful_page",
        "payment_failed_page"
    ]

    payment_status = schema.String(
        required = True,
        enumeration = ("accepted", "failed"),
        default = "accepted",
        translate_value = lambda value, language = None, **kwargs:
            u"" if not value else translations(
                "woost.extensions.payments."
                "DummyPaymentGateway.payment_status " + value,
                language,
                **kwargs
            ),
        text_search = False
    )

    payment_successful_page = schema.Reference(
        type = Document,
        related_end = schema.Reference()
    )

    payment_failed_page = schema.Reference(
        type = Document,
        related_end = schema.Reference()
    )

    def get_payment_form_data(self, payment_id, language = None):
        return (
            context["cms"].application_uri("dummy_payment_gateway"),
            (
                ("gateway_id", self.id),
                ("payment_id", payment_id)
            )
        )

    def process_notification(self, parameters):
        payment_id = parameters["payment_id"]
        payment = self.get_payment(payment_id)
        payment.status = self.payment_status
        return payment

