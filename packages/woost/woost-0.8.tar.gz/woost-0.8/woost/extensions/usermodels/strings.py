#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.translations import translations

# UserForm
#------------------------------------------------------------------------------
translations.define("UserForm",
    ca = u"Formulari",
    es = u"Formulario",
    en = u"Form"
)

translations.define("UserForm-plural",
    ca = u"Formularis",
    es = u"Formularios",
    en = u"Forms"
)

translations.define("UserForm.form",
    ca = u"Formulari",
    es = u"Formulario",
    en = u"Form"
)

translations.define("UserForm.form_model",
    ca = u"Model",
    es = u"Modelo",
    en = u"Model"
)

translations.define("UserForm.form_model-explanation",
    ca = u"El model de dades utilitzat per generar el formulari",
    es = u"El modelo de datos utilizado para generar el formulario",
    en = u"The data model used to generate the form"
)

translations.define("UserForm.excluded_members",
    ca = u"Membres exclosos",
    es = u"Miembros excluídos",
    en = u"Excluded members"
)

translations.define("UserForm.excluded_members-explanation",
    ca = u"Membres del model que no han d'aparèixer al formulari",
    es = u"Miembros del modelo que no deben aparecer en el formulario",
    en = u"Model members that shouldn't appear on the form"
)

translations.define("UserForm.should_save_instances",
    ca = u"Desar registres",
    es = u"Guardar registros",
    en = u"Save instances"
)

translations.define("UserForm.should_save_instances-explanation",
    ca = u"Indica si les dades introduïdes pels usuaris al formulari es desen "
         u"a la base de dades",
    es = u"Indica si los datos introducidos por los usuarios en el formulario "
         u"se guardan en la base de datos",
    en = u"Indicates if submitting the form generates a new register in the "
         u"data base"
)

translations.define("UserForm.redirection",
    ca = u"Pàgina de confirmació",
    es = u"Página de confirmación",
    en = u"Confirmation page"
)

translations.define("UserForm.redirection-explanation",
    ca = u"Un document al que es redirigirà els usuaris després que completin "
         u"el formulari satisfactòriament",
    es = u"Un documento al que se redirigirá a los usuarios tras rellenar el "
         u"formulario satisfactoriamente",
    en = u"A document where users will be redirected to after they have "
         u"sucessfully submitted the form"
)

translations.define("UserForm.email_notifications",
    ca = u"Notificacions per email",
    es = u"Notificaciones por correo",
    en = u"Email notifications"
)

translations.define("woost.extensions.usermodels.user_form_controller.title",
    ca = u"Controlador de formulari",
    es = u"Controlador de formulario",
    en = u"Form controller"
)

translations.define("woost.extensions.usermodels.user_form_template.title",
    ca = u"Plantilla de formulari",
    es = u"Plantilla de formulario",
    en = u"Form template"
)

# UserMember
#------------------------------------------------------------------------------
translations.define("UserMember",
    ca = u"Membre",
    es = u"Miembro",
    en = u"Member"
)

translations.define("UserMember-plural",
    ca = u"Membres",
    es = u"Miembros",
    en = u"Members"
)

translations.define("UserMember.description",
    ca = u"Descripció",
    es = u"Descripción",
    en = u"Description"
)

translations.define("UserMember.definition",
    ca = u"Definició",
    es = u"Definición",
    en = u"Definition"
)

translations.define("UserMember.indexing",
    ca = u"Indexat",
    es = u"Indexado",
    en = u"Indexing"
)
 
translations.define("UserMember.constraints",
    ca = u"Restriccions",
    es = u"Restricciones",
    en = u"Constraints"
)

translations.define("UserMember.behavior",
    ca = u"Comportament",
    es = u"Comportamiento",
    en = u"Behavior"
)

translations.define("UserMember.code",
    ca = u"Codi personalitzat",
    es = u"Código personalizado",
    en = u"Custom code"
)

translations.define("UserMember.label",
    ca = u"Nom descriptiu",
    es = u"Nombre descriptivo",
    en = u"Descriptive name"
)

translations.define("UserMember.explanation",
    ca = u"Explicació",
    es = u"Explicación",
    en = u"Explanation"
)

translations.define("UserMember.explanation-explanation",
    ca = u"Aclaracions sobre el membre que es mostraran als formularis",
    es = u"Aclaracionens sobre el miembro que aparecerán en los formularios",
    en = u"Additional notes on the member's nature and purpose, will be "
         u"displayed on forms"
)

translations.define("UserMember.member_descriptive",
    ca = u"És descriptiu",
    es = u"Es descriptivo",
    en = u"Is descriptive"
)

translations.define("UserMember.member_descriptive-explanation",
    ca = u"El membre descriptiu d'un model és el que s'utilitza quan cal "
         u"descriure una instància del model als usuaris (als llistats, "
         u"formularis, etc)",
    es = u"El miembro descriptivo de un modelo es el que se utiliza cuando es "
         u"necesario describir una instancia del modelo a los usuarios (en "
         u"listados, formularios, etc)",
    en = u"A model's descriptive member is used to describe instances of the "
         u"model to users (in listings, forms, etc)"
)

translations.define("UserMember.member_name",
    ca = u"Nom intern",
    es = u"Nombre interno",
    en = u"Internal name"
)

translations.define("UserMember.member_name-explanation",
    ca = u"Identificador únic del membre, d'ús intern per l'aplicació",
    es = u"Identificador único del miembro, de uso interno para la aplicación",
    en = u"Unique identifier for the member, used internally by the "
         u"application"
)

translations.define("UserMember.member_translated",
    ca = u"Traduït",
    es = u"Traducido",
    en = u"Translated"
)

translations.define("UserMember.member_versioned",
    ca = u"Versionat",
    es = u"Versionado",
    en = u"Versioned"
)

translations.define("UserMember.member_versioned-explanation",
    ca = u"Indica si es manté un registre del valor del membre al llarg del "
         u"temps",
    es = u"Indica si se mantiene un registro del valor del miembro a lo largo "
         u"del tiempo",
    en = u"Indicates if the application should keep a history of the values "
         u"assigned to the member"
)

translations.define("UserMember.member_indexed",
    ca = u"Indexat",
    es = u"Indexado",
    en = u"Indexed"
)

translations.define("UserMember.member_indexed-explanation",
    ca = u"Accelera les cerques basades en aquest membre, a costa de "
         u"penalitzar-ne la modificació. Establir només si el membre serà "
         u"cercat freqüentment.",
    es = u"Acelera las búsquedas basadas en este miembro, a costa de "
         u"penalizar su modificación. Establecer solo si el miembro será "
         u"usado frecuentemente como criterio de búsqueda.",
    en = u"Greatly accelerates searches based on this member, but makes "
         u"updates more costly. Use only on members which will be frequently "
         u"used as search criteria."
)

translations.define("UserMember.initialization",
    ca = u"Codi d'inicialització",
    es = u"Código de inicialización",
    en = u"Initialization code"
)

translations.define("UserMember.member_unique",
    ca = u"Exigeix valor únic",
    es = u"Exige valor único",
    en = u"Requires unique value"
)

translations.define("UserMember.member_member_group",
    ca = u"Grup",
    es = u"Grupo",
    en = u"Group"
)

translations.define("UserMember.member_required",
    ca = u"Obligatori",
    es = u"Obligatorio",
    en = u"Required"
)

translations.define("UserMember.member_default",
    ca = u"Valor per defecte",
    es = u"Valor por defecto",
    en = u"Default value"
)

translations.define("UserMember.member_enumeration",
    ca = u"Valors vàlids",
    es = u"Valores válidos",
    en = u"Valid values"
)

translations.define("UserMember.member_listed_by_default",
    ca = u"Apareix al llistat per defecte",
    es = u"Aparece en el listado por defecto",
    en = u"Included in the default listing"
)

translations.define("UserMember.member_editable",
    ca = u"Editable",
    es = u"Editable",
    en = u"Editable"
)

translations.define("UserMember.member_edit_control",
    ca = u"Control d'edició",
    es = u"Control de edición",
    en = u"Edit control"
)

translations.define("UserMember.member_searchable",
    ca = u"Cercable",
    es = u"Admite búsquedas",
    en = u"Searchable"
)

translations.define("UserMember.member_search_control",
    ca = u"Control per les cerques",
    es = u"Control para las búsquedas",
    en = u"Search control"
)

for model_name in (
    "UserInteger",
    "UserFloat",
    "UserDecimal",
    "UserFraction",
    "UserDate",
    "UserTime",
    "UserDateTime"
):
    translations.define(model_name + ".member_min",
        ca = u"Valor mínim",
        es = u"Valor mínimo",
        en = u"Minimum value"
    )
    translations.define(model_name + ".member_max",
        ca = u"Valor màxim",
        es = u"Valor máximo",
        en = u"Maximum value"
    )

# UserBoolean
#------------------------------------------------------------------------------
translations.define("UserBoolean",
    ca = u"Cert o fals",
    es = u"Cierto o falso",
    en = u"True or false"
)

translations.define("UserBoolean-plural",
    ca = u"Cert o fals",
    es = u"Cierto o falso",
    en = u"True or false"
)

# UserInteger
#------------------------------------------------------------------------------
translations.define("UserInteger",
    ca = u"Número enter",
    es = u"Número entero",
    en = u"Integer number"
)

translations.define("UserInteger-plural",
    ca = u"Números enters",
    es = u"Números enteros",
    en = u"Integer numbers"
)

# UserFloat
#------------------------------------------------------------------------------
translations.define("UserFloat",
    ca = u"Número de coma flotant",
    es = u"Número de coma flotante",
    en = u"Floating point number"
)

translations.define("UserFloat-plural",
    ca = u"Números de coma flotant",
    es = u"Números de coma flotante",
    en = u"Floating point numbers"
)

# UserDecimal
#------------------------------------------------------------------------------
translations.define("UserDecimal",
    ca = u"Número decimal",
    es = u"Número decimal",
    en = u"Decimal number"
)

translations.define("UserDecimal-plural",
    ca = u"Números decimals",
    es = u"Números decimales",
    en = u"Decimal numbers"
)

# UserFraction
#------------------------------------------------------------------------------
translations.define("UserFraction",
    ca = u"Número fraccional",
    es = u"Número fraccional",
    en = u"Fractional number"
)

translations.define("UserFraction-plural",
    ca = u"Números fraccionals",
    es = u"Números fraccionales",
    en = u"Fractional numbers"
)

# UserString
#------------------------------------------------------------------------------
translations.define("UserString",
    ca = u"Text",
    es = u"Texto",
    en = u"Text"
)

translations.define("UserString-plural",
    ca = u"Textos",
    es = u"Textos",
    en = u"Texts"
)

translations.define("UserString.member_min",
    ca = u"Longitud mínima",
    es = u"Longitud mínima",
    en = u"Minimum length"
)

translations.define("UserString.member_max",
    ca = u"Longitud màxima",
    es = u"Longitud máxima",
    en = u"Maximum length"
)

translations.define("UserString.member_format",
    ca = u"Format",
    es = u"Formato",
    en = u"Format"
)

translations.define("UserString.member_text_search",
    ca = u"Incloure a les cerques de text",
    es = u"Incluir en las búsquedas de texto",
    en = u"Include in full text search"
)

translations.define("UserString.member_normalized_index",
    ca = u"Index normalitzat",
    es = u"Índice normalizado",
    en = u"Normalized index"
)

# UserDate
#------------------------------------------------------------------------------
translations.define("UserDate",
    ca = u"Data",
    es = u"Fecha",
    en = u"Date"
)

translations.define("UserDate-plural",
    ca = u"Dates",
    es = u"Fechas",
    en = u"Dates"
)

# UserDate
#------------------------------------------------------------------------------
translations.define("UserTime",
    ca = u"Hora",
    es = u"Hora",
    en = u"Time"
)

translations.define("UserTime-plural",
    ca = u"Hores",
    es = u"Horas",
    en = u"Times"
)

# UserDateTime
#------------------------------------------------------------------------------
translations.define("UserDateTime",
    ca = u"Data i hora",
    es = u"Fecha y hora",
    en = u"Date and time"
)

translations.define("UserDateTime-plural",
    ca = u"Data i hora",
    es = u"Fecha y hora",
    en = u"Date and time"
)

# UserRelation
#------------------------------------------------------------------------------
translations.define("UserRelation",
    ca = u"Relació",
    es = u"Relación",
    en = u"Relation"
)

translations.define("UserRelation-plural",
    ca = u"Relacions",
    es = u"Relaciones",
    en = u"Relations"
)

translations.define("UserRelation.member_related_key",
    ca = u"Nom del membre relacionat",
    es = u"Nombre del miembro relacionado",
    en = u"Related key"
)

translations.define("UserRelation.member_bidirectional",
    ca = u"Bidireccional",
    es = u"Bidirectional",
    en = u"Bidireccional"
)

translations.define("UserRelation.member_integral",
    ca = u"Integral",
    es = u"Integral",
    en = u"Integral"
)

translations.define("UserRelation.member_cascade_delete",
    ca = u"Eliminació en cascada",
    es = u"Eliminación en cascada",
    en = u"Cascade delete"
)

translations.define("UserRelation.member_text_search",
    ca = u"Incloure a les cerques de text",
    es = u"Incluir en las búsquedas de texto",
    en = u"Include in full text search"
)

# UserReference
#------------------------------------------------------------------------------
translations.define("UserReference",
    ca = u"Referència",
    es = u"Referencia",
    en = u"Reference"
)

translations.define("UserReference-plural",
    ca = u"Referències",
    es = u"Referencias",
    en = u"References"
)

translations.define("UserReference.member_type",
    ca = u"Tipus d'objecte",
    es = u"Tipo de objeto",
    en = u"Object type"
)

translations.define("UserReference.member_class_family",
    ca = u"Referència de classe",
    es = u"Referencia de clase",
    en = u"Class reference"
)

translations.define("UserReference.member_cycles_allowed",
    ca = u"Permetre cicles",
    es = u"Permitir ciclos",
    en = u"Cycles allowed",
)

# UserCollection
#------------------------------------------------------------------------------
translations.define("UserCollection",
    ca = u"Col·lecció",
    es = u"Colección",
    en = u"Collection"
)

translations.define("UserCollection-plural",
    ca = u"Col·leccions",
    es = u"Collections",
    en = u"Collection"
)

translations.define("UserCollection.member_items",
    ca = u"Elements de la col·lecció",
    es = u"Elementos de la colección",
    en = u"Collection items"
)

translations.define("UserCollection.member_min",
    ca = u"Mida mínima",
    es = u"Tamaño mínimo",
    en = u"Minimum size"
)

translations.define("UserCollection.member_max",
    ca = u"Mida màxima",
    es = u"Tamaño máximo",
    en = u"Maximum size"
)

translations.define("UserCollection.member_items",
    ca = u"Elements de la col·lecció",
    es = u"Elementos de la colección",
    en = u"Collection items"
)

# UserModel
#------------------------------------------------------------------------------
translations.define("UserModel",
    ca = u"Model d'usuari",
    es = u"Modelo de usuario",
    en = u"User model"
)

translations.define("UserModel-plural",
    ca = u"Models d'usuari",
    es = u"Modelos de usuario",
    en = u"User models"
)

translations.define("UserModel.plural_label",
    ca = u"Nom descriptiu en plural",
    es = u"Nombre descriptivo en plural",
    en = u"Plural descriptive name"
)

translations.define("UserModel.package_name",
    ca = u"Nom del paquet",
    es = u"Nombre del paquete",
    en = u"Package name"
)

translations.define("UserModel.base_model",
    ca = u"Model base",
    es = u"Modelo base",
    en = u"Base model"
)

translations.define("UserModel.child_members",
    ca = u"Membres",
    es = u"Miembros",
    en = u"Members"
)

translations.define("UserModel.member_instantiable",
    ca = u"Instanciable",
    es = u"Instanciable",
    en = u"Instantiable"
)

translations.define("UserModel.member_visible_from_root",
    ca = u"Visible al llistat principal",
    es = u"Visible en el listado principal",
    en = u"Visible in the main listing"
)

# UI controls
#------------------------------------------------------------------------------
translations.define("woost.extensions.usermodels.auto-control",
    ca = u"Automàtic",
    es = u"Automático",
    en = u"Automatic"
)

translations.define("cocktail.html.TextBox",
    ca = u"Caixa de text",
    es = u"Caja de texto",
    en = u"Text box"
)

translations.define("cocktail.html.PasswordBox",
    ca = u"Caixa de contrasenya",
    es = u"Caja de contraseña",
    en = u"Password box"
)

translations.define("cocktail.html.TextArea",
    ca = u"Caixa de text multilínia",
    es = u"Caja de texto multilinea",
    en = u"Multiline text box"
)

translations.define("woost.views.RichTextEditor",
    ca = u"Editor de text avançat",
    es = u"Editor de texto avanzado",
    en = u"Rich text editor"
)

translations.define("cocktail.html.CheckBox",
    ca = u"Casella de verificació",
    es = u"Casilla de verificación",
    en = u"Check box"
)

translations.define("cocktail.html.RadioSelector",
    ca = u"Botons de radio",
    es = u"Botones de radio",
    en = u"Radio buttons"
)

translations.define("cocktail.html.CheckList",
    ca = u"Llistat de caselles de verificació",
    es = u"Listado de casillas de verificación",
    en = u"Check list"
)

translations.define("cocktail.html.MultipleChoiceSelector",
    ca = u"Quadre de diàleg amb múltiples opcions",
    es = u"Ventana modal con múltiples opciones",
    en = u"Multiple choices dialog window"
)

translations.define("cocktail.html.DropdownSelector",
    ca = u"Selector desplegable",
    es = u"Selector desplegable",
    en = u"Dropdown selector"
)

translations.define("woost.views.ItemSelector",
    ca = u"Selector d'element relacionat",
    es = u"Selector de elemento relacionado",
    en = u"Related item selector"
)

translations.define("cocktail.html.DatePicker",
    ca = u"Selector de data/hora",
    es = u"Selector de fecha/hora",
    en = u"Date/time selector"
)

