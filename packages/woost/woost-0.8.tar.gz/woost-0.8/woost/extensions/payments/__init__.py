#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2009
"""
from cocktail.modeling import OrderedDict
from cocktail.translations import translations, get_language
from cocktail import schema
from cocktail.controllers.location import Location
from woost.models import Extension

translations.define("PaymentsExtension",
    ca = u"Pagaments",
    es = u"Pagos",
    en = u"Payments"
)

translations.define("PaymentsExtension-plural",
    ca = u"Pagaments",
    es = u"Pagos",
    en = u"Payments"
)


class PaymentsExtension(Extension):

    def __init__(self, **values):
        Extension.__init__(self, **values)
        self.extension_author = u"Whads/Accent SL"
        self.set("description",
            u"""Afageix suport per pagaments en línia.""",
            "ca"
        )
        self.set("description",            
            u"""Añade soporte para pagos en linea.""",
            "es"
        )
        self.set("description",
            u"""Adds support for online payments.""",
            "en"
        )

    def _load(self):

        # Import the extension's models
        from woost.extensions.payments.paymentgateway import PaymentGateway
        from woost.extensions.payments import (
            strings,
            dummypaymentgateway,
            pasat4b,
            sis,
            paypal,
            transactionnotifiedtrigger
        )

        # Setup payment controllers
        from woost.controllers.cmscontroller import CMSController
        from woost.extensions.payments.paymenthandshakecontroller \
            import PaymentHandshakeController
        from woost.extensions.payments.paymentnotificationcontroller \
            import PaymentNotificationController
        from woost.extensions.payments.dummycontroller \
            import DummyPaymentGatewayController

        CMSController.payment_handshake = PaymentHandshakeController
        CMSController.payment_notification = PaymentNotificationController
        CMSController.dummy_payment_gateway = DummyPaymentGatewayController

        # Append additional members to the extension
        PaymentsExtension.members_order = ["payment_gateway"]

        PaymentsExtension.add_member(
            schema.Reference("payment_gateway",
                type = PaymentGateway,
                related_end = schema.Reference()
            )
        )

    def payment_request(self, payment_id):
        """Begin a payment transaction, redirecting the user to the payment
        gateway.
        
        @param payment_id: The identifier of the payment to execute.
        """
        url, params = self.payment_gateway.get_payment_form_data(
            payment_id,
            get_language()
        )

        location = Location(url)
        location.method = "POST"
        location.form_data = OrderedDict(params)
        location.go()

