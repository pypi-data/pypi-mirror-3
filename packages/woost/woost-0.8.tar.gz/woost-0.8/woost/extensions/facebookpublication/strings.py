#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.translations import translations
from cocktail.translations.helpers import (
    plural2,
    ca_join,
    es_join,
    en_join
)

# FacebookPublicationExtension
#------------------------------------------------------------------------------
translations.define("FacebookPublicationExtension.targets",
    ca = u"Destins",
    es = u"Destinos",
    en = u"Destinations"
)

# FacebookPublicationTarget
#------------------------------------------------------------------------------
translations.define("FacebookPublicationTarget",
    ca = u"Destí de publicació Facebook",
    es = u"Destino de publicación Facebook",
    en = u"Facebook publication target"
)

translations.define("FacebookPublicationTarget-plural",
    ca = u"Destins de publicació Facebook",
    es = u"Destinos de publicación Facebook",
    en = u"Facebook publication targets"
)

translations.define("FacebookPublicationTarget.title",
    ca = u"Nom",
    es = u"Nombre",
    en = u"Name"
)

translations.define("FacebookPublicationTarget.graph_object_id",
    ca = u"Objecte destí",
    es = u"Objeto destino",
    en = u"Target object"
)

translations.define("FacebookPublicationTarget.graph_object_id-explanation",
    ca = u"Identificador de l'objecte de Facebook (usuari, pàgina, etc.) on "
         u"es volen publicar els continguts",
    es = u"Identificador del objeto de Facebook (usuario, página, etc.) "
         u"donde se quieren publicar los contenidos",
    en = u"Identifier for the Facebook object (user, page, etc) where the "
         u"content is to be published"
)

translations.define("FacebookPublicationTarget.administrator_id",
    ca = u"Administrador de la pàgina",
    es = u"Administrador de la página",
    en = u"Page administrator"
)

translations.define("FacebookPublicationTarget.administrator_id-explanation",
    ca = u"Si l'objecte destí és una pàgina de Facebook, cal introduir "
         u"l'identificador de l'usuari de Facebook que la gestiona. En cas "
         u"contrari, deixar en blanc.",
    es = u"Si el objeto destino es una página de Facebook, es necesario "
         u"introducir el identificador del usuario de Facebook que la "
         u"gestiona. En caso contrario, dejar en blanco.",
    en = u"If the target object is a Facebook page, introduce the identifier "
         u"of its appointed administrator. Otherwise, leave blank."
)

translations.define("FacebookPublicationTarget.app_id",
    ca = u"Id d'aplicació Facebook",
    es = u"Id de aplicación Facebook",
    en = u"Facebook application ID"
)

translations.define("FacebookPublicationTarget.app_secret",
    ca = u"Codi secret d'aplicació Facebook",
    es = u"Código secreto de aplicación Facebook",
    en = u"Facebook application secret"
)

translations.define("FacebookPublicationTarget.auth_token",
    ca = u"Autorització",
    es = u"Autorización",
    en = u"Authorization"
)

translations.define("FacebookPublicationTarget.auth_token-conceded",
    ca = u"Concedida",
    es = u"Concedida",
    en = u"Granted"
)

translations.define("FacebookPublicationTarget.auth_token-pending",
    ca = u"Pendent",
    es = u"Pendiente",
    en = u"Pending"
)

translations.define("FacebookPublicationTarget.languages",
    ca = u"Idiomes en que es publica",
    es = u"Idiomas en los que se publica",
    en = u"Published languages"
)

translations.define("FacebookPublicationTarget.targeting",
    ca = u"Segmentació per regió/idioma",
    es = u"Segmentación por región/idioma",
    en = u"Regional/language targeting"
)

# User actions
#------------------------------------------------------------------------------
translations.define("Action fbpublish",
    ca = u"Publicar a Facebook",
    es = u"Publicar en Facebook",
    en = u"Publish to Facebook"
)

translations.define("Action fbpublish_albums",
    ca = u"Publicar imatges a Facebook",
    es = u"Publicar imágenes en Facebook",
    en = u"Publish pictures to Facebook"
)

translations.define("Action fbpublish_auth",
    ca = u"Autoritzar",
    es = u"Autorizar",
    en = u"Authorize"
)

translations.define(
    "woost.extensions.facebookauthentication.fbpublish_auth.success",
    ca = u"S'ha completat l'autorització amb Facebook de forma "
         u"satisfactòria.",
    es = u"Se ha completado la autorización con Facebook de forma "
         u"satisfactoria.",
    en = u"Facebook authorization successful."
)

translations.define(
    "woost.extensions.facebookauthentication.fbpublish_auth.error",
    ca = u"L'autorització amb Facebook ha fallat."
         u"<p><em>Error:</em> %(error)s</p>"
         u"<p><em>Raó:</em> %(error_reason)s</p>"
         u"<p><em>Descripció:</em> %(error_description)s</p>",
    es = u"La autorización con Facebook ha fallado."
         u"<p><em>Error:</em> %(error)s</p>"
         u"<p><em>Razón:</em> %(error_reason)s</p>"
         u"<p><em>Descripción:</em> %(error_description)s</p>",
    en = u"Facebook authorization failed."
         u"<p><em>Error:</em> %(error)s</p>"
         u"<p><em>Reason:</em> %(error_reason)s</p>"
         u"<p><em>Description:</em> %(error_description)s</p>"
)

translations.define(
    "woost.extensions.facebookauthentication.fbpublish_auth.oauth_error",
    ca = u"L'autorització ha fallat: revisa l'id i el codi secret de "
        u"l'aplicació. Resposta: %(response)s",
    es = u"La autorización ha fallado: revisa el id y código secreto de tu "
         u"aplicación. Respuesta: %(response)s",
    en = u"Authorization failed: check your application id and secret code. "
         u"Response: %(response)s"
)

# FacebookPublicationPermission
#------------------------------------------------------------------------------
translations.define("FacebookPublicationPermission",
    ca = u"Permís de publicació a Facebook",
    es = u"Permiso de publicación en Facebook",
    en = u"Facebook publication permission"
)

translations.define("FacebookPublicationPermission-plural",
    ca = u"Permisos de publicació a Facebook",
    es = u"Permisos de publicación en Facebook",
    en = u"Facebook publication permissions"
)

translations.define("FacebookPublicationPermission.publication_targets",
    ca = u"Destins de publicació",
    es = u"Destinos de publicación",
    en = u"Publication targets"
)

# FacebookPublicationController
#------------------------------------------------------------------------------

translations.define("FacebookPublicationForm.subset",
    ca = u"Contingut a publicar",
    es = u"Contenido a publicar",
    en = u"Published content"
)

translations.define("FacebookPublicationForm.published_languages",
    ca = u"Idiomes en que es publicarà el contingut",
    es = u"Idiomas en los que se publicará el contenido",
    en = u"Languages to publish the content in"
)

translations.define("FacebookPublicationForm.publication_targets",
    ca = u"Canals on es publicarà el contingut",
    es = u"Canales donde se publicará el contenido",
    en = u"Channels where the content will be published"
)

translations.define("FacebookPublicationForm.languages",
    ca = u"Idiomes",
    es = u"Idiomas",
    en = u"Languages"
)

translations.define(
    "woost.extensions.facebookpublication.FacebookPublicationView."
    "section_title",
    ca = u"Publicar a Facebook",
    es = u"Publicar en Facebook",
    en = u"Publish with Facebook"
)

translations.define(
    "woost.extensions.facebookpublication.FacebookPublicationView."
    "publication_form.submit_button",
    ca = u"Publicar",
    es = u"Publicar",
    en = u"Publish"
)

translations.define(
    "woost.extensions.facebookpublication.FacebookPublicationView."
    "publication_form.check_button",
    ca = u"Comprovar",
    es = u"Comprobar",
    en = u"Check"
)

translations.define(
    "woost.extensions.facebookpublication.FacebookPublicationView."
    "selection_block",
    ca = u"Contingut a publicar:",
    es = u"Contenido a publicar:",
    en = u"Content to publish:"
)

translations.define(
    "woost.extensions.facebookpublication.FacebookPublicationView."
    "success",
    ca = u"Publicat amb èxit",
    es = u"Publicado con éxito",
    en = u"Published successfully"
)

translations.define(
    "woost.extensions.facebookpublication.FacebookPublicationView."
    "already_published",
    ca = u"Ja publicat",
    es = u"Ya publicado",
    en = u"Already published"
)

translations.define(
    "woost.extensions.facebookpublication.FacebookPublicationView."
    "not_yet_published",
    ca = u"Encara no s'ha publicat",
    es = u"Todavía no se ha publicado",
    en = u"Not published yet"
)

translations.define(
    "woost.extensions.facebookpublication.FacebookPublicationView."
    "publishable_header",
    ca = u"Element",
    es = u"Elemento",
    en = u"Item"
)

translations.define(
    "woost.extensions.facebookpublication.FacebookPublicationView."
    "target_header",
    ca = u"Destí",
    es = u"Destino",
    en = u"Destination"
)

translations.define(
    "woost.extensions.facebookpublication.FacebookPublicationView."
    "language_header",
    ca = u"Idioma",
    es = u"Idioma",
    en = u"Language"
)

translations.define(
    "woost.extensions.facebookpublication.FacebookPublicationView."
    "outcome_header",
    ca = u"Resultat",
    es = u"Resultado",
    en = u"Result"
)

translations.define(
    "woost.extensions.facebookpublication.FacebookAlbumsView."
    "section_title",
    ca = u"Publicar fotos a Facebook",
    es = u"Publicar fotos en Facebook",
    en = u"Publish photos in Facebook"
)

translations.define("FacebookAlbumsForm.album_title",
    ca = u"Títol de l'àlbum",
    es = u"Título del álbum",
    en = u"Album title"
)

translations.define("FacebookAlbumsForm.album_description",
    ca = u"Descripció de l'àlbum",
    es = u"Descripción del álbum",
    en = u"Album description"
)

translations.define("FacebookAlbumsForm.subset",
    ca = u"Imatges incloses a l'àlbum",
    es = u"Imágenes incluídas en el álbum",
    en = u"Album photos"
)

translations.define("FacebookAlbumsForm.photo_languages",
    ca = u"Idiomes per les descripcions de les fotos",
    es = u"Idiomas para las descripciones de las fotos",
    en = u"Languages that photo captions are translated into"
)

translations.define("FacebookAlbumsForm.generate_story",
    ca = u"Anunciar l'àlbum al mur",
    es = u"Anunciar el álbum en el muro",
    en = u"Post a link to the new album in the wall"
)

translations.define("FacebookAlbumsForm.publication_targets",
    ca = u"Canals on es publicaran els àlbums",
    es = u"Canales donde se publicarán los álbumes",
    en = u"Channels where the albums will be published"
)

translations.define(
    "woost.extensions.facebookpublication.FacebookAlbumsView."
    "publication_form.submit_button",
    ca = u"Publicar",
    es = u"Publicar",
    en = u"Publish"
)

translations.define(
    "woost.extensions.facebookpublication.FacebookAlbumsView."
    "selection_block",
    ca = u"Àlbums a publicar:",
    es = u"Álbumes a publicar:",
    en = u"Albums to publish:"
)

translations.define(
    "woost.extensions.facebookpublication.FacebookAlbumsView."
    "success",
    ca = u"Publicat amb èxit",
    es = u"Publicado con éxito",
    en = u"Published successfully"
)

translations.define(
    "woost.extensions.facebookpublication.FacebookAlbumsView."
    "target_header",
    ca = u"Destí",
    es = u"Destino",
    en = u"Destination"
)

translations.define(
    "woost.extensions.facebookpublication.FacebookAlbumsView."
    "outcome_header",
    ca = u"Resultat",
    es = u"Resultado",
    en = u"Result"
)

translations.define(
    "woost.extensions.facebookpublication.facebookpublicationtarget."
    "FacebookPublicationError-instance",
    ca = lambda instance: u"Error de publicació: <pre>%s</pre>" 
                          % instance.response,
    es = lambda instance: u"Error de publicación: <pre>%s</pre>"
                          % instance.response,
    en = lambda instance: u"Publication error: <pre>%s</pre>"
                          % instance.response
)

translations.define(
    "woost.extensions.facebookpublication.FacebookPublicationView."
    "publish_again_link",
    ca = u"Tornar a publicar",
    es = u"Volver a publicar",
    en = u"Publish again"
)

translations.define(
    "woost.extensions.facebookpublication.FacebookPublicationView."
    "loading_sign",
    ca = u"Enviant la petició a Facebook...",
    es = u"Enviando la petición a Facebook...",
    en = u"Sending the request to Facebook..."
)

