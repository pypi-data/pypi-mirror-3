#-*- coding: utf-8 -*-
"""

@author:		Javier Marrero
@contact:		javier.marrero@whads.com
@organization:	Whads/Accent SL
@since:			January 2010
"""
import cherrypy
from cocktail import schema
from cocktail.persistence import datastore
from cocktail.modeling import cached_getter
from cocktail.controllers.location import Location
from cocktail.controllers.formcontrollermixin import FormControllerMixin
from woost.controllers.documentcontroller import DocumentController
from woost.controllers.backoffice.usereditnode import PasswordConfirmationError
from woost.extensions.signup.signupconfirmationcontroller import generate_confirmation_hash
from woost.extensions.signup.signuppage import SignUpPage

from woost.models import Item, Site, Language, User

class SignUpController(FormControllerMixin, DocumentController):

    def __init__(self, *args, **kwargs):
        DocumentController.__init__(self, *args, **kwargs)
        FormControllerMixin.__init__(self)

    @cached_getter
    def form_model(self):
        return self.context["publishable"].user_type

    @cached_getter
    def form_adapter(self):

        adapter = FormControllerMixin.form_adapter(self)
        adapter.exclude(
            ["prefered_language",
             "roles",
             "password_confirmation",
             "enabled",
             "confirmed_email"]
            + [key for key in Item.members()]    
        )
        return adapter

    @cached_getter
    def form_schema(self):

        form_schema = FormControllerMixin.form_schema(self)

        # Set schema name in order to keep always the same value
        # although change value of form_model member
        form_schema.name = u"SignUpForm"

        # Adding extra field for password confirmation
        if form_schema.get_member("password"):

            password_confirmation_member = schema.String(
                name = "password_confirmation",
                edit_control = "cocktail.html.PasswordBox",
                required = form_schema.get_member("password")
            )
            form_schema.add_member(password_confirmation_member)

            # Set password_confirmation position just after
            # password member position
            order_list = form_schema.members_order
            pos = order_list.index("password")
            order_list.insert(pos + 1, "password_confirmation")

            # Add validation to compare password_confirmation and
            # password fields
            @password_confirmation_member.add_validation
            def validate_password_confirmation(member, value, ctx):
                password = ctx.get_value("password")
                password_confirmation = value

                if password and password_confirmation \
                and password != password_confirmation:
                    yield PasswordConfirmationError(
                            member, value, ctx)

        return form_schema

    def submit(self):
        FormControllerMixin.submit(self)
        publishable = self.context["publishable"]

        # Adding roles
        instance = self.form_instance
        instance.roles.extend(publishable.roles)

        # If require email confirmation, disabled authenticated access
        # and send email confirmation message
        confirmation_email_template = publishable.confirmation_email_template
        if confirmation_email_template:
            instance.enabled = False
            instance.confirmed_email = False
            confirmation_email_template.send({
                "user": instance,
                "confirmation_url": self.confirmation_url
            })
            # Storing instance
            instance.insert()
            datastore.commit()
        else:
            # Storing instance
            instance.insert()
            datastore.commit()
            # Getting confirmation target uri
            confirmation_target = self.context["publishable"].confirmation_target
            uri = self.context["cms"].uri(confirmation_target)
            # Enabling user and autologin
            instance.enabled = True
            self.context["cms"].authentication.set_user_session(instance)
            # Redirecting to confirmation target
            raise cherrypy.HTTPRedirect(uri)

    @cached_getter
    def confirmation_url(self): 
        instance = self.form_instance
        confirmation_target = self.context["publishable"].confirmation_target
        canonical_uri = self.context["cms"].uri(confirmation_target)
        location = Location.get_current(relative=False)
        location.path_info = canonical_uri
        location.query_string = {
            "email": instance.email,
            "hash": generate_confirmation_hash(instance.email)
        }
        return str(location)
