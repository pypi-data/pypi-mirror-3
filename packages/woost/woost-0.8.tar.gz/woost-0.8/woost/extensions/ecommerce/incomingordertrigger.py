#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.events import when
from woost.models.trigger import (
    ContentTrigger,
    trigger_responses
)
from woost.extensions.ecommerce.ecommerceorder import ECommerceOrder


class IncomingOrderTrigger(ContentTrigger):

    instantiable = True


@when(ECommerceOrder.incoming)
def _trigger_ecommerceorder_completed_responses(event):
    trigger_responses(
        IncomingOrderTrigger,
        target = event.source
    )

