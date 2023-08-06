#-*- coding: utf-8 -*-
"""

@author:		Javier Marrero
@contact:		javier.marrero@whads.com
@organization:	Whads/Accent SL
@since:			November 2009
"""
from cocktail import schema
from cocktail.persistence import datastore
from cocktail.translations import translations
from cocktail.tests.seleniumtester import selenium_test, browser
from woost.models import Item, Publishable, Template
from woost.tests.test_selenium import admin_login


class EditTestModel(Item):

    description = schema.String(
        required = True
    )
    
    part = schema.Reference(
        bidirectional = True,    
        integral = True
    )

    container = schema.Reference(
        bidirectional = True
    )

EditTestModel.part.type = EditTestModel
EditTestModel.container.type = EditTestModel


class ItemSelectorTestCase(object):
    
    @selenium_test
    def test_select(self):

        template = list(Template.select())[0]

        browser.open("/en/cms/content/new/?item_type=woost.models.publishable.Publishable")
        admin_login()
        
        assert not browser.is_element_present(
            "css=.template_field .control .new"
        )

        assert not browser.is_element_present(
            "css=.template_field .control .unlink"
        )

        assert not browser.is_element_present(
            "css=.template_field .control .delete"
        )

        browser.click("css=.template_field .control .select")
        browser.wait_for_page_to_load(10000)
        
        assert browser.is_visible("css=.collection_display #%d" % template.id)
        browser.click("css=.collection_display #%d" % template.id)
        browser.click("css=.ContentView .select_action")
        browser.wait_for_page_to_load(10000)

        assert translations(template, "en") \
            in browser.jquery_html(".template_field .control")

        assert browser.get_value("edited_item_template") == str(template.id)

    @selenium_test
    def test_unlink(self):

        template = list(Template.select())[0]

        publishable = Publishable()
        publishable.set("enabled", True, "en")
        publishable.template = template
        publishable.insert()
        datastore.commit()

        browser.open("/en/cms/content/%d/fields" % publishable.id)
        admin_login()

        assert not browser.is_element_present(
            "css=.template_field .control .new"
        )

        assert not browser.is_element_present(
            "css=.template_field .control .delete"
        )

        browser.click("css=.template_field .control .unlink")
        browser.wait_for_page_to_load(10000)

        val = browser.get_value("edited_item_template")

        assert not browser.get_value("edited_item_template")


class IntegralSelectorTestCase(object):

    @selenium_test
    def test_new(self):
    
        browser.open(
            "/en/cms/content/new/"
            "?item_type=woost.tests.test_selenium.test_edit.EditTestModel"
        )
        admin_login()

        assert not browser.is_element_present("css=.part_field .control .select")
        assert not browser.is_element_present("css=.part_field .control .edit")
        assert not browser.is_element_present("css=.part_field .control .delete")
        assert not browser.is_element_present("css=.part_field .control .unlink")
        
        browser.click("css=.part_field .control .new")
        browser.wait_for_page_to_load(10000)
        
        browser.type("edited_item_description", "Foo")
        browser.click("css=.save_action")
        browser.wait_for_page_to_load(10000)

        datastore.sync()
        part_id = int(browser.get_value("edited_item_part"))
        assert EditTestModel.require_instance(part_id).description == "Foo"

    @selenium_test
    def test_edit(self):

        datastore.sync()
        container = EditTestModel()
        container.description = "test_edit container"
        
        part = EditTestModel()
        part.description = "test_edit part"
        container.part = part
        
        container.insert()
        datastore.commit()
        
        browser.open("/en/cms/content/%d/fields" % container.id)
        admin_login()

        assert not browser.is_element_present("css=.part_field .control .select")
        assert not browser.is_element_present("css=.part_field .control .new")
        assert not browser.is_element_present("css=.part_field .control .unlink")
        assert browser.get_value("edited_item_part") == str(part.id)

        browser.click("css=.part_field .control .edit")
        browser.wait_for_page_to_load(10000)

        browser.type("edited_item_description", "modified test_edit part")
        browser.click("css=.save_action")
        browser.wait_for_page_to_load(10000)

        browser.click("css=.cancel_action")
        browser.wait_for_page_to_load(10000)

        datastore.sync()
        assert browser.get_value("edited_item_part") == str(part.id)
        assert part.description == "modified test_edit part"
        
    @selenium_test
    def test_delete(self):
        
        datastore.sync()
        container = EditTestModel()
        container.description = "test_edit container"
        
        part = EditTestModel()
        part.description = "test_edit part"
        container.part = part
        
        container.insert()
        datastore.commit()

        browser.open("/en/cms/content/%d/fields" % container.id)
        admin_login()

        assert not browser.is_element_present("css=.part_field .control .select")
        assert not browser.is_element_present("css=.part_field .control .new")
        assert not browser.is_element_present("css=.part_field .control .unlink")

        location = browser.get_location()
        browser.click("css=.part_field .control .delete")
        browser.wait_for_page_to_load(10000)
        assert browser.get_location() == location
        assert not browser.get_value("edited_item_part")

        datastore.sync()
        assert EditTestModel.get_instance(part.id) is part

        browser.click("css=.save_action")
        browser.wait_for_page_to_load(10000)
        datastore.sync()
        assert EditTestModel.get_instance(part.id) is None

