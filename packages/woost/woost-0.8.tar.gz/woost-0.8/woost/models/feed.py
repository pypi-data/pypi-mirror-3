#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2009
"""
from cocktail import schema
from cocktail.controllers.usercollection import UserCollection
from woost.models.publishable import Publishable
from woost.models.language import Language
from woost.models.controller import Controller


class Feed(Publishable):

    instantiable = True

    groups_order = ["meta", "feed_items"]

    members_order = [
        "title",
        "ttl",
        "image",
        "description",
        "limit",
        "query_parameters",
        "item_title_expression",
        "item_link_expression",
        "item_publication_date_expression",
        "item_description_expression"
    ]

    default_mime_type = u"application/rss+xml"

    default_controller = schema.DynamicDefault(
        lambda: Controller.get_instance(qname = "woost.feed_controller")
    )

    edit_controller = \
        "woost.controllers.backoffice.feedfieldscontroller." \
        "FeedFieldsController"
    edit_view = "woost.views.FeedFields"

    title = schema.String(
        indexed = True,
        normalized_index = True,
        full_text_indexed = True,
        descriptive = True,
        translated = True,
        member_group = "meta"
    )           

    ttl = schema.Integer(
        listed_by_default = False,
        member_group = "meta"
    )

    image = schema.Reference(
        type = Publishable,
        related_end = schema.Collection(),
        relation_constraints = Publishable.resource_type.equal("image"),
        member_group = "meta"
    )

    description = schema.String(
        required = True,
        translated = True,
        listed_by_default = False,
        edit_control = "cocktail.html.TextArea",
        member_group = "meta"
    )

    limit = schema.Integer(
        min = 1,
        listed_by_default = False,
        member_group = "feed_items"
    )

    query_parameters = schema.Mapping(
        keys = schema.String(),
        required = True,
        listed_by_default = False,
        member_group = "feed_items"
    )

    item_title_expression = schema.CodeBlock(
        language = "python",
        required = True,
        default = "translations(item)",
        member_group = "feed_items"
    )

    item_link_expression = schema.CodeBlock(
        language = "python",
        required = True,
        default = "cms.uri(item)",
        member_group = "feed_items"
    )

    item_publication_date_expression = schema.CodeBlock(
        language = "python",
        required = True,
        default = "item.start_date or item.creation_time",
        member_group = "feed_items"
    )

    item_description_expression = schema.CodeBlock(
        language = "python",
        required = True,
        default = "item.description",
        member_group = "feed_items"
    )

    def select_items(self):
         
        user_collection = UserCollection(Publishable)
        user_collection.allow_paging = False
        user_collection.allow_member_selection = False
        user_collection.allow_language_selection = False
        user_collection.params.source = self.query_parameters.get
        user_collection.available_languages = Language.codes
        items = user_collection.subset

        if self.limit:
            items.range = (0, self.limit)

        return items

