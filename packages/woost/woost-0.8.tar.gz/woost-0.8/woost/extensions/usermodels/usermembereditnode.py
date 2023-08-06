#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from __future__ import with_statement
from cocktail.modeling import cached_getter
from woost.controllers.backoffice.editstack import EditNode
from woost.extensions.usermodels import models_access


class UserMemberEditNode(EditNode):

    @cached_getter
    def form_adapter(self):
        form_adapter = EditNode.form_adapter(self)

        if not self.content_type.edit_controls:
            form_adapter.exclude(["member_edit_control"])

        if not self.content_type.search_controls:
            form_adapter.exclude(["member_search_control"])

        return form_adapter

    @cached_getter
    def form_schema(self):
        form_schema = EditNode.form_schema(self)
        
        edit_control = form_schema.get_member("member_edit_control")
        if edit_control:
            edit_control.enumeration = self.item.edit_controls

        search_control = form_schema.get_member("member_search_control")
        if search_control:
            search_control.enumeration = self.item.search_controls

        return form_schema

    def import_form_data(self, form_data, item):
        # Overriden to require exclusive access to application schemas. The
        # update will wait for all current requests to end, and then will block
        # any further incoming requests until the schemas have been modified.

        # The current request doesn't count when waiting for exclusive access
        # to the models:
        models_access.leave()

        # Require exclusive access
        try:
            with models_access.locking:
                return EditNode.import_form_data(self, form_data, item)
        
        # Claim usage of the models once again
        finally:
            models_access.enter()

