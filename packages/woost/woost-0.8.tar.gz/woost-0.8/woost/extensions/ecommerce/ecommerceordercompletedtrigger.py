#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			Aug 2009
"""
from cocktail.events import when
from woost.models.trigger import (
    ContentTrigger,
    trigger_responses
)
from woost.extensions.ecommerce.ecommerceorder import ECommerceOrder


class ECommerceOrderCompletedTrigger(ContentTrigger):

    instantiable = True


@when(ECommerceOrder.completed)
def _trigger_ecommerceorder_completed_responses(event):
    trigger_responses(
        ECommerceOrderCompletedTrigger,
        target = event.source
    )

