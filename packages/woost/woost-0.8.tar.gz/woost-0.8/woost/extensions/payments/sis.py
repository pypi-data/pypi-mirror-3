#-*- coding: utf-8 -*-
"""

@author:		Jordi Fernández
@contact:		jordi.fernandez@whads.com
@organization:	Whads/Accent SL
@since:			October 2009
"""
from tpv.sis import SISPaymentGateway as Implementation
from cocktail import schema
from cocktail.translations import translations
from cocktail.modeling import getter
from cocktail.controllers import context
from cocktail.controllers.location import Location
from woost.models import Document
from woost.extensions.payments.paymentgateway import PaymentGateway


class SISPaymentGateway(PaymentGateway, Implementation):

    members_order = [
        "merchant_name", "merchant_code", "merchant_terminal",
        "merchant_secret_key", "payment_successful_page", "payment_failed_page"
    ]

    instantiable = True

    default_label = schema.DynamicDefault(
        lambda: translations("SISPaymentGateway.label default")
    )

    merchant_code = schema.String(
        required = True,
        shadows_attribute = True,
        text_search = False
    )

    merchant_name = schema.String(
        shadows_attribute = True,
        text_search = False
    )

    merchant_terminal = schema.String(
        required = True,
        shadows_attribute = True,
        text_search = False
    )

    merchant_secret_key = schema.String(
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

