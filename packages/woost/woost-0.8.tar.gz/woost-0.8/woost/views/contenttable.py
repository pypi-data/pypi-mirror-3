#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2008
"""
from cocktail.pkgutils import resolve
from cocktail.translations import translations
from cocktail.schema import Reference
from cocktail.schema.expressions import (
    PositiveExpression,
    NegativeExpression
)
from cocktail.html import Element, templates
from cocktail.controllers import view_state
from woost.models import Item
from woost.views.contentdisplaymixin import ContentDisplayMixin

Table = templates.get_class("cocktail.html.Table")


class ContentTable(ContentDisplayMixin, Table):
    
    base_url = None
    inline_draft_copies = True
    entry_selector = "tbody tr.item_row"
    resizable_rows_selector = "tbody tr.item_row"

    def __init__(self, *args, **kwargs):
        Table.__init__(self, *args, **kwargs)
        ContentDisplayMixin.__init__(self)
        self.set_member_sortable("element", False)
        self.set_member_sortable("class", False)

    def _row_added(self, index, item, row):
        if self.inline_draft_copies and isinstance(item, Item):
            for draft in item.drafts:
                draft_row = self.create_row(index, draft)
                self.body.append(draft_row)

    def _fill_head(self):
        Table._fill_head(self)
        if self.head_row.children:
            self.head_row.children[-1].add_class("last")

    def create_row(self, index, item):
        
        row = Table.create_row(self, index, item)
        row.add_class("item_row")

        if getattr(item, "is_draft", False):
            row.add_class("draft")

        if getattr(item, "draft_source", None):
            row.add_class("nested_draft")

        return row

    def create_element_display(self, item, member):
        
        display = templates.new("woost.views.ItemLabel")
        display.tag = "label"
        display["for"] = "selection_" + str(item.id)
        display.item = item
        display.referer = self.referer

        if self.inline_draft_copies and item.draft_source:
            display.get_label = lambda: translations(
                "woost.views.ContentTable draft label",
                draft_id = item.draft_id
            )
        
        return display

    def create_class_display(self, item, member):
        return Element(
                    tag = None,
                    children = [translations(item.__class__.name)])

    def add_header_ui(self, header, column, language):
        
        # Add visual cues for sorted columns
        sortable = self.get_member_sortable(column)
        
        if sortable and self.order:
            current_direction = self._sorted_columns.get(
                (column.name, language)
            )
                    
            if current_direction is not None:

                header.add_class("sorted")

                if current_direction is PositiveExpression:
                    header.add_class("ascending")
                    sign = "-"
                elif current_direction is NegativeExpression:
                    header.add_class("descending")

        # Column options
        if sortable or self.get_member_searchable(column):

            menu = header.menu = Element()
            header.append(menu)
            menu.add_class("selector")
            
            label = menu.label = Element()
            label.add_class("label")
            menu.append(label)
            label.append(header.label)

            if column.translated:
                label.append(header.translation_label)
            
            options = header.menu.options = self.create_header_options(
                column,
                language
            )
            menu.append(options)

    def create_header_options(self, column, language):
        
        options = Element()
        options.add_class("selector_content")
        
        if self.get_member_sortable(column):
            sorting_options = self.create_sorting_options(column, language)
            options.append(sorting_options)

            if column.grouping:
                grouping_options = self.create_grouping_options(
                    column,
                    language
                )
                options.append(grouping_options)

        if self.get_member_searchable(column):            
            search_options = self.create_search_options(column, language)
            options.append(search_options)
            
        return options

    def create_sorting_options(self, column, language):

        if self.order:
            direction = self._sorted_columns.get((column.name, language))
        else:
            direction = None

        order_param = column.name
        if language:
            order_param += "." + language

        options = Element()
        options.add_class("sorting_options")

        title = Element("div")
        title.add_class("options_header")
        title.append(translations("woost.views.ContentTable sorting header"))
        options.append(title)

        asc = options.ascending = Element("a")
        asc.add_class("ascending")
        asc["href"] = "?" + view_state(order = order_param, page = 0)
        asc.append(translations("woost.views.ContentTable sort ascending"))
        options.append(asc)

        if direction is PositiveExpression:
            asc.add_class("selected")

        desc = options.ascending = Element("a")
        desc.add_class("descending")
        desc["href"] = "?" + view_state(order = "-" + order_param, page = 0)
        desc.append(translations("woost.views.ContentTable sort descending"))
        options.append(desc)

        if direction is NegativeExpression:
            desc.add_class("selected")

        return options

    def create_search_options(self, column, language):

        filters = [filter.id for filter in self.filters] \
            if self.filters \
            else []

        filter_id = "member-" + column.name
        filters.append(filter_id)

        options = Element()
        options.add_class("search_options")

        title = Element("div")
        title.add_class("options_header")
        title.append(translations("woost.views.ContentTable search header"))
        options.append(title)

        add_filter = Element("a")
        add_filter.add_class("add_filter")
        add_filter["href"] = "?" + view_state(filter = filters, page = 0)
        add_filter.append(
            translations("woost.views.ContentTable add column filter")
        )
        add_filter.set_client_param("filterId", filter_id)
        options.append(add_filter)

        return options

    def create_grouping_options(self, column, language):

        options = Element()
        options.add_class("grouping_options")

        title = Element("div")
        title.add_class("options_header")
        title.append(translations("woost.views.ContentTable grouping header"))
        options.append(title)

        grouping_class = resolve(column.grouping)
        variants = (None,) + grouping_class.variants

        table = Element("table")
        options.append(table)

        for variant in variants:

            tr = Element("tr")
            table.append(tr)                

            td = Element("td")
            td.add_class("variant")
            td.append(grouping_class.translate_grouping_variant(variant))
            tr.append(td)

            for sign in (PositiveExpression, NegativeExpression):
                grouping = grouping_class()
                grouping.member = column
                grouping.language = language
                grouping.sign = sign
                grouping.variant = variant

                td = Element("td")
                td.add_class("sign")
                tr.append(td)

                grouping_link = Element("a")
                grouping_link.add_class("grouping")
                grouping_link["href"] = \
                    "?" + view_state(grouping = grouping.request_value, page = 0)
                grouping_link.append(
                    translations(
                        "cocktail.controllers.grouping.MemberGrouping-"
                        + ("ascending"
                            if sign is PositiveExpression
                            else "descending")
                    )
                )
                td.append(grouping_link)

        return options

