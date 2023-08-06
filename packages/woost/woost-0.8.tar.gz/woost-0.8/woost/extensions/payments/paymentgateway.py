#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2009
"""
from tpv.currencies import currency_alpha
from cocktail.events import Event
from cocktail.translations import translations
from cocktail import schema
from woost.models import Item


class PaymentGateway(Item):

    instantiable = False
    visible_from_root = False

    transaction_notified = Event(
        """An event triggered when the payment gateway notifies the application
        of the outcome of a payment transaction.

        @param payment: The payment that the notification is sent for.
        @type payment: L{Payment<tpv.payment.Payment>}
        """
    )

    members_order = [
        "label",
        "test_mode",
        "currency"
    ]

    label = schema.String(
        required = True,
        translated = True
    )
    
    test_mode = schema.Boolean(
        required = True,
        default = True
    )

    currency = schema.String(
        required = True,
        enumeration = currency_alpha,
        text_search = False
    )

    def __translate__(self, language, **kwargs):
        return translations(self.__class__.name, language)

