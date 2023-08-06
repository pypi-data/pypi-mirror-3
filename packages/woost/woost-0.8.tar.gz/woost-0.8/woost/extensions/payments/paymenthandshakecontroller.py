#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2009
"""
from cocktail.controllers import Controller


class PaymentHandshakeController(Controller):
    
    def __call__(self, **parameters):
        from woost.extensions.payments import PaymentsExtension
        gateway = PaymentsExtension.instance.payment_gateway
        return gateway.handle_handshake(parameters)

