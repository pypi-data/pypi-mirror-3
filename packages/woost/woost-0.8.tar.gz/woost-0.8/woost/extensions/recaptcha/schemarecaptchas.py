#-*- coding: utf-8 -*-
u"""
Provides a member that handles reCAPTCHA values.

@author:		Jordi Fernández
@contact:		jordi.fernandez@whads.com
@organization:	Whads/Accent SL
@since:			December 2009
"""
import urllib
import urllib2
import cherrypy
from cocktail.schema.schema import Schema
from cocktail.schema.schemastrings import String
from cocktail.schema.accessors import get_accessor
from cocktail.schema.exceptions import ValidationError
from woost.extensions.recaptcha import ReCaptchaExtension


class ReCaptcha(Schema):
    """A member that handles reCAPTCHA values.
    """

    VERIFY_SERVER = "api-verify.recaptcha.net"

    def __init__(self, *args, **kwargs):
        Schema.__init__(self, *args, **kwargs)

        def read_challenge(reader):
            return reader.source("recaptcha_challenge_field")

        def read_response(reader):
            return reader.source("recaptcha_response_field")

        self.add_member(String(
            "challenge", 
            read_request_value = read_challenge
        ))
        self.add_member(String(
            "response", 
            read_request_value = read_response
        ))
        self.add_validation(ReCaptcha.captcha_validation_rule)

        self.edit_control = "woost.extensions.recaptcha.ReCaptchaBox"

    def captcha_validation_rule(self, validable, context):
        """Validation rule for reCaptcha. Applies the validation rules defined 
        by all members in the schema, propagating their errors. Checks that the 
        L{response} member is valid for the L{challenge} and the L{public_key} 
        constraint.
        """

        accessor = self.accessor \
            or context.get("accessor", None) \
            or get_accessor(validable)

        challenge = accessor.get(validable, "challenge", default = None)
        response = accessor.get(validable, "response", default = None)

        if challenge and response:

            def encode_if_necessary(s):
                if isinstance(s, unicode):
                    return s.encode('utf-8')
                return s
            
            private_key = ReCaptchaExtension.instance.private_key
            remote_ip = cherrypy.request.remote.ip

            params = urllib.urlencode({
                'privatekey': encode_if_necessary(private_key),
                'remoteip': encode_if_necessary(remote_ip),
                'challenge': encode_if_necessary(challenge),
                'response': encode_if_necessary(response),
            })

            request = urllib2.Request(
                url = "http://%s/verify" % self.VERIFY_SERVER,
                data = params,
                headers = {
                    "Content-type": "application/x-www-form-urlencoded",
                    "User-agent": "Woost reCAPTCHA extension"
                }
            )
            
            httpresp = urllib2.urlopen(request)

            return_values = httpresp.read().splitlines();
            httpresp.close();

            return_code = return_values[0]

            if (return_code != "true"):
                yield ReCaptchaValidationError(self, response, context)

        else:
            yield ReCaptchaValidationError(self, response, context)

    def _create_default_instance(self):
        return None


class ReCaptchaValidationError(ValidationError):
    """A validation error produced when the user fails a ReCaptcha
    validation.
    """

