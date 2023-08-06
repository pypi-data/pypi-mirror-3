#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.translations import translations

# TwitterPublicationExtension
#------------------------------------------------------------------------------
translations.define("TwitterPublicationExtension.targets",
    ca = u"Destins",
    es = u"Destinos",
    en = u"Targets"
)

# TweetPermission
#------------------------------------------------------------------------------
translations.define("TweetPermission",
    ca = u"Permís de publicació a Twitter",
    es = u"Permiso de publicación en Twitter",
    en = u"Permission for publishing to Twitter"
)

translations.define("TweetPermission-plural",
    ca = u"Permisos de publicació a Twitter",
    es = u"Permisos de publicación en Twitter",
    en = u"Permissions for publishing to Twitter"
)

translations.define("TweetPermission.targets",
    ca = u"Destins permesos",
    es = u"Destinos permitidos",
    en = u"Allowed targets"
)

# TwitterPublicationTarget
#------------------------------------------------------------------------------
translations.define("TwitterPublicationTarget",
    ca = u"Destí de publicació a Twitter",
    es = u"Destino de publicación en Twitter",
    en = u"Twitter publication target"
)

translations.define("TwitterPublicationTarget",
    ca = u"Destins de publicació a Twitter",
    es = u"Destinos de publicación en Twitter",
    en = u"Twitter publication targets"
)

translations.define("TwitterPublicationTarget.title",
    ca = u"Nom",
    es = u"Nombre",
    en = u"Name"
)

translations.define("TwitterPublicationTarget.account",
    ca = u"Compte de Twitter",
    es = u"Cuenta de Twitter",
    en = u"Twitter account"
)

translations.define("TwitterPublicationTarget.app_id",
    ca = u"Identificador d'aplicació de Twitter",
    es = u"Identificador de aplicación de Twitter",
    en = u"Twitter application id"
)

translations.define("TwitterPublicationTarget.app_secret",
    ca = u"Secret d'aplicació de Twitter",
    es = u"Secreto de aplicación de Twitter",
    en = u"Twitter application secret"
)

translations.define("TwitterPublicationTarget.auth_token",
    ca = u"Autorització",
    es = u"Autorización",
    en = u"Authorization"
)

translations.define("TwitterPublicationTarget.auth_token-conceded",
    ca = u"Concedida",
    es = u"Concedida",
    en = u"Granted"
)

translations.define("TwitterPublicationTarget.auth_token-pending",
    ca = u"Pendent",
    es = u"Pendiente",
    en = u"Pending"
)

translations.define("TwitterPublicationTarget.auth_secret",
    ca = u"Secret d'autorització de Twitter",
    es = u"Secreto de autorización de Twitter",
    en = u"Twitter authorization secret"
)

translations.define("TwitterPublicationTarget.url_shortener",
    ca = u"Escurçador d'URLs",
    es = u"Compactador de URLs",
    en = u"URL shortener"
)

translations.define("TwitterPublicationTarget.languages",
    ca = u"Idiomes a publicar",
    es = u"Idiomas a publicar",
    en = u"Published languages"
)

# twitter_auth user action
#------------------------------------------------------------------------------
translations.define("Action twitter_auth",
    ca = u"Autoritzar",
    es = u"Autorizar",
    en = u"Authorize"
)

translations.define(
    "woost.extensions.twitterpublication.successful_authorization_notice",
    ca = u"S'ha completat l'autorització de forma satisfactòria",
    es = u"Se ha completado la autorización de forma satisfactoria",
    en = u"Authorization granted"
)

# tweet user action
#------------------------------------------------------------------------------
translations.define("Action tweet",
    ca = u"Publicar a Twitter",
    es = u"Publicar en Twitter",
    en = u"Tweet"
)

# TwitterAPIError
#------------------------------------------------------------------------------
translations.define(
    "woost.extensions.twitterpublication.exceptions.TwitterAPIError-instance",
    ca = lambda instance: u"Error de comunicació amb Twitter: <pre>%s</pre>"
                          % instance.response,
    es = lambda instance: u"Error de comunicación con Twitter: <pre>%s</pre>"
                          % instance.response,
    en = lambda instance: u"Twitter API error: <pre>%s</pre>"
                          % instance.response
)

# TwitterPublicationForm
#------------------------------------------------------------------------------
translations.define(
    "woost.extensions.twitterpublication.TwitterPublicationView.section_title",
    ca = u"Publicar a Twitter",
    es = u"Publicar en Twitter",
    en = u"Publish to Twitter"
)
    
translations.define("TwitterPublicationForm.subset",
    ca = u"Contingut a publicar",
    es = u"Contenido a publicar",
    en = u"Published items"
)

translations.define("TwitterPublicationForm.published_languages",
    ca = u"Idiomes a publicar",
    es = u"Idiomas a publicar",
    en = u"Published languages"
)

translations.define("TwitterPublicationForm.publication_targets",
    ca = u"Destins on es publicarà el contingut",
    es = u"Destinos donde se publicará el contenido",
    en = u"Publication targets"
)

translations.define(
    "woost.extensions.twitterpublication.TwitterPublicationView."
    "publication_form.submit_button",
    ca = u"Publicar",
    es = u"Publicar",
    en = u"Publish"
)

translations.define(
    "woost.extensions.twitterpublication.TwitterPublicationView."
    "publication_form.check_button",
    ca = u"Comprovar",
    es = u"Comprobar",
    en = u"Check"
)

translations.define(
    "woost.extensions.twitterpublication.TwitterPublicationView."
    "already_published",
    ca = u"Ja publicat",
    es = u"Ya publicado",
    en = u"Already published"
)

translations.define(
    "woost.extensions.twitterpublication.TwitterPublicationView."
    "not_yet_published",
    ca = u"Encara no s'ha publicat",
    es = u"Todavía no se ha publicado",
    en = u"Not published yet"
)

translations.define(
    "woost.extensions.twitterpublication.TwitterPublicationView."
    "success",
    ca = u"Publicat amb èxit",
    es = u"Publicado con éxito",
    en = u"Published successfully"
)

translations.define(
    "woost.extensions.twitterpublication.TwitterPublicationView."
    "publishable_header",
    ca = u"Element",
    es = u"Elemento",
    en = u"Item"
)

translations.define(
    "woost.extensions.twitterpublication.TwitterPublicationView."
    "target_header",
    ca = u"Destí",
    es = u"Destino",
    en = u"Destination"
)

translations.define(
    "woost.extensions.twitterpublication.TwitterPublicationView."
    "language_header",
    ca = u"Idioma",
    es = u"Idioma",
    en = u"Language"
)

translations.define(
    "woost.extensions.twitterpublication.TwitterPublicationView."
    "outcome_header",
    ca = u"Resultat",
    es = u"Resultado",
    en = u"Result"
)

translations.define(
    "woost.extensions.twitterpublication.TwitterPublicationView."
    "publish_again_link",
    ca = u"Tornar a publicar",
    es = u"Volver a publicar",
    en = u"Publish again"
)

translations.define(
    "woost.extensions.twitterpublication.TwitterPublicationView."
    "loading_sign",
    ca = u"Enviant la petició a Twitter...",
    es = u"Enviando la petición a Twitter...",
    en = u"Sending the request to Twitter..."
)

