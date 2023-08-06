#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2009
"""
from cocktail.translations import translations

# Payments extension
#------------------------------------------------------------------------------
translations.define("PaymentsExtension.payment_gateway",
    ca = u"Passarel·la de pagaments",
    es = u"Pasarela de pagos",
    en = u"Payment gateway"
)

# TransactionNotifiedTrigger
#------------------------------------------------------------------------------
translations.define("TransactionNotifiedTrigger",
    ca = u"Disparador de notificació de pagament",
    es = u"Disparador de notificación de pago",
    en = u"Payment notification trigger"
)

translations.define("TransactionNotifiedTrigger-plural",
    ca = u"Disparadors de notificació de pagament",
    es = u"Disparadores de notificación de pago",
    en = u"Payment notification triggers"
)

# PaymentGateway
#------------------------------------------------------------------------------
translations.define("PaymentGateway",
    ca = u"Passarel·la de pagaments",
    es = u"Pasarela de pagos",
    en = u"Payment gateway"
)

translations.define("PaymentGateway-plural",
    ca = u"Passarel·les de pagaments",
    es = u"Pasarelas de pagos",
    en = u"Payment gateways"
)

translations.define("PaymentGateway.label",
    ca = u"Etiqueta",
    es = u"Etiqueta",
    en = u"Label"
)

translations.define("PaymentGateway.label-explanation",
    ca = u"Etiqueta utilitzada per mostrar als usuaris",
    es = u"Etiqueta utilizada para mostrar a los usuarios",
    en = u"Label showed to the users"
)

translations.define("PaymentGateway.test_mode",
    ca = u"Mode de proves",
    es = u"Modo de pruebas",
    en = u"Test mode"
)

translations.define("PaymentGateway.currency",
    ca = u"Divisa",
    es = u"Divisa",
    en = u"Currency"
)

# Pasat4bPaymentGateway
#------------------------------------------------------------------------------
translations.define("Pasat4bPaymentGateway",
    ca = u"Pasat 4B",
    es = u"Pasat 4B",
    en = u"Pasat 4B"
)

translations.define("Pasat4bPaymentGateway-plural",
    ca = u"Pasat 4B",
    es = u"Pasat 4B",
    en = u"Pasat 4B"
)

translations.define("Pasat4bPaymentGateway.merchant_code",
    ca = u"Codi de comerç",
    es = u"Código de comercio",
    en = u"Merchant code"
)

translations.define("Pasat4bPaymentGateway.label default",
    ca = u"Targeta de crèdit",
    es = u"Tarjeta de crédito",
    en = u"Credit card"
)

# SISPaymentGateway
#------------------------------------------------------------------------------
translations.define("SISPaymentGateway",
    ca = u"SIS/Sermepa",
    es = u"SIS/Sermepa",
    en = u"SIS/Sermepa"
)

translations.define("SISPaymentGateway-plural",
    ca = u"SIS/Sermepa",
    es = u"SIS/Sermepa",
    en = u"SIS/Sermepa"
)

translations.define("SISPaymentGateway.merchant_code",
    ca = u"Codi de comerç",
    es = u"Código de comercio",
    en = u"Merchant code"
)

translations.define("SISPaymentGateway.merchant_name",
    ca = u"Nom del comerç",
    es = u"Nombre del comercio",
    en = u"Merchant name"
)

translations.define("SISPaymentGateway.merchant_terminal",
    ca = u"Número de terminal",
    es = u"Número de terminal",
    en = u"Terminal number"
)

translations.define("SISPaymentGateway.merchant_secret_key",
    ca = u"Clau secreta",
    es = u"Clave secreta",
    en = u"Secret key"
)

translations.define("SISPaymentGateway.payment_successful_page",
    ca = u"Pàgina de confirmació de pagament",
    es = u"Página de confirmación de pago",
    en = u"Payment successful page"
)

translations.define("SISPaymentGateway.payment_failed_page",
    ca = u"Pàgina de pagament fallit",
    es = u"Página de pago fallido",
    en = u"Payment failed page"
)

translations.define("SISPaymentGateway.label default",
    ca = u"Targeta de crèdit",
    es = u"Tarjeta de crédito",
    en = u"Credit card"
)

# DummyPaymentGateway
#------------------------------------------------------------------------------
translations.define("DummyPaymentGateway",
    ca = u"Passarel·la de pagaments fictícia",
    es = u"Pasarela de pagos ficticia",
    en = u"Dummy payment gateway"
)

translations.define("DummyPaymentGateway-plural",
    ca = u"Passarel·les de pagaments fictícies",
    es = u"Pasarelas de pagos ficticias",
    en = u"Dummy payment gateways"
)

translations.define("DummyPaymentGateway.payment_status",
    ca = u"Resultat dels pagaments",
    es = u"Resultado de los pagos",
    en = u"Payment outcome"
)

translations.define("DummyPaymentGateway.payment_successful_page",
    ca = u"Pàgina de confirmació de pagament",
    es = u"Página de confirmación de pago",
    en = u"Payment successful page"
)

translations.define("DummyPaymentGateway.payment_failed_page",
    ca = u"Pàgina de pagament fallit",
    es = u"Página de pago fallido",
    en = u"Payment failed page"
)

translations.define(
    "woost.extensions.payments.DummyPaymentGateway.payment_status "
    "accepted",
    ca = u"Acceptat",
    es = u"Aceptado",
    en = u"Accepted"
)

translations.define(
    "woost.extensions.payments.DummyPaymentGateway.payment_status "
    "failed",
    ca = u"Cancel·lat",
    es = u"Cancelado",
    en = u"Canceled"
)

# PayPalPaymentGateway
#------------------------------------------------------------------------------
translations.define("PayPalPaymentGateway",
    ca = u"PayPal",
    es = u"PayPal",
    en = u"PayPal"
)

translations.define("PayPalPaymentGateway-plural",
    ca = u"PayPal",
    es = u"PayPal",
    en = u"PayPal"
)

translations.define("PayPalPaymentGateway.business",
    ca = u"Compte de PayPal",
    es = u"Cuenta de PayPal",
    en = u"PayPal account"
)

translations.define("PayPalPaymentGateway.payment_successful_page",
    ca = u"Pàgina de confirmació de pagament",
    es = u"Página de confirmación de pago",
    en = u"Payment successful page"
)

translations.define("PayPalPaymentGateway.payment_failed_page",
    ca = u"Pàgina de pagament fallit",
    es = u"Página de pago fallido",
    en = u"Payment failed page"
)

translations.define("PayPalPaymentGateway.label default",
    ca = u"Targeta de crèdit / PayPal",
    es = u"Tarjeta de crédito / PayPal",
    en = u"Credit card / PayPal"
)

