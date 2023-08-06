#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.modeling import cached_getter
from woost.extensions.usermodels.usermembereditnode import UserMemberEditNode


class UserModelEditNode(UserMemberEditNode):

    @cached_getter
    def form_adapter(self):
        adapter = UserMemberEditNode.form_adapter(self)
        adapter.exclude([
            "explanation",
            "member_indexed",
            "member_translated",
            "member_descriptive",
            "member_member_group",
            "member_searchable",
            "member_search_control",
            "member_editable",
            "member_listed_by_default",
            "member_edit_control",
            "member_required",
            "member_unique"
        ])
        return adapter

