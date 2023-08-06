#-*- coding: utf-8 -*-
u"""Defines the `LoginController` class.

.. moduleauthor:: Javier Marrero <javier.marrero@whads.com>
"""
import cherrypy
from cocktail import schema
from cocktail.modeling import cached_getter
from cocktail.events import Event, event_handler
from cocktail.schema.exceptions import ValidationError
from cocktail.controllers.parameters import get_parameter
from cocktail.controllers.formcontrollermixin import FormControllerMixin
from woost.models import (
    User,
    AuthorizationError,
    get_current_user
)
from woost.controllers.documentcontroller import DocumentController
from woost.controllers.authentication import AuthenticationFailedError


class LoginController(FormControllerMixin, DocumentController):
    
    def __init__(self, *args, **kwargs):
        DocumentController.__init__(self, *args, **kwargs)
        FormControllerMixin.__init__(self)

    @cached_getter
    def form_errors(self):
        form_errors = FormControllerMixin.form_errors(self)
        
        if not form_errors and self.submitted and get_current_user().anonymous:
            user_param = get_parameter(schema.Member("user"))
            form_errors._items.append(AuthenticationFailedError(user_param))

        return form_errors

    @cached_getter
    def submitted(self):
        return cherrypy.request.method == "POST" and \
            get_parameter(schema.Member("authenticate"))

    @cached_getter
    def form_model(self):

        identifier = self.context["cms"].authentication.identifier_field.copy()
        identifier.name = "user"

        form_model = schema.Schema("woost.controllers.logincontroller.form",
            members = [
                identifier,
                User.password.copy()
            ]
        )

        return form_model

