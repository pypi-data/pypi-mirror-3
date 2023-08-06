#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.translations import translations
from cocktail import schema
from cocktail.schema.exceptions import ValidationError
from woost import app
from woost.models import Publishable

def requires_agreement(form, name = "terms", document = None):

    if document is None:
        document = "%s.%s" % (app.package, name)

    if isinstance(document, basestring):
        document = Publishable.require_instance(qname = document)

    if document is None:
        raise ValueError(
            "Must specify a document detailing the end user agreement"
        )

    member = schema.Boolean(
        name = name,
        required = True,
        __translate__ = lambda language, **kwargs:
            schema.Boolean.__translate__(member, language, **kwargs)
            or translations(
                "woost.controllers.formagreement.%s" % member.name,
                member = member
            )
            or translations("woost.controllers.formagreement", member = member)
    )
    member.agreement_document = document
    member.add_validation(_validate_consent)

    form.schema.add_member(member)
    form.adapter.exclude(name)
    return member

def _validate_consent(member, value, ctx):
    if not value:
        yield ConsentNotGivenError(member, value, ctx)


class ConsentNotGivenError(ValidationError):
    """A validation error produced by forms that enforce an agreement to a
    terms and conditions document when the user attempts to submit the form
    without acknowledging the agreement.
    """

