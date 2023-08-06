#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2009
"""
from cocktail.translations import translations
from cocktail import schema
from cocktail.html import templates
from woost.models.messagestyles import permission_doesnt_match_style
from woost.models.permission import ContentPermission


class TransitionPermission(ContentPermission):
    """Permission to apply a state transition to an item."""

    instantiable = True

    def _transition_edit_control(parent, obj, member):
        display = templates.new("cocktail.html.DropdownSelector")
        display.empty_label = translations(
            "woost.extensions.workflow any transition"
        )
        return display

    transition = schema.Reference(
        type = "woost.extensions.workflow.transition.Transition",
        related_key = "transition_permissions",
        bidirectional = True,
        edit_control = _transition_edit_control
    )

    del _transition_edit_control

    def match(self, target, transition, verbose = False):
        
        if self.transition and transition is not self.transition:
            print permission_doesnt_match_style("transition doesn't match")
            return False

        return ContentPermission.match(self, target, verbose)

