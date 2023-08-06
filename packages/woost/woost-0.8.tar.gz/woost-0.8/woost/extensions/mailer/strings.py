#-*- coding: utf-8 -*-
"""

@author:		Jordi Fernández
@contact:		jordi.fernandez@whads.com
@organization:	Whads/Accent SL
@since:			September 2010
"""
from cocktail.translations import translations
from cocktail.translations.strings import member_identifier

# UI
#------------------------------------------------------------------------------
translations.define("Action send_email",
    ca = u"Enviar",
    es = u"Enviar",
    en = u"Send"
)

translations.define("Action create_mailing",
    ca = u"Enviar per correu",
    es = u"Enviar por correo",
    en = u"Send by e-mail"
)

translations.define("woost.extensions.mailer users",
    ca = u"usuaris",
    es = u"usuarios",
    en = u"usuarios"
)

# Mailing
#------------------------------------------------------------------------------
translations.define("Mailing",
    ca = u"Enviament",
    es = u"Envio",
    en = u"Mailing"
)

translations.define("Mailing-plural",
    ca = u"Enviaments",
    es = u"Envios",
    en = u"Mailings"
)

translations.define("Mailing.content",
    ca = u"Contingut",
    es = u"Contenido",
    en = u"Content"
)

translations.define("Mailing.document",
    ca = u"Document",
    es = u"Documento",
    en = u"Document"
)

translations.define("Mailing.sender",
    ca = u"Remitent",
    es = u"Remitente",
    en = u"Sender"
)

translations.define("Mailing.subject",
    ca = u"Assumpte",
    es = u"Asunto",
    en = u"Subject"
)

translations.define("Mailing.roles",
    ca = u"Rols",
    es = u"Roles",
    en = u"Roles"
)

translations.define("Mailing.language",
    ca = u"Idioma",
    es = u"Idioma",
    en = u"Language"
)

translations.define("Mailing.per_user_customizable",
    ca = u"Personalitzable per usuari",
    es = u"Personalizable por usuario",
    en = u"Per user customizable"
)

translations.define("Mailing.status",
    ca = u"Estat",
    es = u"Estado",
    en = u"Status"
)

translations.define("woost.extensions.mailer.mailing.Mailing.status 1",
    ca = u"Iniciat",
    es = u"Iniciado",
    en = u"Started"
)

translations.define("woost.extensions.mailer.mailing.Mailing.status 2",
    ca = u"Finalitzat",
    es = u"Finalizado",
    en = u"Finished"
)

# SendEmailView
#------------------------------------------------------------------------------
translations.define("woost.extensions.mailer.SendEmailView continue",
    ca = u"Continuar",
    es = u"Continuar",
    en = u"Continue"
)

translations.define("woost.extensions.mailer.SendEmailView send",
    ca = u"Enviar",
    es = u"Enviar",
    en = u"Send"
)

translations.define("woost.extensions.mailer.SendEmailView confirmation text",
    ca = lambda mailing:
        u"S'enviarà el document <strong>%s</strong> en <strong>%s</strong> "
        u"als següents usuaris:"
        % (translations(mailing.document), translations(mailing.language)),
    es = lambda mailing:
        u"Se enviará el documento <strong>%s</strong> en "
        u"</strong>%s</strong> a los siguientes usuarios:"
        % (translations(mailing.document), translations(mailing.language)),
    en = lambda mailing:
        u"You are about to send the document <strong>%s</strong> "
        u"in <strong>%s</strong> to the following users:"
        % (translations(mailing.document), translations(mailing.language))
)

translations.define("woost.extensions.mailer.SendEmailView total",
    ca = u"Total:",
    es = u"Total:",
    en = u"Total:"
)

translations.define("woost.extensions.mailer.SendEmailView accessibility warning",
    ca = u"""Tingues en compte que en aquests moments el document que
estàs enviant no és accessible pels usuaris anònims.""",
    es = u"""Ten en cuenta que en estos momentos el documento que
estás enviando no és accesible para los usuarios anónimos.""",
    en = u"""Note that at this moment the document you are sending
is not accessible for anonymous users."""
)

translations.define("woost.extensions.mailer.SendEmailView doing email delivery",
    ca = u"Realitzant enviament",
    es = u"Realizando envio",
    en = u"Doing email delivery"
)

translations.define("woost.extensions.mailer.SendEmailView zero per cent",
    ca = u"0%",
    es = u"0%",
    en = u"0%"
)

translations.define("woost.extensions.mailer.SendEmailView email delivery finished",
    ca = u"Enviament finalitzat",
    es = u"Envio finalizado",
    en = u"Mail delivery finished"
)

translations.define("woost.extensions.mailer.SendEmailView error email delivery",
    ca = u"No s'ha pogut enviar alguns correus. Posa't en contacte amb l'administrador.",
    es = u"No se ha podido enviar algunos correos. Ponte en contacto con el administrador.",
    en = u"Unable to send some emails. Please, contact your administrator."
)

translations.define("woost.extensions.mailer.SendEmailView mailer summary",
    ca = u"S'ha enviat <strong>{0}</strong> correus de <strong>{1}</strong>.",
    es = u"Se han enviado <strong>{0}</strong> correos de <strong>{1}</strong>.",
    en = u"<strong>{0}</strong> of <strong>{1}</strong> emails have been sent."
)

translations.define("woost.extensions.mailer.SendEmailView test explanation",
    ca = u"""Degut a que molts clients de correu electrònic mostren el disseny
del correu de forma diferent, recomanem enviar alguna prova abans de realitzar
l'enviament definitiu.""",
    es = u"""Debido a que muchos clientes de correo electrónico muestran el
diseño del correo de forma diferente, recomendamos enviar alguna prueba antes
de realitzar el envio definitivo.""",
    en = u"""Because most email clients will display your email design
differently, we recommend sending yourself a few tests before scheduling the
final campaign."""
)

translations.define("woost.extensions.mailer.SendEmailView test email",
    ca = u"Correu electrònic",
    es = u"Correo electrónico",
    en = u"E-mail address"
)

translations.define("woost.extensions.mailer.SendEmailView test",
    ca = u"Enviar el correu de prova",
    es = u"Enviar el correo de prueba",
    en = u"Send the test email"
)

# Template
#------------------------------------------------------------------------------
translations.define("Template.per_user_customizable",
    ca = u"Personalitzable per usuari",
    es = u"Personalizable por usuario",
    en = u"Per user customizable"
)

# SendEmailPermission
#------------------------------------------------------------------------------
translations.define("SendEmailPermission",
    ca = u"Permís d'enviament de correu electrònic",
    es = u"Permiso de envio de correo electrónico",
    en = u"Permission to send email"
)

translations.define("SendEmailPermission-plural",
    ca = u"Permisos d'enviament de correu electrònic",
    es = u"Permisos de envio de correo electrónico",
    en = u"Permissions to send email"
)

translations.define("SendEmailPermission.roles",
    ca = u"Rols",
    es = u"Roles",
    en = u"Roles"
)

translations.define("SendEmailPermission.roles-explanation",
    ca = u"Limita el permís en funció dels destinataris de l'enviament. "
         u"Deixar en blanc per permetre o prohibir l'enviament a tothom.",
    es = u"Limita el permiso en función de los destinatarios del envío. "
         u"Dejar en blanco para permitir o prohibir el envío sin importar "
         u"los destinatarios seleccionados.",
    en = u"Limits the groups of receivers that the user can or can't send "
         u"email to. Leave blank to allow / disallow sending e-mail "
         u"regardless of the selected receivers."
)

# Exceptions
#------------------------------------------------------------------------------
translations.define("woost.extensions.mailer.mailing.DocumentTemplateRequiredError-instance",                                                                                                                             
    ca = lambda instance:
        u"El camp <em>%s</em> ha de tindre plantilla"
        % member_identifier(instance),
    es = lambda instance:
        u"El campo <em>%s</em> debe tener plantilla"
        % member_identifier(instance),
    en = lambda instance:
        u"The <em>%s</em> field must have a template"
        % member_identifier(instance)
)

translations.define("woost.extensions.mailer.mailing.LanguageValueError-instance",                                                                                                                             
    ca = lambda instance:
        u"El camp <em>%s</em> no és un dels idiomes del document"
        % member_identifier(instance),
    es = lambda instance:
        u"El campo <em>%s</em> no es uno de los idiomas del documento"
        % member_identifier(instance),
    en = lambda instance:
        u"The <em>%s</em> field isn't one of the document languages"
        % member_identifier(instance)
)

translations.define("woost.extensions.mailer.mailing.PerUserCustomizableValueError-instance",                                                                                                                             
    ca = lambda instance:
        u"El camp <em>%s</em> no és vàlid pel document seleccionat"
        % member_identifier(instance),
    es = lambda instance:
        u"El campo <em>%s</em> no es válido para el documento seleccionado"
        % member_identifier(instance),
    en = lambda instance:
        u"The <em>%s</em> is not valid for the selected document"
        % member_identifier(instance)
)

translations.define(
    "woost.extensions.mailer.mailing.RunningMailingError-instance",                                                                                                                                     
    ca = u"No es pot eliminar un enviament que està en execució.",
    es = u"No se puede eliminar un envio que está en ejecución.",
    en = u"Can't delete a running mailing."
)

