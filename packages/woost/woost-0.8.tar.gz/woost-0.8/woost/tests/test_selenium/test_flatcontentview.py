#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			May 2009
"""
from cocktail.tests.seleniumtester import selenium_test, browser
from woost.models import Item
from woost.tests.test_selenium import admin_login


class FlatContentViewTestCase(object):
    
    @selenium_test
    def test_show_all(self):
        all = len(Item.select())
        browser.open("/en/cms/content/?content_view=flat&page_size=%d" % all)
        admin_login() 
        assert browser.jquery_count(".collection_display tr.item_row") == all

    @selenium_test
    def test_sort_by_id(self):
        
        browser.open(
            "/en/cms/content/?content_view=flat"
            "&page_size=%d"
            "&members=element&members=id"   
            % len(Item.select())
        )
        admin_login()

        def get_browser_ids():
            return browser.get_eval(
                "var ids = [];"
                "window.jQuery('.collection_display tbody td.id_column')"
                ".each(function () {"
                "   ids.push(window.jQuery(this).text());"
                "});"
                "ids.join(' ');"
            )

        # Show the column dropdown panel and click the ascending order button
        browser.click("css=.collection_display th.id_column .selector a.label")
        browser.click(
            "css=.collection_display th.id_column .sorting_options "
            "a.ascending"
        )
        browser.wait_for_page_to_load(10000)
        sorted_ids = " ".join(str(x.id) for x in Item.select(order = "id"))
        assert get_browser_ids() == sorted_ids

        # Show the column dropdown panel and click the descending order button
        browser.click("css=.collection_display th.id_column .selector a.label")
        browser.click(
            "css=.collection_display th.id_column .sorting_options "
            "a.descending"
        )
        browser.wait_for_page_to_load(10000)
        sorted_ids = " ".join(str(x.id) for x in Item.select(order = "-id"))
        assert get_browser_ids() == sorted_ids

    @selenium_test
    def test_selection_tools(self):

        browser.open("/en/cms/content/?content_view")
        admin_login()

        assert browser.is_element_present("css=.select_all")
        assert browser.is_element_present("css=.clear_selection")

        browser.click("css=.select_all")
        all = browser.jquery_count(".collection_display tr.item_row")
        sel = browser.jquery_count(".collection_display tr.item_row.selected")
        assert all == sel

        browser.click("css=.clear_selection")
        sel = browser.jquery_count(".collection_display tr.item_row.selected")
        assert sel == 0

    @selenium_test
    def test_member_selection(self):

        browser.open("/en/cms/content/?content_view")
        admin_login()

        # Unfold the collection settings panel
        browser.click("css=.settings_box a.label")

        all_columns = ["element", "class"] + [
            member.name
            for member in Item.members().itervalues()
            if member.visible
        ]

        for visible_members in (
            set(["element"]),
            set(["element", "class"]),
            set(["element", "class", "id"]),
            set(["id", "author", "owner", "is_draft", "drafts"]),
            set(["element", "translations"])
        ):
            # Check / uncheck columns
            for key in all_columns:
                locator = \
                    "css=.settings_box .members_selector input[value=%s]" % key
                if key in visible_members:
                    browser.check(locator)
                else:
                    browser.uncheck(locator)
            
            # Apply the member selection
            browser.click("css=.settings_box button[type=submit]")
            browser.wait_for_page_to_load(10000)

            # Assert the browser shows the required columns
            for key in all_columns:
                check_locator = \
                    "css=.settings_box .members_selector input[value=%s]" % key
                column_locator = \
                    "css=.collection_display th.%s_column" % key
                if key in visible_members:
                    assert browser.is_checked(check_locator)
                    assert browser.is_visible(column_locator)
                else:
                    assert not browser.is_checked(check_locator)
                    assert not browser.is_element_present(column_locator)

    @selenium_test
    def test_simple_search(self):

        browser.open("/en/cms/content/?content_view")
        admin_login()

        # Fill in and submit the simple search box
        query = "administrators"
        browser.type("filter_value0", query)
        browser.click("css=.search_button")
        browser.wait_for_page_to_load(10000)

        # Make sure this turns on the advanced search panel
        assert not browser.is_element_present("css=.advanced_search")
        assert browser.is_element_present("css=.filters")
        assert browser.is_element_present("filter_value0")
        assert browser.get_value("filter_value0") == query

        # Test returned results
        assert browser.jquery_count(".collection_display tr.item_row") == 1

    @selenium_test
    def test_simple_search_without_query(self):

        browser.open("/en/cms/content/?content_view")
        admin_login()

        # Perform a search without query
        browser.click("css=.search_button")
        browser.wait_for_page_to_load(10000)

        # Make sure this doesn't turn on the advanced search panel
        assert browser.is_element_present("css=.advanced_search")

