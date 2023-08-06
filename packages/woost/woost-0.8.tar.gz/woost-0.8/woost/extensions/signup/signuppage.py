#-*- coding: utf-8 -*-
"""

@author:		Javier Marrero
@contact:		javier.marrero@whads.com
@organization:	Whads/Accent SL
@since:			January 2010
"""
from cocktail import schema
from woost.models import (
    Controller,
    Document,
    EmailTemplate,
    Publishable,
    Role,
    Template,
    User
)

def excluded_roles():
    return Role.qname.not_one_of((
        'woost.anonymous',
        'woost.everybody',
        'woost.authenticated'
    ))

class SignUpPage(Document):

    members_order = [
        "user_type",
        "roles",
        "confirmation_target",
        "confirmation_email_template"
    ]

    # Defines the persistent class that will be
    # used like schema in signup process
    user_type = schema.Reference(
        class_family = User,
        required = True,
        member_group = "signup_process"
    )

    # The collection of roles that will be applyed
    # to each instance (of user_type class) created throw
    # a signuppage
    roles = schema.Collection(
        items = "woost.models.Role",
        related_end = schema.Collection(
            name = "related_signup_pages",
            visible = False
        ),
        edit_inline = True,
        member_group = "signup_process",
        relation_constraints = lambda ctx: [excluded_roles()]
    )

    # If is None, doesn't require an email confirmation
    # process to complete signup process
    confirmation_email_template = schema.Reference(
        type = EmailTemplate,
        related_end = schema.Collection(),
        member_group = "signup_process"
    )

    confirmation_target = schema.Reference(
        type = "woost.models.Publishable",
        related_end = schema.Collection(),
        member_group = "signup_process",
        required = True
    )

    default_template = schema.DynamicDefault(
        lambda: Template.get_instance(qname = u"woost.extensions.signup.signup_template")
    )

    default_controller = schema.DynamicDefault(
        lambda: Controller.get_instance(qname = u"woost.extensions.signup.signup_controller")
    )

    default_confirmation_email_template = schema.DynamicDefault(
        lambda: EmailTemplate.get_instance(qname = u"woost.extensions.signup.signup_confirmation_email_template")
    )

    default_confirmation_target = schema.DynamicDefault(
        lambda: Publishable.get_instance(qname = u"woost.extensions.signup.signup_confirmation_target")
    )
