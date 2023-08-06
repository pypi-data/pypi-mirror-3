#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2009
"""
from cocktail.events import Event
from cocktail import schema
from woost.models import Item


class Transition(Item):
    """A transition between two item states."""

    visible_from_root = False

    executed = Event("""An event triggered when the transition is executed.
        
        @var item: The item that the transition is executed on.
        @type item: L{Item<woost.models.item.Item>}

        @var data: Additional data supplied to the transition, as required by
            its L{schema<transition_form>}.
        @type data: dict
        """)

    members_order = [
        "title",
        "source_state",
        "target_state",
        "transition_form",
        "transition_permissions"
    ]

    title = schema.String(
        required = True,
        descriptive = True,
        translated = True
    )

    source_state = schema.Reference(
        type = "woost.extensions.workflow.state.State",
        related_key = "outgoing_transitions",
        bidirectional = True,
        edit_control = "cocktail.html.DropdownSelector"
    )

    target_state = schema.Reference(
        type = "woost.extensions.workflow.state.State",
        related_key = "incoming_transitions",
        bidirectional = True,
        edit_control = "cocktail.html.DropdownSelector"
    )

    transition_form = schema.String(
        text_search = False
    )

    transition_permissions = schema.Collection(
        items = "woost.extensions.workflow.transitionpermission."
                "TransitionPermission",
        related_key = "transition",
        bidirectional = True
    )

    def execute(self, item, data = None):
        
        if item.workflow_state is not self.source_state:
            raise ValueError(
                "Can't execute the transition on the indicated item"
            )

        item.workflow_state = self.target_state
        self.executed(item = item, data = data)
