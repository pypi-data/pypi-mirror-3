#-*- coding: utf-8 -*-
u"""Defines the `Basket` class.

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import cherrypy
from cocktail.persistence import datastore
from cocktail.events import Event
from cocktail.controllers import session
from woost.extensions.ecommerce.ecommerceorder import ECommerceOrder
from woost.extensions.ecommerce.ecommercepurchase import ECommercePurchase
from woost.extensions.ecommerce.ecommerceproduct import ECommerceProduct


class Basket(object):

    session_key = "woost.extensions.ecommerce.basket"
    
    created = Event(doc = """
        An event triggered on the class when a new instance is created.

        @ivar basket: A reference to the new instance.
        @type basket: L{Basket}
        """)


    @classmethod
    def get(cls, create_new = True):
        """Obtains the shop order for the current user session.

        If the user had not started an order yet, a new one is created.
        
        :rtype: `~woost.extensions.ecommerce.ecommerceorder.ECommerceOrder`
        """
        order = getattr(
            cherrypy.request,
            "woost_ecommerce_order", 
            None
        )

        if order is None:
            order = cls.restore()

            if order is None and create_new:
                order = ECommerceOrder()
                cls.created(basket = order)

            cherrypy.request.woost_ecommerce_order = order

        return order
    
    @classmethod
    def pop(cls):
        """Remove the current shop order from the session."""
        order = cls.get(create_new = False)

        if order is not None:
            session.pop(cls.session_key, None)
            del cherrypy.request.woost_ecommerce_order

        return order

    @classmethod
    def empty(cls):
        """Removes all products from the basket."""
        order = cls.get(create_new = False)

        if order is not None:
            for purchase in list(order.purchases):
                purchase.delete()
            datastore.commit()

    @classmethod
    def store(cls):

        order = cls.get()
        order.insert()
        
        for purchase in order.purchases:
            purchase.insert()

        datastore.commit()
        session[cls.session_key] = order.id

    @classmethod
    def restore(cls):
        session_data = session.get(cls.session_key)

        if session_data is None:
            return None
        else:
            return ECommerceOrder.get_instance(session_data)

