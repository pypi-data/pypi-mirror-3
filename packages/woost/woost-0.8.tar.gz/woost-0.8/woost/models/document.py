#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from cocktail import schema
from cocktail.modeling import getter
from cocktail.iteration import first
from cocktail.events import event_handler
from cocktail.controllers.renderingengines import get_rendering_engine
from woost.models.publishable import Publishable
from woost.models.file import File
from woost.models.controller import Controller


class Document(Publishable):

    instantiable = True
    default_per_language_publication = True

    groups_order = [
        "content", "navigation", "presentation", "publication", "meta",
        "robots"
    ]

    members_order = (
        "title",
        "inner_title",        
        "template",
        "description",
        "keywords",
        "attachments",
        "page_resources",
        "branch_resources",
        "children",
        "robots_should_index",
        "robots_should_follow"
    )

    default_controller = schema.DynamicDefault(
        lambda: Controller.get_instance(qname = "woost.document_controller")
    )

    title = schema.String(
        indexed = True,
        normalized_index = True,
        full_text_indexed = True,
        descriptive = True,
        translated = True,
        required = True,
        member_group = "content"
    )

    inner_title = schema.String(
        translated = True,
        listed_by_default = False,
        member_group = "content"
    )

    description = schema.String(
        translated = True,
        listed_by_default = False,
        edit_control = "cocktail.html.TextArea",
        member_group = "meta"
    )

    keywords = schema.String(
        translated = True,
        listed_by_default = False,
        edit_control = "cocktail.html.TextArea",
        member_group = "meta"
    )

    template = schema.Reference(
        type = "woost.models.Template",
        bidirectional = True,
        listed_by_default = False,
        member_group = "presentation"
    )

    branch_resources = schema.Collection(
        items = schema.Reference(
            type = Publishable,
            required = True,
            relation_constraints =
                Publishable.resource_type.equal("html_resource")
        ),
        related_end = schema.Collection()
    )

    page_resources = schema.Collection(
        items = schema.Reference(
            type = Publishable,
            required = True,
            relation_constraints =
                Publishable.resource_type.equal("html_resource")
        ),
        related_end = schema.Collection()
    )

    attachments = schema.Collection(
        items = schema.Reference(
            type = Publishable,
            required = True
        ),
        selector_default_type = File,
        related_end = schema.Collection()
    )
 
    children = schema.Collection(
        items = "woost.models.Publishable",
        bidirectional = True,
        related_key = "parent",
        cascade_delete = True
    )

    robots_should_index = schema.Boolean(
        required = True,
        default = True,
        listed_by_default = False,
        member_group = "robots"
    )

    robots_should_follow = schema.Boolean(
        required = True,
        default = True,
        listed_by_default = False,
        member_group = "robots"
    )

    def _update_path(self, parent, path):

        Publishable._update_path(self, parent, path)

        if self.children:
            for child in self.children:
                child._update_path(self, child.path)

    def descend_tree(self, include_self = False):

        if include_self:
            yield self

        if self.children:
            for child in self.children:
                for descendant in child.descend_tree(True):
                    yield descendant

    @getter
    def resources(self):
        """Iterates over all the resources that apply to the page.
        @type: L{Publishable}
        """
        for resource in self.inherited_resources:
            yield resource

        for resource in self.branch_resources:
            yield resource

        for resource in self.page_resources:
            yield resource

    def render(self, **values):
        """Renders the document using its template."""
        if self.template is None:
            raise ValueError("Can't render a document without a template")
        
        values["publishable"] = self
        engine = get_rendering_engine(self.template.engine)
        return engine.render(values, template = self.template.identifier)

    @property
    def default_image(self):
        return first(
            attachment
            for attachment in self.attachments
            if attachment.resource_type == "image"
            and attachment.is_accessible()
        )

