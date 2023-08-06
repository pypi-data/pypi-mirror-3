#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			May 2009
"""
from cocktail.events import when
from cocktail import schema
from woost.models import Item, Action, ChangeSet
from woost.models.trigger import (
    Trigger,
    actions_with_triggers,
    _handles_action,
    trigger_responses
)
from woost.extensions.workflow.state import State

actions_with_triggers.add("transition")

Trigger.add_member(
    schema.Collection(
        "item_states",
        items = schema.Reference(type = State, required = True),
        related_end = schema.Collection(),
        edit_inline = True
    )
)

Trigger.add_member(
    schema.Collection(
        "item_previous_states",
        items = schema.Reference(type = State, required = True),
        related_end = schema.Collection(),
        #exclusive = _handles_action("transition"),
        edit_inline = True
    )
)

_base_matches = Trigger.matches

def _matches(self, item, action, user, **context):
    
    if not _base_matches(self, item, action, user, **context):
        return False

    # Check current state
    if self.item_states and item.state not in self.item_states:
        return False

    # Check source state
    if self.item_previous_states:
        previous_state = context.get("previous_state")
        if previous_state is None \
        or previous_state not in self.item_previous_states:
            return False

    return True

Trigger.matches = _matches

@when(Item.changed)
def _trigger_transition_responses(event):
    if event.member is Item.state:
        trigger_responses(
            event.source,
            Action.get_instance(identifier = "transition"),
            ChangeSet.current_author,
            previous_state = event.previous_value
        )

