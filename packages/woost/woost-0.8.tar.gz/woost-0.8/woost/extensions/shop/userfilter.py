#-*- coding: utf-8 -*-
"""

@author:        Jordi Fernández
@contact:       jordi.fernandez@whads.com
@organization:  Whads/Accent SL
@since:         May 2010
"""
from cocktail import schema
from cocktail.modeling import cached_getter, getter
from cocktail.translations import translations
from cocktail.schema.expressions import CustomExpression
from cocktail.controllers.userfilter import (
    user_filters_registry,
    UserFilter
)
from woost.extensions.shop.shoporder import ShopOrder


class ShopOrderCostFilter(UserFilter):

    id = "shop_order_cost"
    operators = ["eq", "ne", "gt", "ge", "lt", "le"]

    @cached_getter
    def schema(self):
        return schema.Schema("ShopOrderCostFilter", members = [
            schema.String(
                "operator",
                required = True,
                default = "eq",
                enumeration = self.operators,
                text_search = False,
                translate_value = lambda value, language = None, **kwargs:
                    "" if not value
                    else translations(
                        "cocktail.html.UserFilterEntry operator " + value,
                        language,
                        **kwargs
                    )
            ),
            schema.Boolean(
                "include_shipping",
                default = False
            ),
            schema.Boolean(
                "include_taxes",
                default = False
            ),
            schema.Boolean(
                "include_discounts",
                default = False
            ),
            schema.Decimal(
                "value",
                required = True
            )
        ])

    @getter
    def expression(self):
        if self.operator == "eq":
            return CustomExpression(
                lambda item: item.calculate_cost(
                    include_shipping = self.include_shipping,
                    include_taxes = self.include_taxes,
                    include_discounts = self.include_discounts
                )["total"] == self.value
            )
        elif self.operator == "ne":
            return CustomExpression(
                lambda item: item.calculate_cost(
                    include_shipping = self.include_shipping,
                    include_taxes = self.include_taxes,
                    include_discounts = self.include_discounts
                )["total"] != self.value
            )
        elif self.operator == "gt":
            return CustomExpression(
                lambda item: item.calculate_cost(
                    include_shipping = self.include_shipping,
                    include_taxes = self.include_taxes,
                    include_discounts = self.include_discounts
                )["total"] > self.value
            )
        elif self.operator == "ge": 
            return CustomExpression(
                lambda item: item.calculate_cost(
                    include_shipping = self.include_shipping,
                    include_taxes = self.include_taxes,
                    include_discounts = self.include_discounts
                )["total"] >= self.value
            )
        elif self.operator == "lt":
            return CustomExpression(
                lambda item: item.calculate_cost(
                    include_shipping = self.include_shipping,
                    include_taxes = self.include_taxes,
                    include_discounts = self.include_discounts
                )["total"] < self.value
            )
        else:
            return CustomExpression(
                lambda item: item.calculate_cost(
                    include_shipping = self.include_shipping,
                    include_taxes = self.include_taxes,
                    include_discounts = self.include_discounts
                )["total"] <= self.value
            )

user_filters_registry.add(ShopOrder, ShopOrderCostFilter)

