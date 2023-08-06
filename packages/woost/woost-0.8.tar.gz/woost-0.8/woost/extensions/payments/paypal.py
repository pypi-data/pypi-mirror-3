#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Jordi Fernández <jordi.fernandez@whads.com>
"""
from tpv.paypal import PayPalPaymentGateway as Implementation
from cocktail import schema
from cocktail.translations import translations
from cocktail.modeling import getter
from cocktail.controllers import context
from cocktail.controllers.location import Location
from woost.models import Document
from woost.extensions.payments.paymentgateway import PaymentGateway


class PayPalPaymentGateway(PaymentGateway, Implementation):

    members_order = [
        "business", "payment_successful_page", "payment_failed_page"
    ]

    default_label = schema.DynamicDefault(
        lambda: translations("PayPalPaymentGateway.label default")
    )

    instantiable = True

    business = schema.String(
        required = True,
        shadows_attribute = True,
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

    def _base_url(self):
        location = Location.get_current()
        location.relative = False
        location.path_info = context["cms"].application_uri()
        location.query_string = None

        return unicode(location)[:-1]

    @getter
    def notification_url(self):
        return self._base_url() + context["cms"].application_uri("payment_notification")

    @getter
    def payment_successful_url(self):

        if self.payment_successful_page:
            return self._base_url() \
                + context["cms"].uri(self.payment_successful_page) \
                + "?payment_id=%(payment_id)s"

        return None

    @getter
    def payment_failed_url(self):

        if self.payment_failed_page:
            return self._base_url() \
                + context["cms"].uri(self.payment_failed_page) \
                + "?payment_id=%(payment_id)s"

        return None

    def get_payment_form_data(self, payment_id, language = None):
        url, params = Implementation.get_payment_form_data(
            self, payment_id, language = language
        )

        payment = self.get_payment(payment_id)
        order = payment.order

        if order:
            if order.address:
                params.append(("address1", order.address[:100]))

            if order.town:
                params.append(("city", order.town[:40]))

            if order.country and order.country.code:
                params.append(("country", order.country.code))

            if order.postal_code:
                params.append(("zip", order.postal_code[:32]))

            if order.language:
                params.append(("lc", order.language.upper()))

        return url, params
