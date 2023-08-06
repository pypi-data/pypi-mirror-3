#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			November 2009
"""
from __future__ import with_statement
import cherrypy
from cocktail.modeling import cached_getter
from cocktail.events import event_handler
from cocktail.pkgutils import import_object
from cocktail.translations import translations
from cocktail import schema
from cocktail.persistence import datastore
from cocktail.controllers import (
    get_parameter,
    FormControllerMixin
)
from cocktail.controllers.viewstate import view_state
from woost.models import (
    Item,
    get_current_user,
    ReadPermission,
    ModifyPermission
)
from woost.models.changesets import changeset_context
from woost.controllers import notify_user
from woost.controllers.backoffice.basebackofficecontroller \
    import BaseBackOfficeController
from woost.controllers.backoffice.itemfieldscontroller \
    import ItemFieldsController
from woost.controllers.backoffice.collectioncontroller \
    import CollectionController
from woost.extensions.workflow.transition import Transition
from woost.extensions.workflow.transitionpermission \
    import TransitionPermission


class TransitionController(FormControllerMixin, BaseBackOfficeController):

    view_class = "woost.extensions.workflow.TransitionView"

    @event_handler
    def handle_traversed(cls, event):
        controller = event.source        
        get_current_user().require_permission(
            TransitionPermission,
            target = controller.item,
            transition = controller.transition
        )

    @cached_getter
    def item(self):
    
        item = get_parameter(schema.Reference("item", type = Item))

        if item is None or item.workflow_state is None:
            raise ValueError("Invalid item selected")

        return item

    @cached_getter
    def transition(self):

        transition = get_parameter(
            schema.Reference("transition", type = Transition)
        )

        if transition is None \
        or transition not in self.item.workflow_state.outgoing_transitions:
            raise ValueError("Invalid transition selected")

        return transition

    @cached_getter
    def form_model(self):
        form_model =  import_object(self.transition.transition_form)

        if isinstance(form_model, schema.Schema):
            return form_model
        elif callable(form_model):
            form_model = form_model(self.item, self.transition)
            if isinstance(form_model, schema.Schema):
                return form_model

        raise ValueError("Invalid transition form")

    @cached_getter
    def form_errors(self):

        if "cancel" in cherrypy.request.params:
           return schema.ErrorList([])
        else:
            return FormControllerMixin.form_errors(self)

    @cached_getter
    def form_validation_context(self):
        context = FormControllerMixin.form_validation_context(self)
        context.update(
            workflow_item = self.item,
            workflow_transition = self.transition
        )
        return context

    def submit(self):
        
        item = self.item
        draft_source = item.draft_source

        if cherrypy.request.method == "POST" \
        and not "cancel" in cherrypy.request.params:

            # Apply form data
            FormControllerMixin.submit(self)

            transition = self.transition

            # Authorization check
            user = get_current_user()
            user.require_permission(
                TransitionPermission,
                target = item,
                transition = transition
            )

            # Execute the transition
            with changeset_context(user):
                transition.execute(item, data = self.form_instance)
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
        
        # Redirect the user to the transitioned item's edit form
        redirect_transition(item if item.is_inserted else draft_source)

    @cached_getter
    def output(self):
        output = BaseBackOfficeController.output(self)
        output.update(
            item = self.item,
            transition = self.transition
        )
        return output

def redirect_transition(item):
    """ GET redirection, to avoid duplicate POST requests. Also, permissions
    that allowed the user to edit or view the transitioned item may no
    longer apply (as they may have been granted by the item's previous
    state). If that is the case, redirect the user to the best available
    view """

    user = get_current_user()
    controller = cherrypy.request.handler_chain[-1]
    cms = controller.context["cms"]
    url = None

    if isinstance(
        controller,
        (ItemFieldsController, CollectionController, TransitionController)
    ):
        if not user.has_permission(ModifyPermission, target = item):
            if user.has_permission(ReadPermission, target = item):
                url = controller.edit_uri(item, "show_detail")
            else:
                url = cms.contextual_uri()
        elif isinstance(controller, TransitionController):
            if controller.edit_stack:
                controller.go_back()
            else:
                url = controller.edit_uri(item, "show_detail")

    elif not user.has_permission(ReadPermission, target = item):
        url = cms.contextual_uri()

    raise cherrypy.HTTPRedirect(
        url or "?" + view_state(item_action = None, transition = None)
    )

