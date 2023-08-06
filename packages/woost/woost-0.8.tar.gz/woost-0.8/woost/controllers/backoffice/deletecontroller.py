#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			February 2009
"""
from ZODB.POSException import ConflictError
from cocktail.translations import translations
from cocktail.schema import String, Collection
from cocktail.persistence import datastore, delete_dry_run
from cocktail.controllers import request_property
from woost.models import (
    changeset_context,
    delete_validating,
    get_current_user
)
from woost.controllers.notifications import notify_user
from woost.controllers.backoffice.editstack import EditNode
from woost.controllers.backoffice.basebackofficecontroller \
    import BaseBackOfficeController


class DeleteController(BaseBackOfficeController):
    
    MAX_TRANSACTION_ATTEMPTS = 3

    @request_property
    def selection(self):
        """The selected subset of items that should be deleted.
        @type: L{Item<woost.models.item.Item>} collection
        """
        return self.params.read(
            Collection("selection", items = "woost.models.Item"))

    @request_property
    def delete_dry_run(self):
        visited = set()
        return [delete_dry_run(item, visited) for item in self.selection]

    @request_property
    def action(self):
        """A string identifier indicating the action that has been activated by
        the user.
        @type: str or None
        """
        return self.params.read(String("action"))

    @request_property
    def submitted(self):
        return self.action is not None
    
    def submit(self):
        # Load the edit stack before deleting any item, to ensure its
        # loaded properly
        stack = self.edit_stack

        if self.action == "confirm_delete":
            
            user = get_current_user()

            for i in range(self.MAX_TRANSACTION_ATTEMPTS):

                deleted_set = None

                with changeset_context(author = user):
                    for item in self.selection:
                        deleted_set = delete_validating(
                            item,
                            deleted_set = deleted_set
                        )

                try:
                    datastore.commit()
                except ConflictError:
                    datastore.abort()
                    datastore.sync()
                else:
                    break       
          
            # Purge the edit stack of references to deleted items
            if stack:
                prev_stack_size = len(stack)
                stack.remove_references(deleted_set)
            
            # Launch CMS.item_deleted events
            cms = self.context["cms"]

            for item in deleted_set:
                cms.item_deleted(
                    item = item,
                    user = user,
                    change = item.changes[-1] if item.changes else None
                )

            # If the edit stack has been modified as a result of the delete
            # operation (an edited item has been deleted), redirect the user
            # to the topmost edit node, or to the application root
            if stack is not None and len(stack) < prev_stack_size:

                while len(stack) > 0 \
                and not isinstance(stack[-1], EditNode):
                    stack.pop()
                
                notify_user(
                    translations(
                        "woost.controllers.DeleteController."
                        "node_deleted_notice"
                    ),
                    category = "error",
                    transient = True
                )

        if stack:
            stack.go()
        else:
            self.go_back()

    view_class = "woost.views.BackOfficeDeleteView"

    @request_property
    def output(self):
        output = BaseBackOfficeController.output(self)
        output["delete_dry_run"] = self.delete_dry_run
        return output

