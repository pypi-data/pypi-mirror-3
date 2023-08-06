#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			Aug 2009
"""
from cocktail.events import when
from cocktail import schema
from cocktail.translations import translations
from cocktail.html import templates
from woost.models import Item
from woost.extensions.workflow.state import State
from woost.extensions.workflow.transition import Transition
from woost.models.messagestyles import trigger_doesnt_match_style
from woost.models.trigger import (
    ContentTrigger,
    members_without_triggers,
    trigger_responses
)

members_without_triggers.add(Item.workflow_state)


class TransitionTrigger(ContentTrigger):

    instantiable = True

    def _transition_edit_control(parent, obj, member):
        display = templates.new("cocktail.html.DropdownSelector")
        display.empty_label = translations(
            "woost.extensions.workflow.TransitionTrigger any transition"
        )
        return display

    transition = schema.Reference(
        type = "woost.extensions.workflow.transition.Transition",
        edit_control = _transition_edit_control
    )

    del _transition_edit_control

    def match(
        self,
        user,
        target,
        transition,
        transition_data,
        verbose = False,
        **context):

        if self.transition is not None and transition is not self.transition:
            if verbose:
                print trigger_doesnt_match_style("transition doesn't match")
            return False
        
        return ContentTrigger.match(self,
            user,
            target = target,
            transition = transition,
            transition_data = transition_data,
            verbose = verbose,
            **context
        )


@when(Transition.executed)
def _trigger_transition_responses(event):
    trigger_responses(
        TransitionTrigger,
        target = event.item,
        transition = event.source,
        transition_data = event.data
    )

