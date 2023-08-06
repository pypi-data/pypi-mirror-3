#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import cherrypy
from webconsole import WebConsoleController
from cocktail.events import event_handler
from cocktail.iteration import first, last
from cocktail.translations import translations, get_language
from cocktail.persistence import PersistentObject
from cocktail.controllers import request_property
from woost.controllers.documentcontroller import DocumentController
from woost.models import Site, get_current_user
from woost.extensions.webconsole.webconsolepermission \
    import WebConsolePermission


class CMSWebConsole(DocumentController, WebConsoleController):

    @event_handler
    def handle_traversed(self, event):
        get_current_user().require_permission(WebConsolePermission)

    submit = WebConsoleController.submit
    submitted = WebConsoleController.submitted

    @request_property
    def session(self):

        session = WebConsoleController.session(self)

        session.context.update(
            site = Site.main,
            user = get_current_user(),
            language = get_language(),
            translations = translations,
            first = first,
            last = last
        )

        for model in PersistentObject.schema_tree():
            session.context[model.name] = model

        return session

