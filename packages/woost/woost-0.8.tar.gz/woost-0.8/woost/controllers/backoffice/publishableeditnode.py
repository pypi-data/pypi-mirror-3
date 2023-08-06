#-*- coding: utf-8 -*-
u"""

@author:		Javier Marrero
@contact:		javier.marrero@whads.com
@organization:	Whads/Accent SL
@since:			February 2009
"""
from cocktail.modeling import cached_getter
from woost.controllers.backoffice.editstack import EditNode


class PublishableEditNode(EditNode):

    @cached_getter
    def form_adapter(self):
        adapter = EditNode.form_adapter(self)
        adapter.exclude([
            "enabled"
            if self.item.per_language_publication
            else "translation_enabled"
        ])
        return adapter

