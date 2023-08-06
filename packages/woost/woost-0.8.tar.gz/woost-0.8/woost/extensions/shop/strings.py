#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2009
"""
from cocktail.translations import translations

# ShopExtension
#------------------------------------------------------------------------------
translations.define("ShopExtension.discounts",
    ca = u"Descomptes",
    es = u"Descuentos",
    en = u"Discounts"
)

translations.define("ShopExtension.shipping_costs",
    ca = u"Costos d'enviament",
    es = u"Costes de envío",
    en = u"Shipping costs"
)

translations.define("ShopExtension.taxes",
    ca = u"Impostos",
    es = u"Impuestos",
    en = u"Taxes"
)

# Product
#------------------------------------------------------------------------------
translations.define("Product",
    ca = u"Producte",
    es = u"Producto",
    en = u"Product"
)

translations.define("Product-plural",
    ca = u"Productes",
    es = u"Productos",
    en = u"Products"
)

translations.define("Product.price",
    ca = u"Preu",
    es = u"Precio",
    en = u"Price"
)

translations.define("Product.categories",
    ca = u"Categories",
    es = u"Categorías",
    en = u"Categories"
)

# ProductCategory
#------------------------------------------------------------------------------
translations.define("ProductCategory",
    ca = u"Categoria de producte",
    es = u"Categoría de producto",
    en = u"Product category"
)

translations.define("ProductCategory-plural",
    ca = u"Categories de producte",
    es = u"Categorías de producto",
    en = u"Product categories"
)

translations.define("ProductCategory.title",
    ca = u"Nom",
    es = u"Nombre",
    en = u"Name"
)

translations.define("ProductCategory.parent",
    ca = u"Categoria pare",
    es = u"Categoría padre",
    en = u"Parent category"
)

translations.define("ProductCategory.children",
    ca = u"Categories filles",
    es = u"Categorías hijas",
    en = u"Child categories"
)

translations.define("ProductCategory.products",
    ca = u"Productes",
    es = u"Productos",
    en = u"Products"
)

# ShopOrder
#------------------------------------------------------------------------------
translations.define("ShopOrder",
    ca = u"Comanda",
    es = u"Pedido",
    en = u"Shop order"
)

translations.define("ShopOrder-plural",
    ca = u"Comandes",
    es = u"Pedidos",
    en = u"Shop orders"
)

translations.define("ShopOrder.entries",
    ca = u"Contingut de la comanda",
    es = u"Contenido del pedido",
    en = u"Order entries"
)
    
translations.define("ShopOrder.cost",
    ca = u"Cost",
    es = u"Coste",
    en = u"Cost"
)

translations.define("ShopOrder.status",
    ca = u"Estat",
    es = u"Estado",
    en = u"State"
)

translations.define("woost.extensions.shop.ShopOrder.status pending",
    ca = u"Pendent",
    es = u"Pendiente",
    en = u"Pending"
)

translations.define("woost.extensions.shop.ShopOrder.status accepted",
    ca = u"Acceptada",
    es = u"Aceptada",
    en = u"Accepted"
)

translations.define("woost.extensions.shop.ShopOrder.status failed",
    ca = u"Cancel·lada",
    es = u"Cancelada",
    en = u"Cancelled"
)

translations.define("ShopOrder.language",
    ca = u"Idioma",
    es = u"Idioma",
    en = u"Language"
)

translations.define("ShopOrder.shipping_info",
    ca = u"Informació d'enviament",
    es = u"Información de envío",
    en = u"Shipping address"
)

translations.define("ShopOrder.address",
    ca = u"Adreça d'enviament",
    es = u"Dirección de envío",
    en = u"Shipping address"
)

translations.define("ShopOrder.town",
    ca = u"Població",
    es = u"Población",
    en = u"Town"
)

translations.define("ShopOrder.region",
    ca = u"Regió/Estat/Província",
    es = u"Región/Estado/Provincia",
    en = u"Region/Estado/Provincia"
)

translations.define("ShopOrder.country",
    ca = u"País",
    es = u"País",
    en = u"Country"
)

translations.define("ShopOrder.postal_code",
    ca = u"Codi postal",
    es = u"Código postal",
    en = u"Postal code"
)

# ShopOrderEntry
#------------------------------------------------------------------------------
translations.define("ShopOrderEntry",
    ca = u"Línia de comanda",
    es = u"Linea de pedido",
    en = u"Shop order entry"
)

translations.define("ShopOrderEntry-plural",
    ca = u"Línies de comanda",
    es = u"Lineas de pedido",
    en = u"Shop order entries"
)

translations.define("ShopOrderEntry.shop_order",
    ca = u"Comanda",
    es = u"Pedido",
    en = u"Shop order"
)

translations.define("ShopOrderEntry.product",
    ca = u"Producte",
    es = u"Producto",
    en = u"Product"
)

translations.define("ShopOrderEntry.quantity",
    ca = u"Quantitat",
    es = u"Cantidad",
    en = u"Quantity"
)

translations.define("ShopOrderEntry.cost",
    ca = u"Cost",
    es = u"Coste",
    en = u"Cost"
)

# PricingPolicy
#------------------------------------------------------------------------------
translations.define("PricingPolicy",
    ca = u"Política de preus",
    es = u"Política de precios",
    en = u"Pricing policy"
)

translations.define("PricingPolicy-plural",
    ca = u"Polítiques de preus",
    es = u"Políticas de precios",
    en = u"Pricing policies"
)

translations.define("PricingPolicy.title",
    ca = u"Títol",
    es = u"Título",
    en = u"Title"
)

translations.define("PricingPolicy.enabled",
    ca = u"Activa",
    es = u"Activa",
    en = u"Enabled"
)

translations.define("PricingPolicy.start_date",
    ca = u"Data d'inici",
    es = u"Fecha de inicio",
    en = u"Start date"
)

translations.define("PricingPolicy.end_date",
    ca = u"Data de fi",
    es = u"Fecha de fin",
    en = u"End date"
)

translations.define("PricingPolicy.matching_items",
    ca = u"Elements afectats",
    es = u"Elementos afectados",
    en = u"Matching items"
)

# Discount
#------------------------------------------------------------------------------
translations.define("Discount",
    ca = u"Descompte",
    es = u"Descuento",
    en = u"Discount"
)

translations.define("Discount-plural",
    ca = u"Descomptes",
    es = u"Descuentos",
    en = u"Discounts"
)

# AbsoluteDiscount
#------------------------------------------------------------------------------
translations.define("PriceOverride",
    ca = u"Preu ajustat",
    es = u"Precio ajustado",
    en = u"Price override"
)

translations.define("PriceOverride-plural",
    ca = u"Preus ajustats",
    es = u"Precios ajustados",
    en = u"Price overrides"
)

translations.define("PriceOverride.price",
    ca = u"Preu",
    es = u"Precio",
    en = u"Price"
)

# RelativeDiscount
#------------------------------------------------------------------------------
translations.define("RelativeDiscount",
    ca = u"Descompte relatiu",
    es = u"Descuento relativo",
    en = u"Relative discount"
)

translations.define("RelativeDiscount-plural",
    ca = u"Descomptes relatius",
    es = u"Descuentos relativos",
    en = u"Relative discounts"
)

translations.define("RelativeDiscount.amount",
    ca = u"Descompte",
    es = u"Descuento",
    en = u"Discount"
)

# PercentageDiscount
#------------------------------------------------------------------------------
translations.define("PercentageDiscount",
    ca = u"Descompte percentual",
    es = u"Descuento porcentual",
    en = u"Percentage discount"
)

translations.define("PercentageDiscount-plural",
    ca = u"Descomptes percentuals",
    es = u"Descuentos porcentuales",
    en = u"Percentage discounts"
)

translations.define("PercentageDiscount.percentage",
    ca = u"Percentatge",
    es = u"Porcentaje",
    en = u"Percentage"
)

# FreeUnitsDiscount
#------------------------------------------------------------------------------
translations.define("FreeUnitsDiscount",
    ca = u"Unitats gratuïtes",
    es = u"Unidades gratuitas",
    en = u"Free units"
)

translations.define("FreeUnitsDiscount-plural",
    ca = u"Unitats gratuïtes",
    es = u"Unidades gratuitas",
    en = u"Free units"
)

translations.define("FreeUnitsDiscount.paid_units",
    ca = u"Unitats pagades",
    es = u"Unidades pagadas",
    en = u"Paid units"
)

translations.define("FreeUnitsDiscount.free_units",
    ca = u"Unitats de regal",
    es = u"Unidades de regalo",
    en = u"Free units"
)

translations.define("FreeUnitsDiscount.repeated",
    ca = u"Admet múltiples",
    es = u"Admite múltiples",
    en = u"Repeated"
)

# ShippingCost
#------------------------------------------------------------------------------
translations.define("ShippingCost",
    ca = u"Cost d'enviament",
    es = u"Coste de envío",
    en = u"Shipping cost"
)

translations.define("ShippingCost-plural",
    ca = u"Costos d'enviament",
    es = u"Costes de envío",
    en = u"Shipping costs"
)

# ShippingCostOverride
#------------------------------------------------------------------------------
translations.define("ShippingCostOverride",
    ca = u"Cost d'enviament absolut",
    es = u"Coste de envío absoluto",
    en = u"Shipping cost override"
) 

translations.define("ShippingCostOverride-plural",
    ca = u"Costos d'enviament absoluts",
    es = u"Costes de envío absolutos",
    en = u"Shipping cost overrides"
)

translations.define("ShippingCostOverride.cost",
    ca = u"Cost",
    es = u"Coste",
    en = u"Cost"
)

# CumulativeShippingCost
#------------------------------------------------------------------------------
translations.define("CumulativeShippingCost",
    ca = u"Cost d'enviament acomulatiu",
    es = u"Coste de envío acomulativo",
    en = u"Cumulative shipping cost"
)

translations.define("CumulativeShippingCost-plural",
    ca = u"Costos d'enviament acomulatius",
    es = u"Costes de envío acomulativos",
    en = u"Cumulative shipping costs"
)

translations.define("CumulativeShippingCost.cost",
    ca = u"Cost",
    es = u"Coste",
    en = u"Cost"
)

# Tax
#------------------------------------------------------------------------------
translations.define("Tax",
    ca = u"Impost",
    es = u"Impuesto",
    en = u"Tax"
)

translations.define("Tax-plural",
    ca = u"Impostos",
    es = u"Impuestos",
    en = u"Taxes"
)

# CumulativeTax
#------------------------------------------------------------------------------
translations.define("CumulativeTax",
    ca = u"Impost acumulatiu",
    es = u"Impuesto acumulativo",
    en = u"Cumulative tax"
)

translations.define("CumulativeTax-plural",
    ca = u"Impostos acumulatius",
    es = u"Impuestos acumulativos",
    en = u"Cumulative taxes"
)

translations.define("CumulativeTax.cost",
    ca = u"Import",
    es = u"Importe",
    en = u"Cost"
)

# PercentageTax
#------------------------------------------------------------------------------
translations.define("PercentageTax",
    ca = u"Impost percentual",
    es = u"Impuesto porcentual",
    en = u"Percentage tax"
)

translations.define("PercentageTax-plural",
    ca = u"Impostos percentuals",
    es = u"Impuestos porcentuales",
    en = u"Percentage taxes"
)

translations.define("PercentageTax.percentage",
    ca = u"Percentatge",
    es = u"Porcentaje",
    en = u"Percentage"
)

# Views
#------------------------------------------------------------------------------
translations.define("woost.extensions.shop.ShopOrderTable product header",
    ca = u"Producte",
    es = u"Producto",
    en = u"Product"
)

translations.define("woost.extensions.shop.ShopOrderTable quantity header",
    ca = u"Unitats",
    es = u"Unidades",
    en = u"Units"
)

translations.define("woost.extensions.shop.ShopOrderTable price header",
    ca = u"Preu",
    es = u"Precio",
    en = u"Price"
)

translations.define("woost.extensions.shop.ShopOrderTable total header",
    ca = u"Total",
    es = u"Total",
    en = u"Total"
)

translations.define("woost.extensions.shop.ShopOrderTable shipping costs",
    ca = u"Costos d'enviament",
    es = u"Costes de envío",
    en = u"Shipping costs"
)

translations.define("woost.extensions.shop.ShopOrderTable taxes",
    ca = u"Impostos",
    es = u"Impuestos",
    en = u"Taxes"
)

translations.define("woost.extensions.shop.ShopOrderTable total",
    ca = u"Total",
    es = u"Total",
    en = u"Total"
)

translations.define("woost.extensions.shop.ShoppingBasket remove entry",
    ca = u"Eliminar",
    es = u"Eliminar",
    en = u"Delete"
)

translations.define("woost.extensions.shop.ShoppingBasket update button",
    ca = u"Actualitzar preu",
    es = u"Actualizar precio",
    en = u"Update"
)

# UserFilter
#------------------------------------------------------------------------------
translations.define(
    "woost.extensions.shop.userfilter.ShopOrderCostFilter-instance",
    ca = u"Cost de la comanda",
    es = u"Coste del pedido ",
    en = u"Shop order cost"
)

translations.define("ShopOrderCostFilter.include_shipping",
    ca = u"Costos d'enviament inclosos",
    es = u"Costes de envío incluidos",
    en = u"Shipping costs included"
)

translations.define("ShopOrderCostFilter.include_discounts",
    ca = u"Descomptes inclosos",
    es = u"Descuentos incluidos",
    en = u"Discounts included"
)

translations.define("ShopOrderCostFilter.include_taxes",
    ca = u"Impostos inclosos",
    es = u"Impuestos incluidos",
    en = u"Taxes included"
)

# ShopController
#------------------------------------------------------------------------------
translations.define("woost.extensions.shop Product controller title",
    ca = u"Controlador de producte",
    es = u"Controlador de producto",
    en = u"Product controller"
)

