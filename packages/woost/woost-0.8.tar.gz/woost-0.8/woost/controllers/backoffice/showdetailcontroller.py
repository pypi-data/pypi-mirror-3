#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			January 2009
"""
from cocktail.modeling import cached_getter
from cocktail.schema import Adapter, RelationMember
from woost.models import Language
from woost.controllers.backoffice.editcontroller import EditController
from woost.controllers.backoffice.useractions import get_user_action


class ShowDetailController(EditController):

    section = "show_detail"

    @cached_getter
    def detail_schema_adapter(self):
        adapter = Adapter()
        adapter.exclude([
            member.name
            for member in self.stack_node.content_type.members().itervalues()
            if not member.visible
            or not member.visible_in_detail_view
            or (
                isinstance(member, RelationMember)
                and member.is_persistent_relation
                and member.related_type
                and not member.related_type.visible
                and not member.related_type.visible_in_detail_view
            )
        ])
        adapter.exclude(["translations"])
        return adapter

    @cached_getter
    def detail_schema(self):
        content_type = self.stack_node.content_type
        adapter = self.detail_schema_adapter
        schema = adapter.export_schema(content_type)
        schema.name = content_type.name + "Detail"
        return schema

    @cached_getter
    def view_class(self):
        return self.stack_node.item.show_detail_view
    
    @cached_getter
    def output(self):
        
        # TODO: Add a translation selector
        
        output = EditController.output(self)
        output.update(
            translations = Language.codes,
            detail_schema = self.detail_schema,
            selected_action = get_user_action("show_detail")
        )

        node = self.stack_node
        node.import_form_data(node.form_data, node.item)

        return output

