#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2009
"""
from cocktail.events import when
from cocktail.modeling import underscore_to_capital
from cocktail.translations import (
    translations,
    set_language,
    language_context
)
from cocktail import schema
from cocktail.persistence import datastore
from woost.models import (
    Site,
    Extension,
    Publishable,
    Document,
    StandardPage,
    Template,
    Controller,
    EmailTemplate,
    User,
    Language
)
from woost.models.triggerresponse import SendEmailTriggerResponse

translations.define("ECommerceExtension",
    ca = u"Comerç online",
    es = u"Comercio online",
    en = u"E-commerce"
)

translations.define("ECommerceExtension-plural",
    ca = u"Comerç online",
    es = u"Comercio online",
    en = u"E-commerce"
)


class ECommerceExtension(Extension):

    def __init__(self, **values):
        Extension.__init__(self, **values)
        self.extension_author = u"Whads/Accent SL"
        self.set("description",
            u"""Permet vendre productes des del lloc web.""",
            "ca"
        )
        self.set("description",            
            u"""Permite vender productos des del sitio web.""",
            "es"
        )
        self.set("description",
            u"""Allows selling products online.""",
            "en"
        )

    def _load(self):

        extension = self

        from woost.extensions.ecommerce import (
            strings,
            ecommerceproduct,
            ecommerceorder,
            ecommercepurchase,
            ecommercebillingconcept,
            ecommerceordercompletedtrigger,
            imagefactories
        )
        from woost.extensions.ecommerce.ecommerceorder import ECommerceOrder

        # Add the necessary members to define pricing policies
        ECommerceExtension.members_order = [
            "payment_types",
            "pricing",
            "shipping_costs", 
            "taxes",
            "order_steps"
        ]

        available_payment_types = ("payment_gateway", "transfer", "cash_on_delivery")
        ECommerceOrder.payment_type.enumeration = available_payment_types

        ECommerceExtension.add_member(
            schema.Collection(
                "payment_types",
                items = schema.String(
                    enumeration = available_payment_types,
                    translate_value = lambda value, language = None, **kwargs:
                        translations(
                            "ECommerceExtension.payment_types-%s" % value,
                            language = language
                        ),
                ),
                min = 1
            )
        )

        ECommerceExtension.add_member(
            schema.Collection("pricing",
                items = schema.Reference(
                    type = ecommercebillingconcept.ECommerceBillingConcept
                ),
                bidirectional = True,
                related_end = schema.Collection(),
                integral = True
            )
        )

        ECommerceExtension.add_member(
            schema.Collection("shipping_costs",
                items = schema.Reference(
                    type = ecommercebillingconcept.ECommerceBillingConcept
                ),
                bidirectional = True,
                related_end = schema.Collection(),
                integral = True
            )
        )

        ECommerceExtension.add_member(
            schema.Collection("taxes",
                items = schema.Reference(
                    type = ecommercebillingconcept.ECommerceBillingConcept
                ),
                bidirectional = True,
                related_end = schema.Collection(),
                integral = True
            )
        )

        ECommerceExtension.add_member(
            schema.Collection("order_steps",
                items = schema.Reference(type = Publishable),
                related_end = schema.Collection()
            )
        )

        # If the payments extension is enabled, setup the payment gateway for
        # the shop
        from woost.extensions.payments import PaymentsExtension
        payments_ext = PaymentsExtension.instance

        if payments_ext.enabled:
            extension._setup_payment_gateway()
        
        # Create the pages for the shop the first time the extension runs
        self.install()

    def _setup_payment_gateway(self):
            
        from tpv import (
            Currency,
            Payment,
            PaymentItem,
            PaymentNotFoundError
        )
        from woost.extensions.payments.paymentgateway import PaymentGateway
        from woost.extensions.payments.transactionnotifiedtrigger \
            import launch_transaction_notification_triggers
        from woost.extensions.ecommerce.ecommerceorder import ECommerceOrder
        from woost.extensions.payments import PaymentsExtension

        payments_ext = PaymentsExtension.instance

        def get_payment(self, payment_id):

            order = ECommerceOrder.get_instance(int(payment_id))

            if order is None:
                raise PaymentNotFoundError(payment_id)
            
            payment = Payment()
            payment.id = order.id
            payment.description = order.get_description_for_gateway()
            payment.amount = order.total
            payment.order = order
            payment.currency = Currency(payments_ext.payment_gateway.currency)
            
            for purchase in order.purchases:
                payment.add(PaymentItem(
                    reference = str(purchase.product.id),
                    description = translations(purchase.product),
                    units = purchase.quantity,
                    price = purchase.total
                ))

            return payment

        PaymentGateway.get_payment = get_payment

        def receive_order_payment(event):
            payment = event.payment
            order = payment.order
            set_language(order.language)
            order.status = payment.status
            order.gateway_parameters = payment.gateway_parameters

        def commit_order_payment(event):
            datastore.commit()

        events = PaymentGateway.transaction_notified
        pos = events.index(launch_transaction_notification_triggers)
        events.insert(pos, receive_order_payment)
        events.insert(pos + 2, commit_order_payment)

    def _install(self):
        
        catalog = self._create_document("catalog")
        catalog.controller = self._create_controller("catalog")
        catalog.template = self._create_template("catalog")
        catalog.parent = Site.main.home
        catalog.insert()

        for child_name in (
            "basket",
            "checkout",
            "summary"
        ):
            child = self._create_document(child_name)
            child.hidden = True
            child.template = self._create_template(child_name)
            child.controller = self._create_controller(child_name)
            child.parent = catalog
            child.insert()
            self.order_steps.append(child)

        for child_name in (
            "success",
            "failure"
        ):
            child = self._create_document(child_name, StandardPage)
            child.hidden = True
            child.parent = catalog
            child.insert()

        self._create_controller("product").insert()
        self._create_template("product").insert()
        self._create_ecommerceorder_completed_trigger().insert()
        self._create_incoming_order_trigger().insert()

    def _create_document(self, name, 
        cls = Document, 
        template = None,
        controller = None):

        document = cls()
        document.qname = "woost.extensions.ecommerce.%s_page" % name

        self.__translate_field(document, "title")

        if isinstance(document, StandardPage):
            self.__translate_field(document, "body")

        return document

    def _create_template(self, name):
        template = Template()
        template.qname = "woost.extensions.ecommerce.%s_template" % name
        self.__translate_field(template, "title")
        template.engine = "cocktail"
        template.identifier = \
            "woost.extensions.ecommerce.%sPage" % underscore_to_capital(name)
        return template

    def _create_controller(self, name):
        controller = Controller( )
        controller.qname = "woost.extensions.ecommerce.%s_controller" % name
        self.__translate_field(controller, "title")
        controller.python_name = \
            "woost.extensions.ecommerce.%scontroller.%sController" % (
                name,
                underscore_to_capital(name)
            )
        return controller

    def _create_ecommerceorder_completed_trigger(self):
        from woost.extensions.ecommerce.ecommerceordercompletedtrigger import \
            ECommerceOrderCompletedTrigger
        trigger = ECommerceOrderCompletedTrigger( )
        trigger.qname = \
            "woost.extensions.ecommerce.ecommerceorder_completed_trigger"
        self.__translate_field(trigger, "title")
        trigger.site = Site.main
        trigger.condition = "target.customer and not target.customer.anonymous and target.customer.email"
        trigger.matching_items = {'type': u'woost.extensions.ecommerce.ecommerceorder.ECommerceOrder'}

        # EmailTemplate
        template = EmailTemplate()
        template.qname = \
            "woost.extensions.ecommerce.ecommerceorder_completed_emailtemplate"
        self.__translate_field(template, "title")
        template.sender = '"%s"' % User.require_instance(
            qname = "woost.administrator"
        ).email
        template.receivers = '[items[0].customer.email]'
        template.embeded_images = """
from woost.models import Site
images["logo"] = Site.main.logo
"""
        template.template_engine = "cocktail"

        for language in translations:
            with language_context(language):
                template.subject = template.title
                template.body = """
<%
from cocktail.controllers import Location
from cocktail.html import templates

order = items[0]
order_summary = templates.new("woost.extensions.ecommerce.OrderConfirmationMessage")
order_summary.order = order
%>

<html>
    <head>
        <base href="@{unicode(Location.get_current_host())}"/>
    </head>
    <body>
        ${order_summary.render()}
    </body>
</html>
"""

        # Response
        response = SendEmailTriggerResponse()
        response.qname = \
            "woost.extensions.ecommerce.ecommerceorder_completed_response"
        response.email_template = template

        trigger.responses = [response]
        return trigger

    def _create_incoming_order_trigger(self):
        from woost.extensions.ecommerce.incomingordertrigger import \
            IncomingOrderTrigger
        trigger = IncomingOrderTrigger( )
        trigger.qname = "woost.extensions.ecommerce.incoming_order.trigger"
        self.__translate_field(trigger, "title")
        trigger.site = Site.main
        trigger.matching_items = {'type': u'woost.extensions.ecommerce.ecommerceorder.ECommerceOrder'}

        # EmailTemplate
        template = EmailTemplate()
        template.qname = \
            "woost.extensions.ecommerce.incoming_order.email_template"
        self.__translate_field(template, "title")
        admin = User.require_instance(qname = "woost.administrator")
        template.sender = repr(admin.email)
        template.receivers = repr([admin.email])
        template.template_engine = "cocktail"

        for language in translations:
            with language_context(language):
                template.subject = template.title
                template.body = """
<%
from cocktail.translations import translations
from woost.models import Publishable

order = items[0]
bo = Publishable.require_instance(qname = "woost.backoffice")
edit_url = bo.get_uri(host = ".", path = ["content", str(order.id)])
%>

<html>
    <body>
        <a href="${edit_url}">${translations('woost.extensions.ecommerce.incoming_order.edit_link')}
        </a>
    </body>
</html>
"""

        # Response
        response = SendEmailTriggerResponse()
        response.email_template = template
        trigger.responses = [response]

        return trigger

    def __translate_field(self, obj, key):
        for language in translations:
            with language_context(language):
                value = translations("%s.%s" % (obj.qname, key))
                if value:
                    obj.set(key, value)

