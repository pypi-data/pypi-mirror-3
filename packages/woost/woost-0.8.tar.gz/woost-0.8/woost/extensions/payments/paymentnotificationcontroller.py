#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2009
"""
from cocktail.controllers.controller import Controller


class PaymentNotificationController(Controller):
    
    def __call__(self, **parameters):
        from woost.extensions.payments import PaymentsExtension
        gateway = PaymentsExtension.instance.payment_gateway
        payment = gateway.process_notification(parameters)
        gateway.transaction_notified(payment = payment)

