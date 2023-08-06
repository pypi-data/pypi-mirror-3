#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2009
"""
from __future__ import with_statement
from contextlib import contextmanager
from cocktail.translations import translations
from cocktail.tests.seleniumtester import selenium_test, browser
from woost.models import Item
from woost.tests.test_selenium import admin_login

@contextmanager
def override(obj, **kwargs):

    undefined = object()

    prev_values = {}
    
    try:
        for key, value in kwargs.iteritems():
            prev_values[key] = getattr(obj, key, undefined)
            setattr(obj, key, value)
    
        yield

    finally:
        for key, value in prev_values.iteritems():
            if value is undefined:
                delattr(obj, key)
            else:
                setattr(obj, key, value)


class SearchTestCase(object):
    
    @selenium_test
    def test_unfold_expanded_search(self):
        browser.open("/en/cms/content/?content_view=flat")
        admin_login()
        browser.click("css=.advanced_search")
        browser.wait_for_page_to_load(10000)
        assert browser.is_element_present("css=.filters")
        assert browser.is_element_present("css=.filters .new_filter_selector")

    @selenium_test
    def test_add_filters_from_selector(self):
        
        from cocktail.schema.expressions import Self
        from cocktail.persistence import Query
        
        results = Item.select([
            Item.id.greater(15),
            Self.search("@localhost", languages = ["en"])
        ])
        results_count = len(results)

        browser.open(
            "/en/cms/content/?content_view=flat&search_expanded=true"
            "&page_size=%d" % (results_count + 1)
        )
        admin_login()

        # Add filters
        for i, filter_id in enumerate(("member-id", "global_search")):
            browser.fire_event("css=.new_filter_selector", "click")
            browser.fire_event("css=.new_filter-%s" % filter_id, "click")

        assert browser.jquery_count(".filters .filter_list .filter_entry") == 2

        # Set values on filters
        browser.type("filter_operator0", "gt")
        browser.type("filter_value0", "15")
        browser.type("filter_value1", "@localhost")
        browser.click("css=.filters .search_button")
        browser.wait_for_page_to_load(10000)

        # Test the returned content
        rows_count = browser.jquery_count(".collection_display .item_row")
        assert rows_count == results_count

        # Supplied values must be preserved between page loads
        assert browser.get_selected_value("filter_operator0") == "gt"
        assert browser.get_value("filter_value0") == "15"
        assert browser.get_value("filter_value1") == "@localhost"

    @selenium_test
    def test_multiple_options(self):

        from woost.models import User, Role
        from cocktail.controllers.userfilter import MultipleChoiceFilter

        administrators = Role.require_instance(
            qname = "woost.administrators"
        )

        anonymous = Role.require_instance(
            qname = "woost.anonymous"
        )

        with override(User.roles, user_filter = MultipleChoiceFilter):           
            
            browser.open("/en/cms/content/?content_view=flat&type=woost.models.user.User&search_expanded=true")
            admin_login()

            # Select the filter
            browser.fire_event("css=.new_filter_selector", "click")
            browser.fire_event("css=.new_filter-member-roles", "click")
            
            # Select options
            browser.fire_event("css=.filters .values_field .select", "click")
            assert browser.is_visible("css=.modal_selector_dialog")

            for role in (administrators, anonymous):
                browser.click(
                    "css=.modal_selector_dialog input[value=%d]"
                    % role.id
                )
    
            browser.fire_event("css=.modal_selector_dialog .accept", "click")                
            
            for role in (administrators, anonymous):
                assert browser.is_element_present(
                    "css=.filters .values_field input[value=%d]"
                    % role.id
                )

            browser.click("css=.filters .search_button")
            browser.wait_for_page_to_load(10000)
            
            # Validate results
            results_count = len(administrators.users) + len(anonymous.users)
            rows_count = browser.jquery_count(".collection_display .item_row")
            assert rows_count == results_count

            # Make sure the search control preserves its state
            for role in (administrators, anonymous):
                assert browser.is_element_present(
                    "css=.filters .values_field input[value=%d]"
                    % role.id
                )

            browser.fire_event("css=.filters .values_field .select", "click")

            for role in (administrators, anonymous):
                assert browser.is_checked(
                    "css=.modal_selector_dialog input[value=%d]"
                    % role.id
                )            

    @selenium_test
    def test_item_selector(self):

        from woost.models import Publishable, Template
        template = list(Template.select())[0]
        
        browser.open("/en/cms/content/?content_view=flat&type=woost.models.publishable.Publishable&search_expanded=true")
        admin_login()

        browser.fire_event("css=.new_filter_selector", "click")
        browser.fire_event("css=.new_filter-member-template", "click")
        assert not browser.is_element_present("css=.filters .value_field .new")
        assert not browser.is_element_present("css=.filters .value_field .edit")
        assert not browser.is_element_present("css=.filters .value_field .delete")
        assert not browser.is_element_present("css=.filters .value_field .unlink")
        browser.click("css=.filters .value_field .select")

        browser.select_frame("dom=selenium.browserbot.getCurrentWindow().frames[0]")
        browser.wait_for_element_present("css=.collection_display", 10000)
        assert not browser.is_element_present("css=.new_action")
        browser.click("css=.collection_display #%d" % template.id)
        browser.click("css=.select_action")

        browser.select_frame("relative=parent")
        browser.wait_for_element_present("css=.collection_display", 10000)

        assert translations(template, "en") \
            in browser.jquery_html(".filters .value_field")

        assert browser.get_value("filter_value0") == str(template.id)

        browser.click("css=.filters .search_button")
        browser.wait_for_page_to_load(10000)
        
        rows_count = browser.jquery_count(".collection_display .item_row")
        assert rows_count == len(template.items)

