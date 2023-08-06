#-*- coding: utf-8 -*-
u"""

@author:        Jordi Fernández
@contact:       jordi.fernandez@whads.com
@organization:  Whads/Accent SL
@since:         March 2010
"""
from cocktail.translations import translations

translations.define(
    "woost.extensions.campaignmonitor.subscription_controller.title",
    ca = u"Controlador de subscripció a Campaign Monitor",
    es = u"Controlador de suscripicón a Campaign Monitor",
    en = u"Subscription to Campaign Monitor controller"
)

translations.define(
    "woost.extensions.campaignmonitor.unsubscription_controller.title",
    ca = u"Controlador de baixa de Campaign Monitor",
    es = u"Controlador de baja de Campaign Monitor",
    en = u"Unsubscription to Campaign Monitor controller"
)

translations.define(
    "woost.extensions.campaignmonitor.subscription_template.title",
    ca = u"Vista de subscripció a Campaign Monitor",
    en = u"Subscription to Campaign Monitor view",
    es = u"Vista de suscripción a Campaign Monitor"
)

translations.define(
    "woost.extensions.campaignmonitor.unsubscription_template.title",
    ca = u"Plantilla de baixa de Campaign Monitor",
    es = u"Plantilla de baja de Campaign Monitor",
    en = u"Unsubscription from Campaign Monitor template"
)

translations.define(
    "woost.extensions.campaignmonitor.subscription_page.title",
    ca = u"Pàgina de subscripció",
    es = u"Página de suscripción",
    en = u"Subscription page"
)

translations.define(
    "woost.extensions.campaignmonitor.pending_page.title",
    ca = u"Pàgina d'instruccions de subscripció",
    es = u"Página de instrucciones de suscripcion",
    en = u"Page with instructions for subscription"
)

translations.define(
    "woost.extensions.campaignmonitor.pending_page.body",
    ca = u"T'hem enviat un e-mail per confirmar la teva adreça de correu "
         u"electrònic. Si et plau, fes clic a l'enllaç que apareix a "
         u"l'e-mail per confirmar la teva subscripció.",
    es = u"Te hemos enviado un e-mail para confirmar tu dirección de correo "
         u"electrónico. Por favor, haz clic en el enlace que aparece en el "
         u"e-mail para confirmar tu suscripción.""",
    en = u"We've just been sent an email to confirm your email address. "
         u"Please click on the link in this email to confirm your "
         u"subscription."
)

translations.define(
    "woost.extensions.campaignmonitor.confirmation_success_page.title",
    ca = u"Pàgina de confirmació",
    es = u"Página de confirmación",
    en = u"Confirmation page"
)

translations.define(
    "woost.extensions.campaignmonitor.confirmation_success_page.body",
    ca = u"La teva subscripció ha estat confirmada. Hem afegit la teva "
         u"adreça a la nostra llista i en breu rebràs notícies nostres.",
    es = u"Tu suscripción ha sido confirmada. Se ha añadido tu dirección a "
         u"nuestra lista y en breve recibirás noticias nuestras.",
    en = u"Your subscription has been confirmed. You've been added to our "
         u"list and will hear from us soon."
)

translations.define(
    "woost.extensions.campaignmonitor.unsubscribe_page.title",
    ca = u"Pàgina de baixa",
    es = u"Página de baja",
    en = u"Unsubscribe page"
)

translations.define(
    "woost.extensions.campaignmonitor.unsubscribe_page.body",
    ca = u"La teva adreça s'ha retirat amb èxit d'aquesta llista de "
         u"subscripció. No tornaràs a rebre'n missatges.",
    es = u"Tu dirección ha sido eliminada con éxito de esta lista de "
         u"suscripción. No volverás a recibir mensajes de esta lista.",
    en = u"You have been successfully removed from this subscriber list. You "
         u"will no longer receive messages from this list."         
)

# UI
#------------------------------------------------------------------------------
translations.define("Action sync_campaign_monitor_lists",                                                                                                                                                                       
    ca = u"Sincronitzar amb Campaign Monitor",
    es = u"Sincronizar con Campaign Monitor",
    en = u"Synchronize with Campaign Monitor"
)

# CampaignMonitorExtension
#------------------------------------------------------------------------------
translations.define("CampaignMonitorExtension.api_key",
    ca = u"Clau d'API",
    es = u"Clave de API",
    en = u"API key"
)

translations.define("CampaignMonitorExtension.client_id",
    ca = u"Id de client",
    es = u"Id de cliente",
    en = u"Client id"
)

translations.define("CampaignMonitorExtension.lists",
    ca = u"Llistes",
    es = u"Listas",
    en = u"Lists"
)

# CampaignMonitorList
#------------------------------------------------------------------------------
translations.define("CampaignMonitorList",
    ca = u"Llista de subscripció",
    es = u"Lista de suscripción",
    en = u"Subscription list"
)

translations.define("CampaignMonitorList-plural",
    ca = u"Llistes de subscripció",
    es = u"Listas de suscripción",
    en = u"Subscription lists"
)

translations.define("CampaignMonitorList.list_id",
    ca = u"Id de llista",
    es = u"Id de lista",
    en = u"List id"
)

translations.define("CampaignMonitorList.title",
    ca = u"Nom",
    es = u"Nombre",
    en = u"Name"
)

translations.define("CampaignMonitorList.pending_page",
    ca = u"Pàgina d'instruccions",
    es = u"Página de instrucciones",
    en = u"Instructions page"
)

translations.define("CampaignMonitorList.unsubscribe_page",
    ca = u"Pàgina de baixa",
    es = u"Página de baja",
    en = u"Unsubscribe page"
)

translations.define("CampaignMonitorList.confirmation_success_page",
    ca = u"Pàgina de confirmació d'alta",
    es = u"Página de confirmación de alta",
    en = u"Confirmation success page"
)

# CampaignMonitorSubscriptionPage
#------------------------------------------------------------------------------
translations.define("CampaignMonitorSubscriptionPage",
    ca = u"Pàgina de subscripció a mailing",
    es = u"Página de suscripción a mailing",
    en = u"Mailing subscription page"
)

translations.define("CampaignMonitorSubscriptionPage-plural",
    ca = u"Pàgines de subscripció a mailing",
    es = u"Páginas de suscripción a mailing",
    en = u"Mailing subscription pages"
)

translations.define("CampaignMonitorSubscriptionPage.body",
    ca = u"Cos",
    es = u"Cuerpo",
    en = u"Body"
)

translations.define("CampaignMonitorSubscriptionPage.lists",
    ca = u"Llistes",
    es = u"Listas",
    en = u"Lists"
)

translations.define("CampaignMonitorSubscriptionPage.subscription_form",
    ca = u"Formulari de subscripció",
    es = u"Formulario de suscripción",
    en = u"Subscription form"
)

# CampaignMonitorListsSynchronizationView
#------------------------------------------------------------------------------
translations.define(
    "woost.extensions.campaignmonitor.CampaignMonitorListsSynchronizationView outcome",
    ca = u"S'ha completat la sincronització.",
    es = u"Se ha completado la sincronización.",
    en = u"Synchronization complete."
)

translations.define(
    "woost.extensions.campaignmonitor.CampaignMonitorListsSynchronizationView no changes",
    ca = u"No ha estat necessari realitzar cap actualització.",
    es = u"No ha sido necesario realizar ninguna actualización.",
    en = u"No update was needed."
)

translations.define(
    "woost.extensions.campaignmonitor.CampaignMonitorListsSynchronizationView cancel button",                                                                                                                                
    ca = u"Tancar",
    es = u"Cerrar",
    en = u"Close"
)

translations.define(
    "woost.extensions.campaignmonitor.CampaignMonitorListsSynchronizationView created lists title",
    ca = u"Llistes afegides",
    es = u"Listas añadidas",
    en = u"Added lists"
)

translations.define(
    "woost.extensions.campaignmonitor.CampaignMonitorListsSynchronizationView created lists explanation",
    ca = u"Les següents llistes s'han incorporat al lloc web:",
    es = u"Las listas siguientes se han incorporado al sitio web:",
    en = u"The following lists were added to the web site:"
)

translations.define(
    "woost.extensions.campaignmonitor.CampaignMonitorListsSynchronizationView modified lists title",
    ca = u"Llistes modificades",
    es = u"Listas modificadas",
    en = u"Modified lists"
)

translations.define(
    "woost.extensions.campaignmonitor.CampaignMonitorListsSynchronizationView modified lists explanation",
    ca = u"S'ha actualitzat la informació de les llistes següents:",
    es = u"Se ha actualizado la información de las listas siguientes:",
    en = u"The following lists had changes that have been reflected on the "
         u"web site:"
)

translations.define(
    "woost.extensions.campaignmonitor.CampaignMonitorListsSynchronizationView deleted lists title",
    ca = u"Llistes eliminades",
    es = u"Listas eliminadas",
    en = u"Deleted lists"
)

translations.define(
    "woost.extensions.campaignmonitor.CampaignMonitorListsSynchronizationView deleted lists explanation",
    ca = u"Les següents llistes ja no són presents a Campaign Monitor i s'han "
         u"eliminat del lloc web:",
    es = u"Las listas siguientes ya no están disponibles en Campaign Monitor y se "
         u"han eliminado del sitio web:",
    en = u"The following lists are no longer available at Campaign Monitor and "
         u"have been deleted from the web site:"
)

# CampaignMonitorSubscriptionView
#------------------------------------------------------------------------------
translations.define(
    "woost.extensions.campaignmonitor.CampaignMonitorSubscriptionView api error",
    ca = u"Hi ha hagut algun problema. Siusplau, provi-ho de nou més tard.",
    es = u"Ha habido algun problema, por favor pruebelo más tarde.",
    en = u"An error occurred, please try again later."
)

# CampaignMonitorUnsubscriptionView
#------------------------------------------------------------------------------
translations.define(
    "woost.extensions.campaignmonitor.CampaignMonitorUnsubscriptionView resubscribe",
    ca = u"""No volies donar-te de baixa? <a href="%s">Clica aquí</a> per 
resubscriure't i continuar rebent comunicacions nostres.""",
    es = u"""No querías darte de baja? <a href="%s">Clica aquí</a> para 
resuscribirte y continuar recibiendo comunicaciones nuestras.""",
    en = u"""Didn't mean to unsubscribe? <a href="%s">Click here</a> to 
re-subscribe and continue receiving emails from us."""
)

# SubscriptionForm
#------------------------------------------------------------------------------
translations.define("SubscriptionForm.name",
    ca = u"Nom",
    es = u"Nombre",
    en = u"Name"
)

translations.define("SubscriptionForm.email",
    ca = u"Correu electrònic",
    es = u"Correo electrónico",
    en = u"E-mail address"
)

translations.define("SubscriptionForm.list",
    ca = u"Llista",
    es = u"Lista",
    en = u"List"
)

