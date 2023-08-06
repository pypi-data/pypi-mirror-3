#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import cherrypy
from cocktail.modeling import cached_getter
from cocktail import schema
from cocktail.persistence import datastore
from cocktail.controllers import FormProcessor
from woost.models import (
    changeset_context,
    get_current_user,
    ReadMemberPermission,
    ModifyMemberPermission,
    Publishable,
    Document,
    Controller,
    Template,
    EmailTemplate
)
from woost.controllers.uploadform import UploadForm
from woost.controllers.documentcontroller import DocumentController


class UserForm(Document):

    groups_order = list(Document.groups_order)
    groups_order.insert(groups_order.index("content") + 1, "form")

    members_order = [
        "form_model",
        "excluded_members",
        "should_save_instances",
        "redirection",
        "email_notifications"
    ]

    default_controller = schema.DynamicDefault(
        lambda: Controller.get_instance(
            qname = "woost.extensions.usermodels.user_form_controller"
        )
    )

    default_template = schema.DynamicDefault(
        lambda: Template.get_instance(
            qname = "woost.extensions.usermodels.user_form_template"
        )
    )

    form_model = schema.Reference(
        required = True,
        class_family = "woost.models.Item",
        member_group = "form"
    )

    excluded_members = schema.Collection(
        items = schema.String(),
        edit_control = "cocktail.html.TextArea",
        member_group = "form"
    )

    should_save_instances = schema.Boolean(
        required = True,
        default = True,
        member_group = "form"
    )

    redirection = schema.Reference(
        type = Publishable,
        related_end = schema.Collection(),
        member_group = "form"
    )

    email_notifications = schema.Collection(
        items = schema.Reference(type = EmailTemplate),
        related_end = schema.Collection(),
        member_group = "form"
    )


class UserFormController(FormProcessor, DocumentController):

    class UserForm(UploadForm):

        @cached_getter
        def model(self):
            return self.controller.context["publishable"].form_model

        @cached_getter
        def adapter(self):
            adapter = UploadForm.adapter(self)
            document = self.controller.context["publishable"]
            user = get_current_user()

            excluded_members = []

            for member in self.model.members().itervalues():
                if (
                    not member.visible
                    or not member.editable
                    or member.member_group == "administration"
                    or not user.has_permission(
                        ReadMemberPermission,
                        member = member
                    )
                    or not user.has_permission(
                        ModifyMemberPermission,                     
                        member = member
                    )
                ):
                    excluded_members.append(member.name)

            if document.excluded_members:
                excluded_members.extend(document.excluded_members)
            
            if excluded_members:
                adapter.exclude(excluded_members)

            return adapter

        def submit(self):
            document = self.controller.context["publishable"]

            # Write to the database
            if document.should_save_instances:
                with changeset_context(get_current_user()):
                    UploadForm.submit(self)
                    self.instance.insert()
                datastore.commit()
            
            # Do not write to the database, only process form data
            else:
                UploadForm.submit(self)

            # Send email messages based on the submitted data
            for email_template in document.email_notifications:
                email_template.send({
                    "form": document,
                    "instance": self.instance
                })

            # Redirect the user to a confirmation page
            if document.redirection:
                raise cherrypy.HTTPRedirect(
                    self.controller.context["cms"].uri(
                        document.redirection,
                        form = document.id,
                        instance = None 
                                   if not document.should_save_instances 
                                   else self.instance.id
                    )
                )

