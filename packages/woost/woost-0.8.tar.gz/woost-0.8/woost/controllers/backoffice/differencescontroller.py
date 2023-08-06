#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			November 2008
"""
from cocktail.modeling import cached_getter
from cocktail.schema import Collection, String, DictAccessor
from woost.controllers.backoffice.editcontroller import EditController
from woost.controllers.backoffice.useractions import get_user_action


class DifferencesController(EditController):

    view_class = "woost.views.BackOfficeDiffView"
    section = "diff"

    @cached_getter
    def source_item(self):
        item = self.stack_node.item
        return item.draft_source or item

    @cached_getter
    def output(self):
        output = EditController.output(self)
        output.update(
            submitted = False,
            source = self.source_item,
            target = self.stack_node.form_data,
            selected_action = get_user_action("diff")
        )
        return output

