#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			May 2009
"""
from cocktail.translations import translations
from cocktail.translations.helpers import ca_possessive
from woost.translations.strings import content_permission_translation_factory

translations.define(
    "woost.controllers.backoffice.useractions.TransitionAction state set",
    ca = lambda item: u"S'ha canviat l'estat de <em>%s</em> a <em>%s</em>"
        % (translations(item, "ca"), translations(item.workflow_state, "ca")),
    es = lambda item: u"Se ha cambiado el estado de <em>%s</em> a <em>%s</em>"
        % (translations(item, "es"), translations(item.workflow_state, "es")),
    en = lambda item: u"State of <em>%s</em> changed to <em>%s</em>"
        % (translations(item, "en"), translations(item.workflow_state, "en"))
)

# Item
#------------------------------------------------------------------------------
translations.define("Item.workflow_state",
    ca = u"Estat",
    es = u"Estado",
    en = u"State"
)

# TransitionPermission
#------------------------------------------------------------------------------
translations.define("TransitionPermission",
    ca = u"Permís de transició",
    es = u"Permiso de transición",
    en = u"Transition permission"
)

translations.define("TransitionPermission-plural",
    ca = u"Permisos de transició",
    es = u"Permisos de transición",
    en = u"Transition permissions"
)

translations.define("TransitionPermission.transition",
    ca = u"Transició",
    es = u"Transición",
    en = u"Transition"
)

translations.define(
    "woost.extensions.workflow.transitionpermission."
    "TransitionPermission-instance",
    ca = content_permission_translation_factory("ca",
        lambda permission, subject, **kwargs:
            "%s %s" % (    
                translations(permission.transition, "ca", **kwargs),
                subject
            )            
            if permission.transition
            else "canviar l'estat " + ca_possessive(subject),
    ),
    es = content_permission_translation_factory("es",
        lambda permission, subject, **kwargs:
            "%s %s" % (    
                translations(permission.transition, "es", **kwargs),
                subject
            )            
            if permission.transition
            else "cambiar el estado de " + subject,
    ),
    en = content_permission_translation_factory("en",
        lambda permission, subject, **kwargs:
            "%s %s" % (
                translations(permission.transition, "en", **kwargs),
                subject
            )            
            if permission.transition
            else "change the state of " + subject
    )
)

# TransitionTrigger
#------------------------------------------------------------------------------
translations.define("TransitionTrigger",
    ca = u"Disparador de transició",
    es = u"Disparador de transición",
    en = u"Transition trigger"
)

translations.define("TransitionTrigger-plural",
    ca = u"Disparadors de transició",
    es = u"Disparadores de transición",
    en = u"Transition triggers"
)

translations.define("TransitionTrigger.transition",
    ca = u"Transició a observar",
    es = u"Transición a observar",
    en = u"Watched transition"
)

# State
#------------------------------------------------------------------------------
translations.define("State",
    ca = u"Estat",
    es = u"Estado",
    en = u"State"
)

translations.define("State-plural",
    ca = u"Estats",
    es = u"Estados",
    en = u"States"
)

translations.define("State.title",
    ca = u"Nom",
    es = u"Nombre",
    en = u"Name"
)

translations.define("State.outgoing_transitions",
    ca = u"Transicions de sortida",
    es = u"Transiciones de salida",
    en = u"Outgoing transitions"
)

translations.define("State.incoming_transitions",
    ca = u"Transicions d'entrada",
    es = u"Transiciones de entrada",
    en = u"Incoming transitions"
)

# Transition
#------------------------------------------------------------------------------
translations.define("Transition",
    ca = u"Transició",
    es = u"Transición",
    en = u"Transition"
)

translations.define("Transition-plural",
    ca = u"Transicions",
    es = u"Transiciones",
    en = u"Transitions"
)

translations.define("Transition.title",
    ca = u"Nom",
    es = u"Nombre",
    en = u"Title"
)

translations.define("Transition.source_state",
    ca = u"Estat origen",
    es = u"Estado origen",
    en = u"Source state"
)

translations.define("Transition.target_state",
    ca = u"Estat destí",
    es = u"Estado destino",
    en = u"Target state"
)

translations.define("Transition.transition_form",
    ca = u"Formulari de transició",
    es = u"Formulario de transición",
    en = u"Transition form"
)

translations.define("Transition.transition_permissions",
    ca = u"Permisos",
    es = u"Permisos",
    en = u"Permissions"
)

# SetStateTriggerResponse
#------------------------------------------------------------------------------
translations.define("SetStateTriggerResponse",
    ca = u"Canvi d'estat",
    es = u"Cambio de estado",
    en = u"State change"
)

translations.define("SetStateTriggerResponse-plural",
    ca = u"Canvis d'estat",
    es = u"Cambios de estado",
    en = u"State changes"
)

translations.define("SetStateTriggerResponse.target_state",
    ca = u"Estat de destí",
    es = u"Estado de destino",
    en = u"Destination state"
)

# TransitionAction
#------------------------------------------------------------------------------
translations.define("Action transition",
    ca = u"Transició",                                                                                                                                                                                    
    es = u"Transición",
    en = u"Transition"
)

# Views
#------------------------------------------------------------------------------
translations.define(
    "woost.extensions.workflow any transition",
    ca = u"Qualsevol",
    es = u"Cualquiera",
    en = u"Any"
)

translations.define(
    "woost.extensions.workflow.TransitionView cancel",                                                                                                                                                     
    ca = u"Cancel·lar",
    es = u"Cancelar",
    en = u"Cancel"
)

translations.define(
    "woost.extensions.workflow.TransitionView title",
    ca = lambda item, transition: u"%s l'element %s" % (
        transition.title, translations(item)
    ),
    es = lambda item, transition: u"%s el elemento %s" % (
        transition.title, translations(item)
    ),
    en = lambda item, transition: u"%s the %s item" % (
        transition.title, translations(item)
    )
)

