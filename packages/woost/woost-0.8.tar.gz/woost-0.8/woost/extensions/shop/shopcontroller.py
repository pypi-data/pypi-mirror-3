#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2009
"""
from cocktail.modeling import cached_getter
from woost.controllers.documentcontroller import DocumentController
from woost.extensions.shop.basket import Basket


class ShopController(DocumentController):

    @cached_getter
    def output(self):
        output = DocumentController.output(self)
        output["shop_order"] = Basket.get()
        return output

