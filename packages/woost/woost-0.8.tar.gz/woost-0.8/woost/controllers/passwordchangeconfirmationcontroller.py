#-*- coding: utf-8 -*-
u"""Defines the `PasswordChangeConfirmationController` class.

.. moduleauthor:: Javier Marrero <javier.marrero@whads.com>
"""
import cherrypy
from cocktail import schema
from cocktail.events import event_handler
from cocktail.persistence import datastore
from cocktail.controllers import (
    request_property,
    get_parameter,
    FormProcessor,
    Form
)
from woost.models.user import User
from woost.controllers.backoffice.usereditnode import PasswordConfirmationError
from woost.controllers.documentcontroller import DocumentController
from woost.controllers.passwordchangecontroller import generate_confirmation_hash


class PasswordChangeConfirmationController(FormProcessor, DocumentController):

    is_transactional = True
    class_view = "woost.views.PasswordChangeFormTemplate"

    @event_handler
    def handle_traversed(cls, e):
        
        controller = e.source

        # Make sure we are given a user
        if controller.user is None:
            raise cherrypy.HTTPError(400, "Invalid user")

        # Verify the request using the provided hash
        provided_hash = controller.hash
        expected_hash = generate_confirmation_hash(controller.identifier)

        if provided_hash != expected_hash:
            raise cherrypy.HTTPError(400, "Invalid hash")

    @request_property
    def identifier_member(self):
        cms = self.context["cms"]
        return cms.authentication.identifier_field

    @request_property
    def identifier(self):        
        member = self.identifier_member.copy()
        member.name = "user"
        return get_parameter(member, errors = "ignore")

    @request_property
    def hash(self):
        return get_parameter(schema.String("hash"))

    @request_property
    def user(self):
        if self.identifier:
            return User.get_instance(**{
                self.identifier_member.name: self.identifier
            })
    
    class ChangePasswordForm(Form):

        @request_property
        def schema(self):

            form_schema = schema.Schema("PasswordChangeConfirmationForm")

            # New password
            password_member = User.password.copy()
            password_member.required = True
            form_schema.add_member(password_member)

            # New password confirmation
            password_confirmation_member = schema.String(
                name = "password_confirmation",
                edit_control = "cocktail.html.PasswordBox",
                required = True
            )
            
            @password_confirmation_member.add_validation
            def validate_password_confirmation(member, value, ctx):
                password = ctx.get_value("password")
                password_confirmation = value

                if password and password_confirmation \
                and password != password_confirmation:
                    yield PasswordConfirmationError(member, value, ctx)

            form_schema.add_member(password_confirmation_member)

            return form_schema

        def submit(self):

            Form.submit(self)
            
            # Update the user's password
            user = self.controller.user
            user.password = self.data["password"]
            datastore.commit()

            # Log in the user (after all, we just made certain it's him/her)
            self.controller.context["cms"].authentication.set_user_session(user)

    @request_property
    def output(self):
        output = DocumentController.output(self)
        output["identifier"] = self.identifier
        output["hash"] = self.hash
        return output

