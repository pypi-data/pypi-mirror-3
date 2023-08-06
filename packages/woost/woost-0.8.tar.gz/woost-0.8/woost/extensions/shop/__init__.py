#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2009
"""
from cocktail.events import when
from cocktail.translations import (
    translations,
    set_language
)
from cocktail import schema
from cocktail.persistence import datastore
from woost.models import Extension, Language, Controller

translations.define("ShopExtension",
    ca = u"Botiga",
    es = u"Tienda",
    en = u"Shop"
)

translations.define("ShopExtension-plural",
    ca = u"Botigues",
    es = u"Tiendas",
    en = u"Shops"
)


class ShopExtension(Extension):

    def __init__(self, **values):
        Extension.__init__(self, **values)
        self.extension_author = u"Whads/Accent SL"
        self.set("description",
            u"""Proporciona els elements necessaris per implementar una botiga
            electrònica.""",
            "ca"
        )
        self.set("description",            
            u"""Proporciona los elementos necesarios para implementar una
            tienda electrónica.""",
            "es"
        )
        self.set("description",
            u"""Supplies the building blocks required to implement an online
            shop.""",
            "en"
        )

    def _load(self):

        from woost.extensions import shop
        from woost.extensions.shop import (
            strings,
            product,
            productcategory,
            shoporder,
            shoporderentry,
            pricing,
            basket,
            userfilter
        )

        for module, keys in (
            (product, ("Product",)),
            (productcategory, ("ProductCategory",)),
            (shoporder, ("ShopOrder",)),
            (shoporderentry, ("ShopOrderEntry",)),
            (pricing, (
                "PricingPolicy",
                "Discount",
                "PriceOverride",
                "RelativeDiscount",
                "PercentageDiscount",
                "FreeUnitsDiscount",
                "ShippingCost",
                "ShippingCostOverride",
                "CumulativeShippingCost",
                "Tax",
                "CumulativeTax",
                "PercentageTax"
            )),
            (basket, ("Basket",))
        ):
            for key in keys:
                setattr(shop, key, getattr(module, key))

        ShopExtension.add_member(
            schema.Collection("discounts",
                items = schema.Reference(type = pricing.Discount),
                related_end = schema.Reference()
            )
        )

        ShopExtension.add_member(
            schema.Collection("shipping_costs",
                items = schema.Reference(type = pricing.ShippingCost),
                related_end = schema.Reference()
            )
        )

        ShopExtension.add_member(
            schema.Collection("taxes",
                items = schema.Reference(type = pricing.Tax),
                related_end = schema.Reference()
            )
        )

        from tpv import (
            Currency,
            Payment,
            PaymentItem,
            PaymentNotFoundError
        )
        from woost.extensions.payments import PaymentsExtension
        from woost.extensions.payments.paymentgateway import PaymentGateway
        from woost.extensions.payments.transactionnotifiedtrigger \
            import launch_transaction_notification_triggers

        payments_ext = PaymentsExtension.instance
            
        def get_payment(self, payment_id):

            order = shoporder.ShopOrder.get_instance(int(payment_id))

            if order is None:
                raise PaymentNotFoundError(payment_id)
            
            payment = Payment()
            payment.id = order.id
            payment.amount = order.cost
            payment.shop_order = order
            payment.currency = Currency(payments_ext.payment_gateway.currency)
            
            for entry in order.entries:
                payment.add(PaymentItem(
                    reference = str(entry.product.id),
                    description = translations(entry.product),
                    units = entry.quantity,
                    price = entry.cost
                ))

            return payment

        PaymentGateway.get_payment = get_payment

        def receive_order_payment(event):            
            payment = event.payment
            shop_order = payment.shop_order            
            set_language(shop_order.language)           
            shop_order.status = payment.status
            shop_order.gateway_parameters = payment.gateway_parameters
        
        def commit_order_payment(event):
            datastore.commit()
        
        events = PaymentGateway.transaction_notified
        pos = events.index(launch_transaction_notification_triggers)
        events.insert(pos, receive_order_payment)
        events.insert(pos + 2, commit_order_payment)

        self.install()

    def _install(self):

        # Create the product controller
        controller = Controller()
        controller.qname = "woost.product_controller"
        for language in Language.codes:
            value = translations(
                "woost.extensions.shop Product controller title",
                language
            )
            if value:
                controller.set("title", value, language)
        controller.python_name = \
            "woost.extensions.shop.productcontroller.ProductController"
        controller.insert()

