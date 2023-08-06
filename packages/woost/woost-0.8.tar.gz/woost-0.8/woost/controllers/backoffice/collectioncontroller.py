#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""
from cocktail.modeling import cached_getter
from cocktail import schema
from woost.controllers.backoffice.contentviews \
    import relation_content_views
from woost.controllers.backoffice.contentcontroller \
    import ContentController
from woost.controllers.backoffice.editcontroller import EditController
from woost.controllers.backoffice.useractions import get_user_action


class CollectionController(EditController, ContentController):
 
    view_class = "woost.views.BackOfficeCollectionView"

    def __init__(self, member):
        ContentController.__init__(self)
        EditController.__init__(self)
        self.member = member
        self.section = member.name

    @cached_getter
    def root_content_type(self):
        return self.member.items.type

    @cached_getter
    def action(self):
        return self.edited_item_action or self.collection_action

    @cached_getter
    def edited_item_action(self):
        return EditController.action(self)
    
    @cached_getter
    def collection_action(self):
        return self._get_user_action("collection_action")

    @cached_getter
    def action_content(self):
        if self.collection_action:
            return self.user_collection.selection
        else:
            return EditController.action_content(self)

    @cached_getter
    def user_collection(self):
        user_collection = ContentController.user_collection(self)
        user_collection.content_views_registry = relation_content_views
        user_collection.base_collection = \
            schema.get(self.stack_node.form_data, self.member)
        user_collection.default_order = None
        return user_collection

    @cached_getter
    def view_class(self):
        return self.member.edit_view or self.stack_node.item.collection_view

    @cached_getter
    def output(self):
        output = ContentController.output(self)
        output.update(EditController.output(self))
        output.update(
            member = self.member,
            selected_action = get_user_action("edit")
        )
        return output

