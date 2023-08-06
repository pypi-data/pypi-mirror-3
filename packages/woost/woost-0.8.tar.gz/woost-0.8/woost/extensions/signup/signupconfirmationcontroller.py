#-*- coding: utf-8 -*-
"""

@author:		Javier Marrero
@contact:		javier.marrero@whads.com
@organization:	Whads/Accent SL
@since:			January 2010
"""
import hashlib
from cocktail import schema
from cocktail.persistence import datastore
from cocktail.modeling import cached_getter
from woost.models import User
from woost.controllers.documentcontroller import DocumentController
from woost.extensions.signup import SignUpExtension

def generate_confirmation_hash(email):
    hash = hashlib.sha1()
    hash.update(email)
    hash.update(SignUpExtension.instance.secret_key)
    return hash.hexdigest()

class SignUpConfirmationController(DocumentController):

    autologin = True
    confirmed = False

    def __init__(self, *args, **kwargs):
        self.email = self.params.read(schema.String("email"))
        self.hash = self.params.read(schema.String("hash"))

    def submit(self):

        if self.email or self.hash:
            # Checking hash code
            if generate_confirmation_hash(self.email) == self.hash:
                instance = User.get_instance(email=self.email)
                if instance:
                    # Confirming and enabling user instance
                    instance.set("confirmed_email", True)
                    instance.set("enabled", True)
                    self.confirmed = True
                    datastore.commit()

                    # Autologin after confirmation
                    if self.autologin:
                        self.context["cms"].authentication.set_user_session(instance)
    
    @cached_getter
    def output(self):
        output = DocumentController.output(self)
        output.update(
            confirmed = self.confirmed
        )

        return output
