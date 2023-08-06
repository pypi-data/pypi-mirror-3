#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2009
"""
import cherrypy
from cocktail import schema
from cocktail.controllers import get_parameter, Location
from woost.controllers.basecmscontroller import BaseCMSController
from woost.extensions.payments.dummypaymentgateway \
    import DummyPaymentGateway
from urllib import urlopen


class DummyPaymentGatewayController(BaseCMSController):
    """A controller used by L{DummyPaymentGateway
    <woost.extensions.payments.dummypaymentgateway.DummyPaymentGateway>}
    instances to simulate transaction payments.
    """
    
    def __call__(self, **parameters):

        # Get references to the gateway and payment
        gateway = get_parameter(
            schema.Reference("gateway_id", type = DummyPaymentGateway)
        )

        if gateway is None:
            raise ValueError("Wrong payment gateway")
        
        payment_id = get_parameter(schema.String("payment_id"))
        payment = payment_id and gateway.get_payment(payment_id) or None

        if payment is None:
            raise ValueError("Wrong payment id (%s)" % payment_id)
        
        # Notify the payment to the application
        cms = self.context["cms"]
        notification_uri = Location.get_current_host()
        notification_uri.path_info = cms.application_uri(
            "payment_notification",
            payment_id = payment_id
        )
        urlopen(str(notification_uri))

        # Redirect the user after the transaction's over
        redirection = None

        if gateway.payment_status == "accepted":
            redirection = gateway.payment_successful_page
        elif gateway.payment_status == "failed":
            redirection = gateway.payment_failed_page            

        raise cherrypy.HTTPRedirect(
            (redirection and cms.uri(redirection)
            or cms.application_uri()).encode("utf-8")
        )

