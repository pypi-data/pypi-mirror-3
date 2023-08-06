#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Jordi Fernández <jordi.fernandez@whads.com>
"""
from cocktail.translations import translations

translations.define("woost.extensions.blocks.slots.blocks",
    ca = u"Blocs",
    es = u"Bloques",
    en = u"Blocks"
)

# BlocksPage
#------------------------------------------------------------------------------
translations.define("BlocksPage",
    ca = u"Pàgina de blocs",
    es = u"Página de bloques",
    en = u"Blocks page"
)

translations.define("BlocksPage-plural",
    ca = u"Pàgines de blocs",
    es = u"Páginas de bloques",
    en = u"Blocks pages"
)

translations.define("BlocksPage.blocks",
    ca = u"Blocs",
    es = u"Bloques",
    en = u"Blocks"
)

# Blocks page template
#------------------------------------------------------------------------------
translations.define("woost.extensions.blocks.blocks_page_template.title",
    ca = u"Plantilla pàgina de blocs",
    es = u"Plantilla página de bloques",
    en = u"Blocks page template"
)

# Block
#------------------------------------------------------------------------------
translations.define("Block",
    ca = u"Bloc",
    es = u"Bloque",
    en = u"Block"
)

translations.define("Block-plural",
    ca = u"Blocs",
    es = u"Bloques",
    en = u"Blocks"
)

translations.define("Block.content",
    ca = u"Contingut",
    es = u"Contenido",
    en = u"Content"
)

translations.define("Block.title",
    ca = u"Títol",
    es = u"Título",
    en = u"Title"
)

translations.define("Block.title-explanation",
    ca = u"Descripció del bloc, d'ús intern pels editors",
    es = u"Descripción del bloque, de uso interno para los editores",
    en = u"Description for this block, used internally by editors"
)

translations.define("Block.heading",
    ca = u"Títol de capçalera",
    es = u"Título de cabecera",
    en = u"Heading"
)

translations.define("Block.heading-explanation",
    ca = u"Títol del bloc, tal com es mostrarà al web",
    es = u"Título del bloque, tal como se mostraré en la web",
    en = u"Block title, as shown on the website"
)

translations.define("Block.html_id",
    ca = u"ID de l'element HTML",
    es = u"ID del elemento HTML",
    en = u"HTML element ID"
)

translations.define("Block.css_class",
    ca = u"Classes CSS",
    es = u"Clases CSS",
    en = u"CSS classes"
)

translations.define("Block.enabled",
    ca = u"Actiu",
    es = u"Activo",
    en = u"Active"
)

translations.define("Block.containers",
    ca = u"Contenidors",
    es = u"Contenedores",
    en = u"Containers"
)

# ImageGalleryBlock
#------------------------------------------------------------------------------
translations.define("ImageGalleryBlock",
    ca = u"Galeria d'imatges",
    es = u"Galería de imágenes",
    en = u"Image gallery"
)

translations.define("ImageGalleryBlock.gallery_type",
    ca = u"Tipus de galeria",
    es = u"Tipo de galería",
    en = u"Gallery type"
)

translations.define("ImageGalleryBlock.gallery_type-thumbnails",
    ca = u"Miniatures",
    es = u"Miniaturas",
    en = u"Thumbnails"
)

translations.define("ImageGalleryBlock.gallery_type-slideshow",
    ca = u"Passador",
    es = u"Pasador",
    en = u"Slideshow"
)

translations.define("ImageGalleryBlock.images",
    ca = u"Imatges",
    es = u"Imágenes",
    en = u"Images"
)

translations.define("ImageGalleryBlock-plural",
    ca = u"Galeries",
    es = u"Galerías",
    en = u"Image galleries"
)

translations.define("ImageGalleryBlock.thumbnail_factory",
    ca = u"Processat per les miniatures",
    es = u"Procesado para las miniaturas",
    en = u"Thumbnail factory"
)

translations.define("ImageGalleryBlock.close_up_factory",
    ca = u"Processat per les imatges ampliades",
    es = u"Procesado para la imagen ampliada",
    en = u"Close up factory"
)

translations.define("ImageGalleryBlock.auto_play",
    ca = u"Transicions automàtiques",
    es = u"Transiciones automáticas",
    en = u"Auto play"
)

translations.define("ImageGalleryBlock.labels_visible",
    ca = u"Mostrar els títols de les imatges",
    es = u"Mostrar los títulos de las imágenes",
    en = u"Show image titles"
)

translations.define("ImageGalleryBlock.footnotes_visible",
    ca = u"Mostrar els peus de foto",
    es = u"Mostrar los pies de foto",
    en = u"Include footnotes"
)

translations.define("ImageGalleryBlock.original_link_visible",
    ca = u"Mostrar un enllaç a la imatge completa",
    es = u"Mostrar un enlace a la imagen completa",
    en = u"Include a link to the original image"
)

translations.define("ImageGalleryBlock.close_up_enabled",
    ca = u"Habilitar la versió ampliada de les imatges",
    es = u"Habilitar la versión ampliada de las imágenes",
    en = u"Enable image close ups"
)

translations.define("ImageGalleryBlock.close_up_preload",
    ca = u"Precàrrega de la versió ampliada de les imatges",
    es = u"Precarga de la versión ampliada de las imágenes",
    en = u"Preload image close ups"
)

translations.define("ImageGalleryBlock.close_up_preload-explanation",
    ca = u"Habilitar per tal que el navegador carregui la versió ampliada de "
         u"les imatges tan bon punt es mostri la galeria. Això accelera la "
         u"navegació, però representa un major impacte pel servidor.",
    es = u"Habilitar para que el navegador empiece a cargar la versión "
         u"ampliada de las imágenes desde el primer momento en que se muestre "
         u"la galería. Esto acelera la navegación, pero representa un mayor "
         u"impacto para el servidor.",
    en = u"Enable to instruct the browser to start downloading the image "
         u"close ups as soon as the gallery is displayed. This improves the "
         u"user experience but causes a higher load for the web server."
)

# ContainerBlock
#------------------------------------------------------------------------------
translations.define("ContainerBlock",
    ca = u"Contenidor",
    es = u"Contenedor",
    en = u"Container"
)

translations.define("ContainerBlock-plural",
    ca = u"Contenidors",
    es = u"Contenedores",
    en = u"Containers"
)

translations.define("ContainerBlock.blocks",
    ca = u"Blocs fills",
    es = u"Bloques hijos",
    en = u"Child blocks"
)

# SlideShowBlock
#------------------------------------------------------------------------------
translations.define("SlideShowBlock",
    ca = u"Passador",
    es = u"Pasador",
    en = u"Slide show"
)

translations.define("SlideShowBlock-plural",
    ca = u"Passadors",
    es = u"Pasadores",
    en = u"Slide shows"
)

translations.define("SlideShowBlock.transition_settings",
    ca = u"Transicions",
    es = u"Transiciones",
    en = u"Transitions"
)

translations.define("SlideShowBlock.autoplay",
    ca = u"Transicions automàtiques",
    es = u"Transiciones automáticas",
    en = u"Autoplay"
)

translations.define("SlideShowBlock.navigation_controls",
    ca = u"Mostrar controls de navegació",
    es = u"Mostrar controles de navegación",
    en = u"Show navigation controls"
)

translations.define("SlideShowBlock.interval",
    ca = u"Freqüència de les transicions",
    es = u"Frecuencia de las transiciones",
    en = u"Time between transitions"
)

translations.define("SlideShowBlock.interval-explanation",
    ca = u"Si s'activen les transicions automàtiques, indica el nombre de "
         u"milisegons abans que el bloc passi a la següent diapositiva.",
    es = u"Si se activan las transiciones automáticas, indica el número de "
         u"milisegundos antes que el bloque pase a la diapositiva siguiente.",
    en = u"If autoplay is enabled, indicates the number of milliseconds that "
         u"pass between automatic transitions."
)

translations.define("SlideShowBlock.transition_duration",
    ca = u"Duració de les transicions",
    es = u"Duración de las transiciones",
    en = u"Transition duration"
)

translations.define("SlideShowBlock.interval-explanation",
    ca = u"Especifica la duració de l'efecte de transició, en milisegons",
    es = u"Especifica la duración del efecto de transición, en milisegundos",
    en = u"Sets the duration of the slide transition effect, in milliseconds"
)

# BannerBlock
#------------------------------------------------------------------------------
translations.define("BannerBlock",
    ca = u"Banner",
    es = u"Banner",
    en = u"Banner"
)

translations.define("BannerBlock-plural",
    ca = u"Banners",
    es = u"Banners",
    en = u"Banners"
)

translations.define("BannerBlock.text",
    ca = u"Text",
    es = u"Texto",
    en = u"Text"
)

translations.define("BannerBlock.text-explanation",
    ca = u"En cas de no especificar-se s'utilitzarà el títol de l'element "
         u"destí",
    es = u"En caso de no especificarse se utilitzará el título del "
         u"elemento destino",
    en = u"If no text is provided the title from the target item will be used"
)

translations.define("BannerBlock.target",
    ca = u"Destí",
    es = u"Destino",
    en = u"Target"
)

translations.define("BannerBlock.image",
    ca = u"Imatge",
    es = u"Imagen",
    en = u"Image"
)

translations.define("BannerBlock.image_factory",
    ca = u"Processat d'imatge",
    es = u"Procesado de imagen",
    en = u"Image processing"
)

translations.define("BannerBlock.label_displayed",
    ca = u"Mostrar el text",
    es = u"Mostrar el texto",
    en = u"Label displayed"
)

translations.define("BannerBlock.label_displayed-explanation",
    ca = u"Si es desactiva aquesta opció no es mostra el text del bloc, "
         u"només la seva imatge.",
    es = u"Si se desactiva esta opción no se muestra el texto del bloque, "
         u"solo su imagen.",
    en = u"If this option is disabled, the block's text won't be displayed, "
         u"only its image will be shown."
)

# MenuBlock
#------------------------------------------------------------------------------
translations.define("MenuBlock",
    ca = u"Menú",
    es = u"Menú",
    en = u"Menu"
)

translations.define("MenuBlock-plural",
    ca = u"Menús",
    es = u"Menús",
    en = u"Menus"
)

translations.define("MenuBlock.root",
    ca = u"Arrel",
    es = u"Raiz",
    en = u"Root"
)

translations.define("MenuBlock.root_visible",
    ca = u"Arrel visible",
    es = u"Raiz visible",
    en = u"Root visible"
)

translations.define("MenuBlock.max_depth",
    ca = u"Profunditat màxima",
    es = u"Profundidad máxima",
    en = u"Maximum depth"
)

translations.define("MenuBlock.expanded",
    ca = u"Expandit",
    es = u"Expandido",
    en = u"Expanded"
)

# RichTextBlock
#------------------------------------------------------------------------------
translations.define("RichTextBlock",
    ca = u"Text",
    es = u"Texto",
    en = u"Text"
)

translations.define("RichTextBlock-plural",
    ca = u"Textos",
    es = u"Textos",
    en = u"Texts"
)

translations.define("RichTextBlock.text",
    ca = u"Text",
    es = u"Texto",
    en = u"Text"
)

translations.define("RichTextBlock.attachments",
    ca = u"Adjunts",
    es = u"Adjuntos",
    en = u"Attachments"
)

# TranslatedRichTextBlock
#------------------------------------------------------------------------------
translations.define("TranslatedRichTextBlock",
    ca = u"Text traduïble",
    es = u"Texto traducible",
    en = u"Translated text"
)

translations.define("TranslatedRichTextBlock-plural",
    ca = u"Textos traduïbles",
    es = u"Textos traducibles",
    en = u"Translated texts"
)

translations.define("TranslatedRichTextBlock.text",
    ca = u"Text",
    es = u"Texto",
    en = u"Text"
)

translations.define("TranslatedRichTextBlock.text",
    ca = u"Text",
    es = u"Texto",
    en = u"Text"
)

translations.define("TranslatedRichTextBlock.image",
    ca = u"Imatge",
    es = u"Imagen",
    en = u"Image"
)

translations.define("TranslatedRichTextBlock.image_factory",
    ca = u"Processat de la imatge",
    es = u"Procesado de la imagen",
    en = u"Image processing"
)

translations.define("TranslatedRichTextBlock.attachments",
    ca = u"Adjunts",
    es = u"Adjuntos",
    en = u"Attachments"
)

# VimeoBlock
#------------------------------------------------------------------------------
translations.define("VimeoBlock",
    ca = u"Vídeo de Vimeo",
    es = u"Video de Vimeo",
    en = u"Vimeo video"
)

translations.define("VimeoBlock-plural",
    ca = u"Vídeos de Vimeo",
    es = u"Vídeos de Vimeo",
    en = u"Vimeo videos"
)

translations.define("VimeoBlock.video",
    ca = u"Vídeo",
    es = u"Video",
    en = u"Video"
)

translations.define("VimeoBlock.video_width",
    ca = u"Amplada",
    es = u"Ancho",
    en = u"Width"
)

translations.define("VimeoBlock.video_width-explanation",
    ca = u"en píxels",
    es = u"en píxeles",
    en = u"in pixels"
)

translations.define("VimeoBlock.video_height",
    ca = u"Alçada",
    es = u"Alto",
    en = u"Height"
)

translations.define("VimeoBlock.video_height-explanation",
    ca = u"en píxels",
    es = u"en píxeles",
    en = u"in pixels"
)

# TwitterTimelineBlock
#------------------------------------------------------------------------------
translations.define("TwitterTimelineBlock",
    ca = u"Missatges de Twitter",
    es = u"Mensajes de Twitter",
    en = u"Twitter timeline"
)

translations.define("TwitterTimelineBlock-plural",
    ca = u"Missatges de Twitter",
    es = u"Mensajes de Twitter",
    en = u"Twitter timeline"
)

translations.define("TwitterTimelineBlock.account",
    ca = u"Compte de Twitter",
    es = u"Cuenta de Twitter",
    en = u"Twitter account"
)

translations.define("TwitterTimelineBlock.max_tweets",
    ca = u"Missatges a mostrar",
    es = u"Mensajes a mostrar",
    en = u"Max tweets"
)

# LinksBox
#------------------------------------------------------------------------------
translations.define("LinksBlock",
    ca = u"Llista d'enllaços",
    es = u"Lista de enlaces",
    en = u"Link list"
)

translations.define("LinksBlock-plural",
    ca = u"Llistes d'enllaços",
    es = u"Listas de enlaces",
    en = u"Link lists"
)

translations.define("LinksBlock.links",
    ca = u"Enllaços",
    es = u"Enlaces",
    en = u"Links"
)

# FolderBlock
#------------------------------------------------------------------------------
translations.define("FolderBlock",
    ca = u"Llistat de documents fills",
    es = u"Listado de documentos hijos",
    en = u"Child documents listing"
)

translations.define("FolderBlock-plural",
    ca = u"Llistats de documents fills",
    es = u"Listados de documentos hijos",
    en = u"Child documents listings"
)

translations.define("FolderBlock.show_hidden_children",
    ca = u"Mostrar documents ocults",
    es = u"Mostrar documentos ocultos",
    en = u"Show hidden documents"
)

translations.define("FolderBlock.show_thumbnails",
    ca = u"Mostrar miniatures",
    es = u"Mostrar miniaturas",
    en = u"Show thumbnails"
)

translations.define("FolderBlock.thumbnails_factory",
    ca = u"Processador de miniatures",
    es = u"Procesador de miniaturas",
    en = u"Thumbnail factory"
)

# LoginBlock
#------------------------------------------------------------------------------
translations.define("LoginBlock",
    ca = u"Formulari d'autenticació d'usuari",
    es = u"Formulario de autenticación de usuario",
    en = u"Login form"
)

translations.define("LoginBlock-plural",
    ca = u"Formularis d'autenticació d'usuari",
    es = u"Formularios de autenticación de usuario",
    en = u"Login forms"
)

translations.define("LoginBlock.login_target",
    ca = u"Pàgina de destí",
    es = u"Página de destino",
    en = u"Destination page"
)

translations.define("LoginBlock.login_target-explanation",
    ca = u"La pàgina que rebrà la petició d'autenticació de l'usuari",
    es = u"La pàgina que recibirá la petición de autenticación del "
         u"usuario",
    en = u"The page that will handle the user's authentication request"
)

translations.define("LoginBlockForm.user",
    ca = u"Usuari",
    es = u"Usuario",
    en = u"User"
)

translations.define("LoginBlockForm.password",
    ca = u"Contrasenya",
    es = u"Contraseña",
    en = u"Password"
)

translations.define("woost.extensions.blocks.LoginBlockView.submit_button",
    ca = u"Entrar",
    es = u"Entrar",
    en = u"Login"
)

# IFrameBlock
#------------------------------------------------------------------------------
translations.define("IFrameBlock",
    ca = u"IFrame",
    es = u"IFrame",
    en = u"IFrame"
)

translations.define("IFrameBlock-plural",
    ca = u"IFrames",
    es = u"IFrames",
    en = u"IFrames"
)

translations.define("IFrameBlock.src",
    ca = u"Adreça a mostrar",
    es = u"Dirección a mostrar",
    en = u"Content URL"
)

translations.define("IFrameBlock.width",
    ca = u"Amplada",
    es = u"Ancho",
    en = u"Width"
)

translations.define("IFrameBlock.height",
    ca = u"Alçada",
    es = u"Alto",
    en = u"Height"
)

