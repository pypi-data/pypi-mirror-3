#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2009
"""
from cocktail.translations import translations, DATE_STYLE_TEXT
from cocktail.translations.helpers import plural2
from woost.models import Site

# ECommerceExtension
#------------------------------------------------------------------------------
translations.define("ECommerceExtension.pricing",
    ca = u"Preus",
    es = u"Precios",
    en = u"Pricing",
    fr = u"Prix"
)

translations.define("ECommerceExtension.shipping_costs",
    ca = u"Costos d'enviament",
    es = u"Costes de envío",
    en = u"Shipping costs",
    fr = u"Frais d'expédition"
)

translations.define("ECommerceExtension.taxes",
    ca = u"Taxes",
    es = u"Tasas",
    en = u"Taxes",
    fr = u"Taux"
)

translations.define("ECommerceExtension.order_steps",
    ca = u"Passos de la compra",
    es = u"Pasos de la compra",
    en = u"Order steps",
    fr = u"Étapes à suivre pour l'achat"
)

translations.define("ECommerceExtension.payment_types",
    ca = u"Tipus de pagament",
    es = u"Tipos de pago",
    en = u"Payment types",
    fr = u"Type de paiement"
)

translations.define("ECommerceExtension.payment_types-payment_gateway",
    ca = u"Pagament en línia",
    es = u"Pago en línea",
    en = u"On-line payment",
    fr = u"Paiement on-line"
)

translations.define("ECommerceExtension.payment_types-transfer",
    ca = u"Transferència",
    es = u"Transferencia",
    en = u"Transfer",
    fr = u"Transfert"
)

translations.define("ECommerceExtension.payment_types-cash_on_delivery",
    ca = u"Contra reemborsament",
    es = u"Contra reembolso",
    en = u"Cash on delivery",
    fr = u"Contre remboursement"
)

# ECommerceProduct
#------------------------------------------------------------------------------
translations.define("ECommerceProduct",
    ca = u"Producte",
    es = u"Producto",
    en = u"Product",
    fr = u"Produit"
)

translations.define("ECommerceProduct-plural",
    ca = u"Productes",
    es = u"Productos",
    en = u"Products",
    fr = u"Produits"
)

translations.define("ECommerceProduct.product_data",
    ca = u"Dades del producte",
    es = u"Datos del producto",
    en = u"Product data",
    fr = u"Détails sur le produit"
)

translations.define("ECommerceProduct.description",
    ca = u"Descripció",
    es = u"Descripción",
    en = u"Description",
    fr = u"Description"
)

translations.define("ECommerceProduct.price",
    ca = u"Preu",
    es = u"Precio",
    en = u"Price",
    fr = u"Prix"
)

translations.define("ECommerceProduct.weight",
    ca = u"Pes",
    es = u"Peso",
    en = u"Weight",
    fr = u"Poids"
)

translations.define("ECommerceProduct.attachments",
    ca = u"Adjunts",
    es = u"Adjuntos",
    en = u"Attachments",
    fr = u"Pièces jointes"
)

translations.define("ECommerceProduct.purchase_model",
    ca = u"Model de compra",
    es = u"Modelo de compra",
    en = u"Purchase model",
    fr = u"Achat modèle"
)

translations.define("ECommerceProduct.purchases",
    ca = u"Compres",
    es = u"Compras",
    en = u"Purchases",
    fr = u"Achats"
)

translations.define("ECommerceProduct.template",
    ca = u"Plantilla",
    es = u"Plantilla",
    en = u"Template",
    fr = u"Modèle"
)

# ECommerceOrder
#------------------------------------------------------------------------------
translations.define("ECommerceOrder",
    ca = u"Comanda",
    es = u"Pedido",
    en = u"Shop order",
    fr = u"Commande"
)

translations.define("ECommerceOrder-plural",
    ca = u"Comandes",
    es = u"Pedidos",
    en = u"Shop orders",
    fr = u"Commandes"
)

translations.define("ECommerceOrder.customer",
    ca = u"Client",
    es = u"Cliente",
    en = u"Customer",
    fr = u"Client"
)

translations.define("ECommerceOrder.shipping_info",
    ca = u"Direcció d'enviament",
    es = u"Dirección de envío",
    en = u"Shipping address",
    fr = u"Adresse de livraison"
)

translations.define("ECommerceOrder.address",
    ca = u"Adreça",
    es = u"Dirección",
    en = u"Address",
    fr = u"Adresse"
)

translations.define("ECommerceOrder.town",
    ca = u"Població",
    es = u"Población",
    en = u"Town",
    fr = u"Ville"
)

translations.define("ECommerceOrder.region",
    ca = u"Estat o província",
    es = u"Estado o provincia",
    en = u"State or province",
    fr = u"État ou province"
)

translations.define("ECommerceOrder.country",
    ca = u"País",
    es = u"País",
    en = u"Country",
    fr = u"Pays"
)

translations.define("ECommerceOrder.postal_code",
    ca = u"Codi postal",
    es = u"Código postal",
    en = u"Postal code",
    fr = u"Code postal"
)

translations.define("ECommerceOrder.language",
    ca = u"Idioma",
    es = u"Idioma",
    en = u"Language",
    fr = u"Langue"
)

translations.define("ECommerceOrder.status",
    ca = u"Estat",
    es = u"Estado",
    en = u"State",
    fr = u"État"
)

translations.define("ECommerceOrder.status-shopping",
    ca = u"En curs",
    es = u"En curso",
    en = u"Shopping",
    fr = u"En cours"
)

translations.define("ECommerceOrder.status-payment_pending",
    ca = u"Pendent de pagament",
    es = u"Pago pendiente",
    en = u"Payment pending",
    fr = u"Paiement en attente"
)

translations.define("ECommerceOrder.status-accepted",
    ca = u"Acceptada",
    es = u"Aceptada",
    en = u"Accepted",
    fr = u"Accepté"
)

translations.define("ECommerceOrder.status-refund",
    ca = u"Devolució",
    es = u"Devolución",
    en = u"Refund",
    fr = u"Remboursement"
)

translations.define("ECommerceOrder.status-failed",
    ca = u"Cancel·lada",
    es = u"Cancelada",
    en = u"Cancelled",
    fr = u"Annulé"
)

translations.define("ECommerceOrder.purchases",
    ca = u"Contingut de la comanda",
    es = u"Contenido del pedido",
    en = u"Purchases",
    fr = u"Contenu de la commande"
)

translations.define("ECommerceOrder.billing",
    ca = u"Facturació",
    es = u"Facturación",
    en = u"Billing",
    fr = u"Facturation"
)

translations.define("ECommerceOrder.total_price",
    ca = u"Preu",
    es = u"Precio",
    en = u"Price",
    fr = u"Prix"
)

translations.define("ECommerceOrder.pricing",
    ca = u"Modificacions al preu",
    es = u"Modificaciones al precio",
    en = u"Pricing",
    fr = u"Modifications au prix"
)

translations.define("ECommerceOrder.total_shipping_costs",
    ca = u"Costos d'enviament",
    es = u"Costes de envío",
    en = u"Shipping costs",
    fr = u"Frais d'expédition"
)

translations.define("ECommerceOrder.shipping_costs",
    ca = u"Costos d'enviament aplicats",
    es = u"Costes de envío aplicados",
    en = u"Applied shipping costs",
    fr = u"Frais d'expédition appliqués"
)

translations.define("ECommerceOrder.total_taxes",
    ca = u"Taxes",
    es = u"Tasas",
    en = u"Taxes",
    fr = u"Impôts"
)

translations.define("ECommerceOrder.taxes",
    ca = u"Taxes aplicades",
    es = u"Tasas aplicadas",
    en = u"Applied taxes",
    fr = u"Taxes appliquées"
)

translations.define("ECommerceOrder.total",
    ca = u"Total",
    es = u"Total",
    en = u"Total",
    fr = u"Total"
)

translations.define("ECommerceOrder.payment_type",
    ca = u"Tipus de pagament",
    es = u"Tipo de pago",
    en = u"Payment type",
    fr = u"Type de paiement"
)

translations.define("ECommerceOrder.payment_type-payment_gateway",
    ca = u"Pagament en línia",
    es = u"Pago en línea",
    en = u"On-line payment",
    fr = u"Paiment on-line "
)

translations.define("ECommerceOrder.payment_type-transfer",
    ca = u"Transferència",
    es = u"Transferencia",
    en = u"Transfer",
    fr = u"Transfert"
)

translations.define("ECommerceOrder.payment_type-cash_on_delivery",
    ca = u"Contra reemborsament",
    es = u"Contra reembolso",
    en = u"Cash on delivery",
    fr = u"Contre remboursement"
)

translations.define("woost.extensions.ECommerceOrder description for gateway",
    ca = u"Comanda de %s",
    es = u"Pedido de %s",
    en = u"Order at %s",
    fr = u"Commande de %s"
)

# ECommercePurchase
#------------------------------------------------------------------------------
translations.define("ECommercePurchase",
    ca = u"Línia de comanda",
    es = u"Linea de pedido",
    en = u"Purchase",
    fr = u"Achat en ligne"
)

translations.define("ECommercePurchase-plural",
    ca = u"Línies de comanda",
    es = u"Lineas de pedido",
    en = u"Purchases",
    fr = u"Achats en ligne"
)

translations.define("ECommercePurchase.order",
    ca = u"Comanda",
    es = u"Pedido",
    en = u"Order",
    fr = u"Commande"
)

translations.define("ECommercePurchase.product",
    ca = u"Producte",
    es = u"Producto",
    en = u"Product",
    fr = u"Produit"
)

translations.define("ECommercePurchase.quantity",
    ca = u"Quantitat",
    es = u"Cantidad",
    en = u"Quantity",
    fr = u"Quantité"
)

translations.define("ECommercePurchase.billing",
    ca = u"Facturació",
    es = u"Facturación",
    en = u"Billing",
    fr = u"Facturation"
)

translations.define("ECommercePurchase.total_price",
    ca = u"Preu",
    es = u"Precio",
    en = u"Price",
    fr = u"Prix"
)

translations.define("ECommercePurchase.pricing",
    ca = u"Modificacions al preu",
    es = u"Modificaciones al precio",
    en = u"Pricing",
    fr = u"Modifications au prix"
)

translations.define("ECommercePurchase.total_shipping_costs",
    ca = u"Costos d'enviament",
    es = u"Costes de envío",
    en = u"Shipping costs",
    fr = u"Frais d'expédition"
)

translations.define("ECommercePurchase.shipping_costs",
    ca = u"Costos d'enviament aplicats",
    es = u"Costes de envío aplicados",
    en = u"Applied shipping costs",
    fr = u"Frais d'expédition appliqués"
)

translations.define("ECommercePurchase.total_taxes",
    ca = u"Taxes",
    es = u"Tasas",
    en = u"Taxes",
    fr = u"Impôts"
)

translations.define("ECommercePurchase.taxes",
    ca = u"Taxes aplicades",
    es = u"Tasas aplicadas",
    en = u"Applied taxes",
    fr = u"Impôts appliqués"
)

translations.define("ECommercePurchase.total",
    ca = u"Total",
    es = u"Total",
    en = u"Total",
    fr = u"Total"
)

# ECommerceBillingConcept
#------------------------------------------------------------------------------
translations.define("ECommerceBillingConcept",
    ca = u"Concepte de facturació",
    es = u"Concepto de facturación",
    en = u"Billing concept",
    fr = u"Concept de facturation"
)

translations.define("ECommerceBillingConcept-plural",
    ca = u"Conceptes de facturació",
    es = u"Conceptos de facturación",
    en = u"Billing concepts",
    fr = u"Concepts de facturation"
)


translations.define("ECommerceBillingConcept.title",
    ca = u"Títol",
    es = u"Título",
    en = u"Title",
    fr = u"Titre"
)

translations.define("ECommerceBillingConcept.enabled",
    ca = u"Activa",
    es = u"Activa",
    en = u"Enabled",
    fr = u"Active"
)

translations.define("ECommerceBillingConcept.start_date",
    ca = u"Data d'inici",
    es = u"Fecha de inicio",
    en = u"Start date",
    fr = u"Date de début"
)

translations.define("ECommerceBillingConcept.end_date",
    ca = u"Data de fi",
    es = u"Fecha de fin",
    en = u"End date",
    fr = u"Date de fin"
)

translations.define("ECommerceBillingConcept.hidden",
    ca = u"Ocult",
    es = u"Oculto",
    en = u"Hidden",
    fr = u"Invisible"
)

translations.define("ECommerceBillingConcept.scope",
    ca = u"Àmbit",
    es = u"Ámbito",
    en = u"Scope",
    fr = u"Champ d'application"
)

translations.define("ECommerceBillingConcept.scope-order",
    ca = u"Comanda",
    es = u"Pedido",
    en = u"Order",
    fr = u"Commande"
)

translations.define("ECommerceBillingConcept.scope-purchase",
    ca = u"Línia de comanda",
    es = u"Linea de pedido",
    en = u"Purchase",
    fr = u"Commande en ligne"
)

translations.define("ECommerceBillingConcept.condition",
    ca = u"Condició",
    es = u"Condición",
    en = u"Condition",
    fr = u"Condition"
)

translations.define("ECommerceBillingConcept.eligible_countries",
    ca = u"Països",
    es = u"Paises",
    en = u"Countries",
    fr = u"Pays"
)

translations.define("ECommerceBillingConcept.eligible_products",
    ca = u"Productes",
    es = u"Productos",
    en = u"Products",
    fr = u"Produits"
)

translations.define("ECommerceBillingConcept.eligible_roles",
    ca = u"Rols",
    es = u"Roles",
    en = u"Roles",
    fr = u"Roles"
)

translations.define("ECommerceBillingConcept.implementation",
    ca = u"Valor",
    es = u"Valor",
    en = u"Value",
    fr = u"Valeur"
)

# Initialization
#------------------------------------------------------------------------------
translations.define("woost.extensions.ecommerce.catalog_page.title",
    ca = u"Botiga",
    es = u"Tienda",
    en = u"Shop",
    fr = u"Boutique"
)

translations.define("woost.extensions.ecommerce.catalog_controller.title",
    ca = u"Controlador de catàleg de productes",
    es = u"Controlador de catálogo de productos",
    en = u"Product catalog controller",
    fr = u"Controleur de catalogue de produits"
)

translations.define("woost.extensions.ecommerce.catalog_template.title",
    ca = u"Plantilla de catàleg de productes",
    es = u"Plantilla de catálogo de productos",
    en = u"Product catalog template",
    fr = u"Modèle de catalogue de produits"
)

translations.define("woost.extensions.ecommerce.basket_page.title",
    ca = u"Cistella de la compra",
    es = u"Cesta de la compra",
    en = u"Shopping basket",
    fr = u"Panier"
)

translations.define("woost.extensions.ecommerce.basket_controller.title",
    ca = u"Controlador per la cistella de la compra",
    es = u"Controlador para la Cesta de la compra",
    en = u"Shopping basket controller",
    fr = u"Controleur de panier"
)

translations.define("woost.extensions.ecommerce.basket_template.title",
    ca = u"Plantilla per cistella de la compra",
    es = u"Plantilla para cesta de la compra",
    en = u"Shopping basket template",
    fr = u"Modèle de panier"
)

translations.define("woost.extensions.ecommerce.checkout_page.title",
    ca = u"Dades de la comanda",
    es = u"Datos del pedido",
    en = u"Checkout",
    fr = u"Détails de la commande"
)

translations.define("woost.extensions.ecommerce.checkout_controller.title",
    ca = u"Controlador de recollida de dades de comanda de la botiga",
    es = u"Controlador de recogida de datos de pedido de la tienda",
    en = u"Shop checkout controller",
    fr = u"Controleur de prise de détails de la commande"
)

translations.define("woost.extensions.ecommerce.checkout_template.title",
    ca = u"Plantilla de recollida de dades de comanda de la botiga",
    es = u"Plantilla de recojida de datos de pedido de la tienda",
    en = u"Shop checkout template",
    fr = u"Modèle de prise de détails de la commande"
)

translations.define("woost.extensions.ecommerce.summary_page.title",
    ca = u"Sumari de la comanda",
    es = u"Sumario del pedido",
    en = u"Order summary",
    fr = u"Resumé de la commande"
)

translations.define("woost.extensions.ecommerce.summary_controller.title",
    ca = u"Controlador de sumari de comanda de la botiga",
    es = u"Controlador de sumario de pedido de la tienda",
    en = u"Shop order summary controller",
    fr = u"Controleur de resumé de la commande"
)

translations.define("woost.extensions.ecommerce.summary_template.title",
    ca = u"Plantilla de sumari de comanda de la botiga",
    es = u"Plantilla de sumario de pedido de la tienda",
    en = u"Shop order summary template",
    fr = u"Modèle de resumé de commande"
)

translations.define("woost.extensions.ecommerce.success_page.title",
    ca = u"Comanda completada",
    es = u"Pedido completado",
    en = u"Order completed",
    fr = u"Commande terminée"
)

translations.define("woost.extensions.ecommerce.success_page.body",
    ca = u"La teva comanda s'ha processat correctament.",
    es = u"Tu pedido se ha procesado correctamente.",
    en = u"Your order has been completed successfully.",
    fr = u"Votre commande a été traitée avec succès."
)

translations.define("woost.extensions.ecommerce.failure_page.title",
    ca = u"Comanda cancel·lada",
    es = u"Pedido cancelado",
    en = u"Order cancelled",
    fr = u"Commande annulée"
)

translations.define("woost.extensions.ecommerce.failure_page.body",
    ca = u"La teva comanda ha estat cancel·lada.",
    es = u"Tu pedido ha sido cancelado.",
    en = u"Your order has been cancelled.",
    fr = u"Votre commande a été annulée."
)

translations.define("woost.extensions.ecommerce.product_controller.title",
    ca = u"Controlador de detall de producte",
    es = u"Controlador de detalle de producto",
    en = u"Shop product detail controller",
    fr = u"Contrôleur de détail du produit"
)

translations.define("woost.extensions.ecommerce.product_template.title",
    ca = u"Plantilla de detall de producte",
    es = u"Plantilla de detalle de producto",
    en = u"Shop product detail template",
    fr = u"Modèle de détail du produit"
)

translations.define("woost.extensions.ecommerce.ecommerceorder_completed_trigger.title",
    ca = u"Enviar resum de la comanda",
    es = u"Enviar resumen del pedido",
    en = u"Send order summary",
    fr = u"Envoyer résumé de la commande"
)

translations.define("woost.extensions.ecommerce.ecommerceorder_completed_emailtemplate.title",
    ca = u"Resum de la comanda",
    es = u"Resumen del pedido",
    en = u"Order summary",
    fr = u"Résumé de la commande"
)

translations.define("woost.extensions.ecommerce.incoming_order.trigger.title",
    ca = u"Enviar resum de la comanda",
    es = u"Enviar resumen del pedido",
    en = u"Send order summary"
)

translations.define("woost.extensions.ecommerce.incoming_order.email_template.title",
    ca = u"Notificació de nova comanda",
    es = u"Notificación de nuevo pedido",
    en = u"New shop order notification"
)

translations.define("woost.extensions.ecommerce.incoming_order.edit_link",
    ca = u"Obrir la comanda",
    es = u"Abrir el pedido",
    en = u"Edit the order"
)

# Notices
#------------------------------------------------------------------------------
translations.define(
    "woost.extensions.ecommerce.product_added_notice",
    ca = lambda product: 
        u"S'ha afegit <strong>%s</strong> a la cistella"
        % translations(product),
    es = lambda product: 
        u"Se ha añadido <strong>%s</strong> a la cesta"
        % translations(product),
    en = lambda product: 
        u"<strong>%s</strong> added to the shopping basket"
        % translations(product),
    fr = lambda product: 
        u"<strong>%s</strong> ajouté au panier"
        % translations(product)
)


translations.define(
    "woost.extensions.ecommerce.set_quantities_notice",
    ca = u"S'han actualitzat les quantitats",
    es = u"Se han actualizado las cantidades",
    en = u"Product quantities have been updated",
    fr = u"Les montants ont été mis à jour"
)

translations.define(
    "woost.extensions.ecommerce.delete_purchase_notice",
    ca = lambda product: 
        u"S'ha tret <strong>%s</strong> de la cistella"
        % translations(product),
    es = lambda product: 
        u"Se ha quitado <strong>%s</strong> de la cesta"
        % translations(product),
    en = lambda product: 
        u"<strong>%s</strong> has been removed from the shopping basket"
        % translations(product),
    fr = lambda product: 
        u"<strong>%s</strong> a été effacé du panier"
        % translations(product)
)

translations.define(
    "woost.extensions.ecommerce.empty_basket_notice",
    ca = u"S'ha buidat la cistella",
    es = u"Se ha vaciado la cesta",
    en = u"The shopping basket has been cleared",
    fr = u"Le panier a été effacé"
)

# ProductView
#------------------------------------------------------------------------------
translations.define(
    "woost.extensions.ecommerce.ProductPage.back_link",
    ca = u"Tornar al catàleg",
    es = u"Volver al catálogo",
    en = u"Return to the catalog",
    fr = u"Retour au catalogue"
)

translations.define(
    "woost.extensions.ecommerce.ProductPage.checkout_button",
    ca = u"Continuar la compra",
    es = u"Continuar la compra",
    en = u"Checkout",
    fr = u"Continuer les achats"
)

# OrderStep
#------------------------------------------------------------------------------
translations.define(
    "woost.extensions.ecommerce.OrderStep.catalog_button",
    ca = u"Veure més productes",
    es = u"Ver más productos",
    en = u"See more products",
	fr = u"Voire plus products"
)

translations.define(
    "woost.extensions.ecommerce.OrderStep.back_button",
    ca = u"Tornar endarrere",
    es = u"Volver atrás",
    en = u"Go back",
	fr = u"Retourner"
)

translations.define(
    "woost.extensions.ecommerce.OrderStep.proceed_button",
    ca = u"Continuar la compra",
    es = u"Continuar la compra",
    en = u"Proceed",
	fr = u"Procédez"
)

translations.define(
    "woost.extensions.ecommerce.OrderStep.submit_button",
    ca = u"Confirmar la compra",
    es = u"Confirmar la compra",
    en = u"Submit order",
	fr = u"Confirmer l'achat"
)

# BasketPage
#------------------------------------------------------------------------------
translations.define(
    "woost.extensions.ecommerce.BasketPage.back_link",
    ca = u"Tornar al catàleg",
    es = u"Volver al catálogo",
    en = u"Return to the catalog",
	fr = u"Retourner au catalogue"
)

# BasketView
#------------------------------------------------------------------------------
translations.define(
    "Basket.product",
    ca = u"Producte",
    es = u"Producto",
    en = u"Product",
	fr = u"Produit"
)

translations.define(
    "Basket.quantity",
    ca = u"Quantitat",
    es = u"Cantidad",
    en = u"Quantity",
	fr = u"Quantité"
)

translations.define(
    "Basket.price",
    ca = u"Preu",
    es = u"Precio",
    en = u"Price",
	fr = u"Prix"
)

translations.define(
    "Basket.subtotal",
    ca = u"Subtotal",
    es = u"Subtotal",
    en = u"Subtotal",
	fr = u"Subtotal"
)

translations.define(
    "Basket.taxes",
    ca = u"Taxes",
    es = u"Tasas",
    en = u"Taxes",
	fr = u"Impôts"
)

translations.define(
    "Basket.total",
    ca = u"Total",
    es = u"Total",
    en = u"Total",
	fr = u"Total" 
)

translations.define(
    "SetQuantitiesForm-MinValueError",
    ca = u"No es pot demanar menys d'una unitat d'un producte",
    es = u"No se puede solicitar menos de una unidad de un producto",
    en = u"Can't request less than one unit of a product",
	fr = u"Vous ne pouvez pas demander moins d'une unité d'un produit"
)

translations.define(
    "woost.extensions.ecommerce.BasketView.basket_table_total_header",
    ca = u"Total",
    es = u"Total",
    en = u"Total",
	fr = u"Total"
)

translations.define(
    "woost.extensions.ecommerce.BasketView.delete_purchase_button",
    ca = u"Treure",
    es = u"Quitar",
    en = u"Remove",
	fr = u"Supprimer"
)

translations.define(
    "woost.extensions.ecommerce.BasketView.empty_basket_button",
    ca = u"Buidar la cistella",
    es = u"Vaciar la cesta",
    en = u"Empty the basket",
	fr = u"Vider le panier"
)

translations.define(
    "woost.extensions.ecommerce.BasketView.set_quantities_button",
    ca = u"Establir quantitats",
    es = u"Establecer cantidades",
    en = u"Set quantities",
	fr = u"Fixer les montants"
)

translations.define(
    "woost.extensions.ecommerce.BasketView.empty_basket_notice",
    ca = u"La cistella de la compra està buida.",
    es = u"La cesta de la compra está vacía.",
    en = u"The shopping basket is empty.",
	fr = u"Le panier est vide."
)

translations.define("woost.extensions.ecommerce.BasketView.shipping_costs",
    ca = u"Costos d'enviament",
    es = u"Costes de envío",
    en = u"Shipping costs",
	fr = u"Frais d'expédition"
)

translations.define("woost.extensions.ecommerce.BasketView.taxes",
    ca = u"Taxes",
    es = u"Tasas",
    en = u"Taxes",
	fr = u"Taux"
)

# Discount
#------------------------------------------------------------------------------
translations.define("woost.extensions.ecommerce.Discount.end_date",
    ca = lambda end_date:
        u"fins al " + translations(end_date, style = DATE_STYLE_TEXT),
    es = lambda end_date:
        u"hasta el " + translations(end_date, style = DATE_STYLE_TEXT),
    en = lambda end_date:
        u"until " + translations(end_date, style = DATE_STYLE_TEXT),
	fr = lambda end_date:
        u"jusqu'à " + translations(end_date, style = DATE_STYLE_TEXT)	
)

# Basket indicator
#------------------------------------------------------------------------------
translations.define("woost.extensions.ecommerce.BasketIndicator",
    ca = lambda count: 
        plural2(
            count,
            u"<strong>1</strong> producte", 
            u"<strong>%d</strong> productes" % count
        ) + u" a la cistella",
    es = lambda count: 
        plural2(
            count,
            u"<strong>1</strong> producto", 
            u"<strong>%d</strong> productos" % count
        ) + u" en la cesta",
    en = lambda count: 
        plural2(
            count,
            u"<strong>1</strong> product", 
            u"<strong>%d</strong> products" % count
        ) + u" in the shopping basket",
	fr = lambda count: 
        plural2(
            count,
            u"<strong>1</strong> produit", 
            u"<strong>%d</strong> produits" % count
        ) + u" au panier"
)

# SummaryOrderStep
#------------------------------------------------------------------------------
translations.define(
    "woost.extensions.ecommerce.SummaryOrderStep.modify_basket_link",
    ca = u"Modificar el contingut de la comanda",
    es = u"Modificar el contenido del pedido",
    en = u"Edit the shopping basket",
	fr = u"Modifier le contenu de l'ordre"
)

translations.define(
    "woost.extensions.ecommerce.SummaryOrderStep.modify_checkout_link",
    ca = u"Modificar les dades de la comanda",
    es = u"Modificar los datos del pedido",
    en = u"Edit checkout data",
	fr = u"Modifier les données checkout"
)

# AddProductForm
#------------------------------------------------------------------------------
translations.define("woost.extensions.ecommerce.AddProductForm.title",
    ca = u"Afegir a la cistella",
    es = u"Añadir a la cesta",
    en = u"Add to basket",
	fr = u"Ajouter au panier"
)

translations.define("woost.extensions.ecommerce.AddProductForm.submit_button",
    ca = u"Afegir",
    es = u"Añadir",
    en = u"Add",
	fr = u"Ajouter"
)

translations.define(
    "woost.extensions.ecommerce.AddProductForm.product_added_back_button",
    ca = u"Veure més productes",
    es = u"Ver más productos",
    en = u"Keep shopping",
	fr = u"Voir plus de produits"
)

translations.define(
    "woost.extensions.ecommerce.AddProductForm.product_added_forward_button",
    ca = u"Comprar",
    es = u"Comprar",
    en = u"Checkout",
	fr = u"Acheter"
)

# ECommerceOrderCompletedTrigger
#------------------------------------------------------------------------------
translations.define("ECommerceOrderCompletedTrigger",
    ca = u"Disparador de comanda completada",
    es = u"Disparador de pedido completado",
    en = u"Order completed trigger",
	fr = u"Order completed trigger"
)

translations.define("ECommerceOrderCompletedTrigger-plural",
    ca = u"Disparadors de comanda completada",
    es = u"Disparadores de pedido completado",
    en = u"Order completed triggers",
	fr = u"Order completed trigger"
)

# IncomingOrderTrigger
#------------------------------------------------------------------------------
translations.define("IncomingOrderTrigger",
    ca = u"Disparador de nova comanda",
    es = u"Disparador de nuevo pedido",
    en = u"Incoming order trigger"
)

translations.define("IncomingOrderTrigger-plural",
    ca = u"Disparadors de nova comanda",
    es = u"Disparadores de nuevo pedido",
    en = u"Incoming order triggers"
)

# OrderConfirmationMessage
#------------------------------------------------------------------------------
translations.define(
    "woost.extensions.OrderConfirmationMessage.product_subtotal_cell",
    ca = u"Subtotal",
    es = u"Subtotal",
    en = u"Subtotal",
	fr = u"Subtotal"
)

translations.define(
    "woost.extensions.OrderConfirmationMessage.product_footer_cell",
    ca = u"Total",
    es = u"Total",
    en = u"Total",
	fr = u"Total"
)

translations.define(
    "woost.extensions.ecommerce.OrderConfirmationMessage.introduction",
    ca = u"Gràcies per la teva compra! Hem rebut la teva comanda "
        u"correctament, i te la farem arribar amb la major brevetat possible. "
        u"A continuació pots veure els productes que has comprat i les dades "
        u"personals i d'enviament que has facilitat. Et recomanem que "
        u"conservis o imprimeixis aquest correu, com a comprovant de la "
        u"compra i per facilitar-ne qualsevol possible gestió.",
    es = u"Gracias por tu compra! Hemos recibido tu pedido correctamente, y "
        u"te lo enviaremos en breve. A continuación te recordamos los "
        u"productos que has comprado y los datos personales y de envío que "
        u"nos has facilitado. Te recomendamos que conserves este correo, como "
        u"comprovante de la compra y para facilitar cualquier possible "
        u"gestión.",
    en = u"Thank you for your purchase! We have received your order, and will "
        u"ship it to you as soon as possible. This message contains a summary "
        u"of the items you purchased, and of your personal and shipping "
        u"information. We recommend you keep or print this message, to use as "
        u"a purchase receipt.",
	fr = u"Merci pour votre achat! Nous avons reçu votre commande "
        u"correctement, et nous alons l'envoyer le plus tôt possible. "
        u"Ci-dessous vous pouvez voir les produits que vous avez acheté et "
        u"les données personnelles que vous nous avez fourni. Nous "
        u"recommandons conserver ou imprimer cet email comme preuve de "
        u"l'achat et pour faciliter toute gestion."
)

