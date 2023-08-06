#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2009
"""
import cherrypy
from cocktail.modeling import cached_getter
from cocktail import schema
from cocktail.controllers import get_parameter
from cocktail.controllers.usercollection import UserCollection
from woost.extensions.shop.shopcontroller import ShopController
from woost.extensions.shop.product import Product


class ProductsController(ShopController):
    """A controller used to browse a shop's product catalog."""

    def resolve(self, path):
        
        # Product detail
        if path:
            product_id = path.pop(0)
            
            try:
                product_id = int(product_id)
                product = Product.require_instance(product_id)
            except:
                raise cherrypy.NotFound()
 
            return self.get_detail_controller(product)        
       
        # Product listing
        return self

    def get_detail_controller(self, product):
        return ProductDetailController(product)

    @cached_getter
    def user_collection(self):
        user_collection = UserCollection(Product)
        return user_collection

    @cached_getter
    def output(self):
        output = ShopController.output(self)
        output["user_collection"] = self.user_collection
        return output


class ProductDetailController(ShopController):
    """A controller that provides a detailed view over a single product.
    
    @ivar product: The selected product.
    @type product: L{Product<woost.extensions.shop.product.Product>}
    """

    def __init__(self, product, *args, **kwargs):
        ShopController.__init__(self, *args, **kwargs)
        self.product = product

    @cached_getter
    def output(self):
        output = ShopController.output(self)
        output["product"] = self.product
        return output

