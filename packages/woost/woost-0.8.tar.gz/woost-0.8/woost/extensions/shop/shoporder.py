#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2009
"""
from decimal import Decimal
from cocktail.translations import get_language, translations
from cocktail import schema
from woost.models import Item, Site
from woost.extensions.countries.country import Country
from woost.extensions.shop.shoporderentry import ShopOrderEntry


class ShopOrder(Item):

    members_order = [
        "address",
        "town",
        "region",
        "country",
        "postal_code",
        "cost",
        "entries"
    ]

    address = schema.String(
        member_group = "shipping_info",
        required = True,
        listed_by_default = False
    )

    town = schema.String(
        member_group = "shipping_info",
        required = True,
        listed_by_default = False
    )

    region = schema.String(
        member_group = "shipping_info",
        required = True,
        listed_by_default = False
    )

    country = schema.Reference(        
        member_group = "shipping_info",
        type = Country,
        related_end = schema.Collection(),
        required = True,
        listed_by_default = False,
        user_filter = "cocktail.controllers.userfilter.MultipleChoiceFilter"
    )

    postal_code = schema.String(
        member_group = "shipping_info",
        required = True,
        listed_by_default = False
    )

    cost = schema.Decimal(
        required = True,
        default = Decimal("0"),
        editable = False
    )

    language = schema.String(
        required = True,
        format = "^[a-z]{2}$",
        editable = False,
        default = schema.DynamicDefault(get_language),
        text_search = False,
        translate_value = lambda value, language = None, **kwargs:
            u"" if not value else translations(value, language, **kwargs)
    )

    status = schema.String(
        required = True,
        indexed = True,
        enumeration = ["pending", "accepted", "failed"],
        default = "pending",
        text_search = False,
        translate_value = lambda value, language = None, **kwargs:
            u"" if not value else translations(
                "woost.extensions.shop.ShopOrder.status " + value,
                language,
                **kwargs
            )
    )
    
    entries = schema.Collection(
        items = "woost.extensions.shop.shoporderentry.ShopOrderEntry",
        integral = True,
        bidirectional = True,
        min = 1
    )

    def calculate_cost(
        self, 
        include_shipping = True, 
        include_taxes = True, 
        include_discounts = True
    ):
        """Calculates the costs for the order.
        @rtype: dict
        """
        costs = {
            "pricing_policies": [],
            "price": {
                "cost": 0,
                "percentage": 0,
                "total": None
            },
            "shipping": 0,
            "tax": {
                "cost": 0,
                "percentage": 0
            },
            "entries": [
                {
                    "pricing_policies": [],
                    "quantity": entry.quantity,
                    "paid_quantity": entry.quantity,
                    "price": {
                        "cost": entry.product.price,
                        "percentage": 0
                    },
                    "shipping": 0,
                    "tax": {
                        "cost": 0,
                        "percentage": 0
                    }
                }
                for entry in self.entries
            ]
        }

        from woost.extensions.shop import ShopExtension
        shop_ext = ShopExtension.instance
        
        policies = list()

        if include_discounts:
            policies.extend(shop_ext.discounts)
        
        if include_shipping:
            policies.extend(shop_ext.shipping_costs)

        if include_taxes:
            policies.extend(shop_ext.taxes)

        for pricing_policy in policies:
            matching_items = pricing_policy.select_matching_items()

            if issubclass(matching_items.type, ShopOrder):
                if pricing_policy.applies_to(self):
                    pricing_policy.apply(self, costs)
                    costs["pricing_policies"].append(pricing_policy)
            else:
                for entry, entry_costs in zip(self.entries, costs["entries"]):
                    if pricing_policy.applies_to(entry.product):
                        pricing_policy.apply(entry.product, entry_costs)
                        entry_costs["pricing_policies"].append(pricing_policy)
        
        # Total price
        def apply_percentage(costs):
            cost = costs["cost"]
            percentage = costs["percentage"]
            if percentage:
                cost += cost * percentage / 100
            costs["total"] = cost
            return cost
        
        total_price = apply_percentage(costs["price"])

        for entry_costs in costs["entries"]:
            entry_price = apply_percentage(entry_costs["price"])
            entry_total_price = entry_price * entry_costs["paid_quantity"]
            entry_costs["total_price"] = entry_total_price
            total_price += entry_total_price

        costs["total_price"] = total_price

        # Total taxes
        total_taxes = costs["tax"]["cost"] \
                    + total_price * costs["tax"]["percentage"] / 100
        
        for entry_costs in costs["entries"]:
            quantity = entry_costs["paid_quantity"]
            entry_price = entry_costs["price"]["total"] * quantity
            entry_taxes = entry_costs["tax"]["cost"] * quantity \
                        + entry_price * entry_costs["tax"]["percentage"] / 100
            total_taxes += entry_taxes
            entry_costs["tax"]["total"] = entry_taxes

        costs["total_taxes"] = total_taxes

        # Total shipping costs
        total_shipping_costs = costs["shipping"] \
                             + sum(entry_costs["shipping"] * entry_costs["quantity"]
                                   for entry_costs in costs["entries"])
        costs["total_shipping_costs"] = total_shipping_costs

        # Grand total
        costs["total"] = total_price + total_taxes + total_shipping_costs

        return costs

    def count_items(self):
        """Gets the number of purchased product units in the order.
        @rtype: int
        """
        return sum(entry.quantity for entry in self.entries)

    def get_product_entry(self, product):
        """Gets the entry in the order for the given product.

        @param product: The product to obtain the entry for.
        @type product: L{Product<woost.extensions.shop.product.Product>}

        @return: The matching entry, or None if the order doesn't contain an
            entry for the indicated product.
        @rtype: L{ShopOrderEntry
                  <woost.extensions.shop.shoporderentry.ShopOrderEntry>}
        """
        for entry in self.entries:
            if entry.product is product:
                return entry

    def set_product_quantity(self, product, quantity):
        """Updates the quantity of ordered units for the indicated product.

        If an entry for the given product already exists, its quantity will be
        updated to the indicated value. If the indicated quantity is zero, the
        entry will be removed from the order. If no matching entry exists, a
        new entry for the product will be created with the specified amount of
        units.

        @param product: The product to set the quantity for.
        @type product: L{Product<woost.extensions.shop.product.Product>}

        @param quantity: The number of units of the product to order.
        @type quantity: int
        """
        entry = self.get_product_entry(product)

        if entry is None:
            if quantity:
                entry = ShopOrderEntry(
                    product = product,
                    quantity = quantity
                )
                self.entries.append(entry)
                if self.is_inserted:
                    entry.insert()
        else:
            if quantity:
                entry.quantity = quantity
            else:
                if entry.is_inserted:
                    entry.delete()
                else:
                    self.entries.remove(entry)

