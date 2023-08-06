#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2009
"""
import cherrypy
from cocktail.persistence import datastore
from cocktail.controllers import session
from woost.extensions.shop.shoporder import ShopOrder
from woost.extensions.shop.shoporderentry import ShopOrderEntry
from woost.extensions.shop.product import Product


class Basket(object):

    session_key = "woost.extensions.shop basket"
    
    @classmethod
    def get(cls):
        """Returns the shop order for the current user session.

        If the user had not started an order yet, a new one is created.
        
        @rtype: L{ShopOrder<woost.extensions.shop.shoporder.ShopOrder>}
        """
        order = getattr(cherrypy.request, "woost_shop_basket", None)

        if order is None:
            order = cls.restore()

            if order is None:
                order = ShopOrder()

            cherrypy.request.woost_shop_basket = order

        return order
    
    @classmethod
    def drop(cls):
        """Drops the current shop order."""
        session.pop(cls.session_key, None)

    @classmethod
    def store(cls):
        order = cls.get()
        order.insert()
        datastore.commit()
        session[cls.session_key] = order.id

    @classmethod
    def restore(cls):
        session_data = session.get(cls.session_key)

        if session_data is None:
            return None
        else:
            return ShopOrder.get_instance(session_data)

