#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2009
"""
from decimal import Decimal
from cocktail.translations import translations
from cocktail import schema
from woost.models import (
    Item,
    get_current_user,
    ModifyMemberPermission
)
from woost.extensions.ecommerce.ecommercebillingconcept \
    import ECommerceBillingConcept


class ECommercePurchase(Item):

    listed_from_root = False

    members_order = [
        "order",
        "product",
        "quantity",
        "total_price",
        "pricing",
        "total_shipping_costs",
        "shipping_costs",
        "total_taxes",
        "taxes",
        "total"
    ]

    order = schema.Reference(
        type = "woost.extensions.ecommerce.ecommerceorder.ECommerceOrder",
        bidirectional = True,
        required = True
    )

    product = schema.Reference(
        type = "woost.extensions.ecommerce.ecommerceproduct.ECommerceProduct",
        bidirectional = True,
        required = True
    )

    quantity = schema.Integer(
        required = True,
        min = 1,
        default = 1
    )

    total_price = schema.Decimal(
        member_group = "billing",
        editable = False,
        listed_by_default = False
    )

    pricing = schema.Collection(
        member_group = "billing",
        items = schema.Reference(type = ECommerceBillingConcept),
        related_end = schema.Collection(
            block_delete = True
        ),
        editable = False
    )

    total_shipping_costs = schema.Decimal(
        member_group = "billing",
        editable = False,
        listed_by_default = False
    )

    shipping_costs = schema.Collection(
        member_group = "billing",
        items = schema.Reference(type = ECommerceBillingConcept),
        related_end = schema.Collection(
            block_delete = True
        ),
        editable = False
    )
    
    total_taxes = schema.Decimal(
        member_group = "billing",
        editable = False,
        listed_by_default = False
    )

    taxes = schema.Collection(
        member_group = "billing",
        items = schema.Reference(type = ECommerceBillingConcept),
        related_end = schema.Collection(
            block_delete = True
        ),
        editable = False
    )
    
    total = schema.Decimal(
        member_group = "billing",
        editable = False
    )

    def __translate__(self, language, **kwargs):
        if self.draft_source is not None:
            return Item.__translate__(self, language, **kwargs)

        desc = u"%d x %s" % (
            self.quantity,
            translations(self.product, language)
        )

        options = []
        for member in self.get_options():
            if member is ECommercePurchase.quantity:
                continue
            options.append("%s: %s" % (
                translations(member, language),
                member.translate_value(self.get(member), language)
            ))

        if options:
            desc += u" (%s)" % u", ".join(options)

        return desc
    
    def calculate_costs(self,
        apply_pricing = True,
        apply_shipping_costs = True, 
        apply_taxes = True
    ):
        from woost.extensions.ecommerce import ECommerceExtension
        extension = ECommerceExtension.instance

        purchase_costs = {
            "price": {
                "cost": self.get_unit_price(),
                "paid_units": self.quantity,
                "percentage": Decimal("0.00"),
                "concepts": []
            },
            "shipping_costs": {
                "cost": Decimal("0.00"),
                "paid_units": self.quantity,
                "percentage": Decimal("0.00"),
                "concepts": []
            },
            "taxes": {
                "cost": Decimal("0.00"),
                "paid_units": self.quantity,
                "percentage": Decimal("0.00"),
                "concepts": []
            }
        }

        # Price
        purchase_price = purchase_costs["price"]

        if apply_pricing:
            for pricing in extension.pricing:
                if pricing.applies_to(self, purchase_costs):
                    pricing.apply(self, purchase_price)

        purchase_price["cost"] += \
            purchase_price["cost"] * purchase_price["percentage"] / 100

        purchase_price["total"] = \
            purchase_price["cost"] * purchase_price["paid_units"]

        # Shipping costs
        purchase_shipping_costs = purchase_costs["shipping_costs"]

        if apply_shipping_costs:
            for shipping_cost in extension.shipping_costs:
                if shipping_cost.applies_to(self, purchase_costs):
                    shipping_cost.apply(self, purchase_shipping_costs)

        purchase_shipping_costs["cost"] += \
            purchase_price["cost"] * purchase_shipping_costs["percentage"] / 100

        purchase_shipping_costs["total"] = \
            purchase_shipping_costs["cost"] * purchase_shipping_costs["paid_units"]

        # Taxes
        purchase_taxes = purchase_costs["taxes"]
        
        if apply_taxes:
            for tax in extension.taxes:
                if tax.applies_to(self, purchase_costs):
                    tax.apply(self, purchase_taxes)

        purchase_taxes["cost"] += \
            purchase_price["cost"] * purchase_taxes["percentage"] / 100

        purchase_taxes["total"] = \
            purchase_taxes["cost"] * purchase_taxes["paid_units"]

        # Total
        purchase_costs["total"] = (
            purchase_price["total"] 
          + purchase_shipping_costs["total"]
          + purchase_taxes["total"]
        )
        return purchase_costs

    def get_unit_price(self):
        return self.product.price

    def get_weight(self):
        if self.product is None or self.product.weight is None:
            return 0
        else:
            return self.quantity * self.product.weight

    @classmethod
    def get_options(cls):
        for member in cls.members().itervalues():
            if (
                member is not cls.product
                and member is not cls.order
                and member.visible
                and member.editable
                and issubclass(member.schema, ECommercePurchase)
                and get_current_user().has_permission(
                    ModifyMemberPermission,
                    member = member
                )
            ):
                yield member

