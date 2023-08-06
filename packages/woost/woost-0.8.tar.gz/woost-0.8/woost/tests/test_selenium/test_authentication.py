#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			May 2009
"""
from cocktail.tests.seleniumtester import selenium_test, browser
from woost.tests.test_selenium import (
    admin_email,
    admin_password
)


class AuthenticationTestCase(object):

    def assert_login_form_visible(self):
        assert browser.is_text_present("User")
        assert browser.is_text_present("Password")
        assert browser.is_element_present("xpath=//input[@name='user']")
        assert browser.is_element_present(
            "xpath=//input[@name='password' and @type='password']"
        )

    def login(self, user_name = "", password = ""):
        browser.type("user", user_name)
        browser.type("password", password)
        browser.click("authenticate")
        browser.wait_for_page_to_load(10000)

    @selenium_test
    def test_unauthorized_access_shows_login_form(self):
        browser.open("/en/cms")
        self.assert_login_form_visible()
    
    @selenium_test
    def test_wrong_login_attempt_fails(self):
        browser.open("/en/cms")

        self.login()
        self.assert_login_form_visible()

        self.login(admin_email + "asdk23h4")
        self.assert_login_form_visible()

        self.login(admin_email)
        self.assert_login_form_visible()

        self.login(admin_email, admin_password + "kn324n1")
        self.assert_login_form_visible()

    @selenium_test
    def test_valid_login_attempt_succeeds(self):
        browser.open("/en/cms")
        self.login(admin_email, admin_password)
        assert browser.is_text_present(admin_email)
        assert browser.is_element_present("css=.logout_button")
    
    @selenium_test
    def test_logout(self):
        browser.open("/en/cms")
        self.login(admin_email, admin_password)
        browser.click("css=.logout_button")
        browser.wait_for_page_to_load(5000)
        self.assert_login_form_visible()

