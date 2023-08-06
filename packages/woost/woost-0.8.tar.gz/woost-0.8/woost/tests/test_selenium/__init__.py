#-*- coding: utf-8 -*-
"""
Selenium test suite for the Woost CMS.

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			May 2009
"""
from os.path import join        
from shutil import rmtree
from tempfile import mkdtemp
from ZODB.FileStorage import FileStorage
import cherrypy
from cocktail.persistence import datastore
from cocktail.tests.seleniumtester import (
    get_selenium_enabled,
    get_selenium_site_address,
    browser
)
from woost import app
from woost.models.initialization import init_site
from woost.controllers.cmscontroller import CMSController

# Site defaults
admin_email = "admin@localhost"
admin_password = "topsecret"
site_languages = ("en",)

# Path for site temporary files
_site_temp_path = None

def login(user, password):
    browser.type("user", user)
    browser.type("password", password)
    browser.click("authenticate")
    browser.wait_for_page_to_load(10000)

def admin_login():
    login(admin_email, admin_password)


def setup_package():
    
    if not get_selenium_enabled():
        return

    # Create a temporary folder to hold site files
    _site_temp_path= mkdtemp()
    app.root = _site_temp_path

    # Set up a temporary database
    datastore.storage = FileStorage(app.path("testdb.fs"))

    # Initialize site content before testing
    init_site(
        admin_email,
        admin_password,
        site_languages
    )
    datastore.commit()

    # Configure the site's webserver
    hostname, port = get_selenium_site_address()
    cherrypy.config.update({
        "log.screen": False,
        "server.socket_host": hostname,
        "server.socket_port": port,
        "engine.autoreload.on": False
    })

    # Configure the application
    cms = CMSController()
    cms.closing_item_requires_confirmation = False

    # Launch the site's webserver on another thread
    cms.run(block = False)

def teardown_package():

    if not get_selenium_enabled():
        return

    # Stop the site's webserver
    cherrypy.server.stop()
    cherrypy.engine.exit()

    # Remove temporary site files:
    # This will often fail on Windows, probably because we try to delete a
    # running executable, so delay & retry a limited number of times, to give
    # any running process a chance to end.
    for i in range(5):
        try:
            rmtree(_site_temp_path)
        except Exception:
            from time import sleep
            sleep(1)
        else:
            break

