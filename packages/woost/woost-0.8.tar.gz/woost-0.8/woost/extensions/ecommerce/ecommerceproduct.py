#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2009
"""
from decimal import Decimal
from cocktail.modeling import getter
from cocktail import schema
from cocktail.translations import translations
from woost.models import (
    Publishable,
    Document,
    Controller,
    Template,
    File
)


class ECommerceProduct(Publishable):

    instantiable = False

    members_order = [
        "description",
        "price",
        "weight",
        "attachments",
        "purchase_model",
        "purchases",
        "template"
    ]

    default_controller = schema.DynamicDefault(
        lambda: Controller.get_instance(
            qname = "woost.extensions.ecommerce.product_controller"
        )
    )

    description = schema.String(
        translated = True,
        edit_control = "woost.views.RichTextEditor",
        member_group = "product_data"
    )

    price = schema.Decimal(
        required = True,
        default = Decimal("0"),
        member_group = "product_data"
    )
 
    weight = schema.Decimal(
        translate_value = lambda value, language = None, **kwargs:
            "" if not value else "%s Kg" % translations(value, language),
        member_group = "product_data"
    )

    attachments = schema.Collection(
        items = schema.Reference(type = File),
        related_end = schema.Collection(),
        member_group = "product_data"
    )

    purchase_model = schema.Reference(
        class_family = "woost.extensions.ecommerce.ecommercepurchase."
                       "ECommercePurchase",
        default = schema.DynamicDefault(
            lambda: ECommerceProduct.purchase_model.class_family
        ),
        required = True,
        searchable = False,
        member_group = "product_data"
    )

    purchases = schema.Collection(
        items = "woost.extensions.ecommerce.ecommercepurchase."
                "ECommercePurchase",
        bidirectional = True,
        visible = False,
        member_group = "product_data"
    )

    template = schema.Reference(
        type = Template,
        related_end = schema.Collection(),
        default = schema.DynamicDefault(
            lambda: Template.get_instance(
                qname = "woost.extensions.ecommerce.product_template"
            )
        ),
        member_group = "presentation"
    )

    def get_image(self):
        for attachment in self.attachments:
            if attachment.resource_type == "image" \
            and attachment.is_accessible():
                return attachment

    def offers(self):
        from woost.extensions.ecommerce import ECommerceExtension
        for pricing in ECommerceExtension.instance.pricing:
            if not pricing.hidden and pricing.applies_to(self):
                yield pricing

    @getter
    def inherited_resources(self):

        if self.inherit_resources and self.parent is None:
            catalog = Document.get_instance(
                qname = "woost.extensions.ecommerce.catalog_page"
            )

            if catalog:
                for resource in catalog.inherited_resources:
                    yield resource

                for resource in catalog.branch_resources:
                    yield resource        
        else:
            for resource in Publishable.inherited_resources.__get__(self):
                yield resource

