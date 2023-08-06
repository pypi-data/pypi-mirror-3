#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Jordi Fernández <jordi.fernandez@whads.com>
"""
from cocktail import schema
from woost.extensions.blocks.block import Block


class ContainerBlock(Block):

    instantiable = True
    view_class = "cocktail.html.Element"

    blocks = schema.Collection(
        items = schema.Reference(type = Block),
        bidirectional = True,
        related_key = "containers",
        member_group = "content"
    )

    def descend_tree(self, include_self = False):

        if include_self:
            yield self

        for child in self.blocks:
            for descendant in child.descend_tree(include_self = True):
                yield descendant

    def create_view(self):
        
        view = Block.create_view(self)
    
        children_container = getattr(view, "block_content", view)

        for child in self.blocks:
            if child.enabled:
                child_view = child.create_view()
                children_container.append(child_view)

        return view

