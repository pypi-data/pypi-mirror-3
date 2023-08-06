#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2009
"""
from decimal import Decimal
from cocktail import schema
from woost.models import Publishable, Controller


class Product(Publishable):

    instantiable = False
    view_class = None

    members_order = [
        "price",
        "categories",
        "entries"
    ]

    default_controller = schema.DynamicDefault(
        lambda: Controller.get_instance(qname = "woost.product_controller")
    )

    price = schema.Decimal(
        required = True,
        default = Decimal("0")
    )
    
    categories = schema.Collection(
        items = "woost.extensions.shop.productcategory.ProductCategory",
        bidirectional = True
    )

    entries = schema.Collection(
        items = "woost.extensions.shop.shoporderentry.ShopOrderEntry",
        bidirectional = True,
        visible = False,
        block_delete = True
    )

    def discounts(self):
        """Returns the discounts that can be applied to the product.        
        @rtype: L{Product<woost.extensions.shop.product.Product>}
        """
        from woost.extensions.shop import ShopExtension
        return [discount
                for discount in ShopExtension.instance.discounts
                if discount.applies_to(self)]

