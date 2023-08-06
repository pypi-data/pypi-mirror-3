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
from cocktail.events import Event, event_handler
from woost.models import (
    Item,
    Site,
    User,
    get_current_user,
    ModifyMemberPermission
)
from woost.extensions.locations.location import Location
from woost.extensions.ecommerce.ecommercebillingconcept \
    import ECommerceBillingConcept
from woost.extensions.payments import PaymentsExtension

def _translate_amount(amount, language = None, **kwargs):
    if amount is None:
        return "" 
    else:
        return translations(
            amount.quantize(Decimal("1.00")),
            language,
            **kwargs
        )

def _get_default_payment_type():
    from woost.extensions.ecommerce import ECommerceExtension
    payment_types = ECommerceExtension.instance.payment_types
    if len(payment_types) == 1:
        return payment_types[0]


class ECommerceOrder(Item):

    payment_types_completed_status = {
        "payment_gateway": "accepted",
        "transfer": "payment_pending", 
        "cash_on_delivery": "payment_pending"
    }

    incoming = Event(doc = """
        An event triggered when a new order is received.
        """)

    completed = Event(doc = """
        An event triggered when an order is completed.
        """)

    groups_order = [
        "shipping_info",
        "billing"
    ]

    members_order = [
        "customer",
        "address",
        "town",
        "region",
        "country",
        "postal_code",
        "language",
        "status",
        "purchases",
        "payment_type",
        "total_price",
        "pricing",
        "total_shipping_costs",
        "shipping_costs",
        "total_taxes",
        "taxes",
        "total"
    ]

    customer = schema.Reference(
        type = User,
        related_end = schema.Collection(),
        required = True,
        default = schema.DynamicDefault(get_current_user)
    )

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
        type = Location,
        relation_constraints = [Location.location_type.equal("country")],
        default_order = "location_name",
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
        enumeration = [
            "shopping",
            "payment_pending",
            "accepted",
            "failed",
            "refund"
        ],
        default = "shopping",
        text_search = False,
        translate_value = lambda value, language = None, **kwargs:
            u"" if not value else translations(
                "ECommerceOrder.status-" + value,
                language,
                **kwargs
            )
    )
    
    purchases = schema.Collection(
        items = "woost.extensions.ecommerce.ecommercepurchase."
                "ECommercePurchase",
        integral = True,
        bidirectional = True,
        min = 1
    )

    payment_type = schema.String(
        member_group = "billing",
        required = True,
        translate_value = lambda value, language = None, **kwargs:
            translations(
                "ECommerceOrder.payment_type-%s" % value,
                language = language
            ),
        default = schema.DynamicDefault(_get_default_payment_type),
        text_search = False,
        edit_control = "cocktail.html.RadioSelector",
        listed_by_default = False
    )

    total_price = schema.Decimal(
        member_group = "billing",
        editable = False,
        listed_by_default = False,
        translate_value = _translate_amount
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
        listed_by_default = False,
        translate_value = _translate_amount
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
        listed_by_default = False,
        translate_value = _translate_amount
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
        editable = False,
        translate_value = _translate_amount
    )

    def calculate_cost(self, 
        apply_pricing = True,
        apply_shipping_costs = True, 
        apply_taxes = True
    ):
        """Calculates the costs for the order.
        :rtype: dict
        """
        from woost.extensions.ecommerce import ECommerceExtension
        extension = ECommerceExtension.instance

        order_costs = {
            "price": {
                "cost": Decimal("0.00"),
                "percentage": Decimal("0.00"),
                "concepts": []
            },
            "shipping_costs": {
                "cost": Decimal("0.00"),
                "percentage": Decimal("0.00"),
                "concepts": []
            },
            "taxes": {
                "cost": Decimal("0.00"),
                "percentage": Decimal("0.00"),
                "concepts": []
            },
            "purchases": {}
        }
        
        # Per purchase costs:
        for purchase in self.purchases:
            purchase_costs = purchase.calculate_costs(
                apply_pricing = apply_pricing,
                apply_shipping_costs = apply_shipping_costs,
                apply_taxes = apply_taxes
            )
            order_costs["purchases"][purchase] = purchase_costs

            order_costs["price"]["cost"] += purchase_costs["price"]["total"]
            order_costs["shipping_costs"]["cost"] += \
                purchase_costs["shipping_costs"]["total"]
            order_costs["taxes"]["cost"] += purchase_costs["taxes"]["total"]

        # Order price
        order_price = order_costs["price"]

        if apply_pricing:
            for pricing in extension.pricing:
                if pricing.applies_to(self):
                    pricing.apply(self, order_price)

        order_price["cost"] += \
            order_price["cost"] * order_price["percentage"] / 100

        order_price["total"] = order_price["cost"]

        # Order shipping costs
        order_shipping_costs = order_costs["shipping_costs"]

        if apply_shipping_costs:
            for shipping_cost in extension.shipping_costs:
                if shipping_cost.applies_to(self):
                    shipping_cost.apply(self, order_shipping_costs)

        order_shipping_costs["total"] = (
            order_shipping_costs["cost"]
            + order_price["total"] * order_shipping_costs["percentage"] / 100
        )

        # Order taxes
        order_taxes = order_costs["taxes"]

        if apply_taxes:
            for tax in extension.taxes:
                if tax.applies_to(self):
                    tax.apply(self, order_taxes)

        order_taxes["total"] = (
            order_taxes["cost"]
            + order_price["total"] * order_taxes["percentage"] / 100
        )

        # Total
        order_costs["total"] = (
            order_price["total"]
          + order_shipping_costs["total"]
          + order_taxes["total"]
        )

        return order_costs

    def update_cost(self,
        apply_pricing = True,
        apply_shipping_costs = True, 
        apply_taxes = True
    ):
        costs = self.calculate_cost(
            apply_pricing = apply_pricing,
            apply_shipping_costs = apply_shipping_costs,
            apply_taxes = apply_taxes
        )
        
        self.total_price = costs["price"]["total"]
        self.pricing = list(costs["price"]["concepts"])

        self.total_shipping_costs = costs["shipping_costs"]["total"]
        self.shipping_costs = list(costs["shipping_costs"]["concepts"])

        self.total_taxes = costs["taxes"]["total"]
        self.taxes = list(costs["taxes"]["concepts"])

        self.total = costs["total"]

        for purchase, purchase_costs in costs["purchases"].iteritems():
            purchase.total_price = purchase_costs["price"]["total"]
            purchase.pricing = list(purchase_costs["price"]["concepts"])
            self.pricing.extend(purchase.pricing)

            purchase.total_shipping_costs = \
                purchase_costs["shipping_costs"]["total"]
            purchase.shipping_costs = \
                list(purchase_costs["shipping_costs"]["concepts"])
            self.shipping_costs.extend(purchase.shipping_costs)

            purchase.total_taxes = purchase_costs["taxes"]["total"]
            purchase.taxes = list(purchase_costs["taxes"]["concepts"])
            self.taxes.extend(purchase.taxes)

            purchase.total = purchase_costs["total"]

    def count_units(self):
        return sum(purchase.quantity for purchase in self.purchases)

    def get_weight(self):
        return sum(purchase.get_weight() for purchase in self.purchases)

    def add_purchase(self, purchase):
        for order_purchase in self.purchases:
            if order_purchase.__class__ is purchase.__class__ \
            and order_purchase.product is purchase.product \
            and all(
                order_purchase.get(option) == purchase.get(option)
                for option in purchase.get_options()
                if option.name != "quantity"
            ):
                order_purchase.quantity += purchase.quantity                
                purchase.product = None
                if purchase.is_inserted:
                    purchase.delete()
                break
        else:
            self.purchases.append(purchase)

    @classmethod
    def get_public_schema(cls):
        public_schema = schema.Schema("OrderCheckoutSummary")
        cls.get_public_adapter().export_schema(
            cls,
            public_schema
        )

        payment_type = public_schema.get_member("payment_type")
        if payment_type:
            payments = PaymentsExtension.instance

            if payments.enabled and payments.payment_gateway:

                translate_value = payment_type.translate_value

                def payment_type_translate_value(value, language = None, **kwargs):
                    if value == "payment_gateway":
                        return payments.payment_gateway.label
                    else:
                        return translate_value(
                            value, language = language, **kwargs
                        )

                payment_type.translate_value = payment_type_translate_value

        return public_schema

    @classmethod
    def get_public_adapter(cls):
        from woost.extensions.ecommerce import ECommerceExtension

        user = get_current_user()            
        adapter = schema.Adapter()
        adapter.exclude(["customer", "status", "purchases"])
        adapter.exclude([
            member.name
            for member in cls.members().itervalues()
            if not member.visible
            or not member.editable
            or not issubclass(member.schema, ECommerceOrder)
            or not user.has_permission(
                ModifyMemberPermission,
                member = member
            )
        ])
        if len(ECommerceExtension.instance.payment_types) == 1:
            adapter.exclude(["payment_type"])
        return adapter

    @property
    def is_completed(self):
        return self.status \
        and self.status == self.payment_types_completed_status.get(
            self.payment_type
        )

    @event_handler
    def handle_changed(cls, event):

        item = event.source
        member = event.member

        if member.name == "status":
            
            if event.previous_value == "shopping" \
            and event.value in ("payment_pending", "accepted"):
                item.incoming()

            if item.is_completed:
                item.completed()

    def get_description_for_gateway(self):
        if Site.main.site_name:
            return translations(
                "woost.extensions.ECommerceOrder description for gateway"
            ) % Site.main.site_name
        else:
            return translations(self)
