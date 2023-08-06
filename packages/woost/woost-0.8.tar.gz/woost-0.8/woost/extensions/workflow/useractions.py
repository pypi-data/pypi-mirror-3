#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			May 2009
"""
from __future__ import with_statement
from cocktail.translations import translations
from cocktail import schema
from cocktail.persistence import datastore
from cocktail.controllers import get_parameter, context as controller_context
from cocktail.controllers.viewstate import view_state
from cocktail.html import Element
from woost.models import get_current_user
from woost.models.changesets import changeset_context
from woost.controllers import notify_user
from woost.controllers.backoffice.useractions import UserAction
from woost.extensions.workflow.transitionpermission import \
    TransitionPermission
from woost.extensions.workflow.transition import Transition
from woost.extensions.workflow.transitioncontroller import \
    redirect_transition


class TransitionAction(UserAction):
 
    included = frozenset(["item_buttons"])
    excluded = frozenset(["new_item"])

    def is_available(self, context, target):
 
        # Hide the transition action unless there are one or more available
        # outgoing states for the item's current condition
        return UserAction.is_available(self, context, target) \
            and bool(self._get_outgoing_transitions(target))
    
    def get_dropdown_panel(self, item):
        
        panel = Element()

        for transition in self._get_outgoing_transitions(item):
            
            button = Element("a")

            # Transitions with parameters: redirect to the transition form
            if transition.transition_form:
                button["href"] = controller_context["cms"].contextual_uri(
                    "workflow_transition",
                    item = item.id,
                    transition = transition.id
                )

            # This should really be a POST operation, but HTML doesn't provide
            # multi-value buttons, so regular links and GET requests are all
            # that is left :(
            else:
                button["href"] = u"?" + view_state(
                    transition = transition.id,
                    item_action = "transition"
                )

            button.append(translations(transition))            
            panel.append(button)

        return panel

    def _get_outgoing_transitions(self, item, restricted = True):

        if item.workflow_state is None:
            transitions = []
        else:
            transitions = item.workflow_state.outgoing_transitions

        if restricted:
            user = get_current_user()
            transitions = [
                transition
                for transition in transitions
                if user.has_permission(
                    TransitionPermission,
                    target = item,
                    transition = transition
                )
            ]

        return transitions

    def invoke(self, controller, selection):
        
        item = selection[0]
        draft_source = item.draft_source

        # Retrieve and validate the desired transition for the item
        transition = get_parameter(
            schema.Reference(
                "transition",
                type = Transition,
                enumeration = self._get_outgoing_transitions(
                    item,
                    # This allows to discriminate between invalid ids and authz
                    # errors:
                    restricted = False
                )
            )            
        )

        if transition is None:
            raise ValueError("Wrong transition identifier")

        # Authorization check
        user = get_current_user()
        user.require_permission(
            TransitionPermission,
            target = item,
            transition = transition
        )

        # Transition the item to its new state
        with changeset_context(user):
            transition.execute(item)
            datastore.commit()

        # Inform the user of the result
        notify_user(
            translations(
                "woost.controllers.backoffice.useractions.TransitionAction"
                " state set",
                item = item
            ),
            "success"
        )

        redirect_transition(item if item.is_inserted else draft_source)

TransitionAction("transition").register(before = "close")

