#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Jordi Fernández <jordi.fernandez@whads.com>
"""
import logging
import smtplib
from email.mime.text import MIMEText
from email.Header import Header
from email.Utils import formatdate
from cocktail import schema
from cocktail.asynctask import TaskManager
from cocktail.modeling import cached_getter, getter
from cocktail.controllers import context
from cocktail.translations import translations, set_language
from cocktail.persistence import datastore
from cocktail.schema.exceptions import ValidationError
from woost.models import (
    Site, Item, Role, Language, get_current_user, set_current_user
)
from woost.extensions.mailer.sendemailpermission import SendEmailPermission


logger = logging.getLogger("woost.extensions.mailer")
tasks = TaskManager()

MAILING_STARTED = 1
MAILING_FINISHED = 2

class RunningMailingError(Exception):
    """An exception raised when trying to delete a running mailing"""


class DocumentTemplateRequiredError(ValidationError):

    def __str__(self):
        return "%s (Document must have a template)" \
                % ValidationError.__str__(self)

class LanguageValueError(ValidationError):

    def __str__(self):
        return "%s (Language isn't one of the document languages)" \
                % ValidationError.__str__(self)

class PerUserCustomizableValueError(ValidationError):

    def __str__(self):
        return "%s (Document template isn't per user customizable)" \
            % ValidationError.__str__(self)


def available_roles(ctx):
    user = get_current_user()
    return [role 
            for role in Role.select() 
            if not role.implicit
            and user.has_permission(SendEmailPermission, role = role) 
            and len(get_receivers_by_roles([role]))]


class Mailing(Item):

    emails_per_transaction = 10
    __cached_body = None

    # Members
    #------------------------------------------------------------------------------
    members_order = (
        "sender", "subject", "document", "language", "per_user_customizable", "roles"
    )
    groups_order = "content", "administration"

    document = schema.Reference(
        required = True,
        type = "woost.models.document.Document",
        related_end = schema.Collection(),
        member_group = "content"
    )

    sender = schema.String(
        required = True,
        format = r"([\w\-\.]+@(\w[\w\-]+\.)+[\w\-]+)",
        member_group = "content"
    )

    subject = schema.String(
        required = True,
        member_group = "content"
    )

    language = schema.Reference(
        type = "woost.models.Language",
        required = True,
        edit_control = "cocktail.html.RadioSelector",
        member_group = "content"
    )

    roles = schema.Collection(
        "roles",
        items = schema.Reference(
            type = "woost.models.Role",
            default_order = "title",
            enumeration = available_roles,
            translate_value = lambda value, language = None, **kwargs: \
                "%s (%d %s)" % (
                    translations(value),
                    len(get_receivers_by_roles([value])),
                    translations("woost.extensions.mailer users")
                )
        ),
        min = 1,
        edit_inline = True,
        member_group = "content"
    )

    per_user_customizable = schema.Boolean(
        "per_user_customizable",
        default = False,
        member_group = "content"
    )

    pending = schema.Mapping(visible = False)

    sent = schema.Mapping(visible = False)

    errors = schema.Mapping(visible = False)

    status = schema.Integer(
        editable = False,
        enumeration = (MAILING_STARTED, MAILING_FINISHED),
        translate_value = lambda value, language = None, **kwargs: \
            "" if value is None else translations(
                "woost.extensions.mailer.mailing.Mailing.status %d" % value
            ),
        member_group = "administration"
    )

    def __init__(self, *args, **kwargs):
        Item.__init__(self, *args, **kwargs)
        self._v_template_values = {}

    def delete(self, deleted_objects = None):
        if self.id in tasks and not tasks[self.id].completed:
            raise RunningMailingError("Can't delete a running mailing")
        
        Item.delete(self, deleted_objects)

    def _get_message(self, receiver):
        message = MIMEText(
            self.render_body(receiver),
            _subtype = self.document.mime_type.split("/")[1],
            _charset = self.document.encoding
        )
        message["To"] = receiver.email
        message["From"] = self.sender
        message["Subject"] = Header(self.subject, self.document.encoding)
        message["Date"] = formatdate()

        return message

    def render_body(self, receiver):
        
        if not self.per_user_customizable and self.__cached_body:
            return self.__cached_body

        values = self._v_template_values
        
        if self.per_user_customizable:
            values = values.copy()
            values["mailing_receiver"] = receiver
        
        values["show_user_controls"] = False
        body = self.document.render(**values)

        if not self.per_user_customizable:
            self.__cached_body = body

        return body

    def send_message(self, smtp_server, receiver):
        message = self._get_message(receiver)
        try:
            return smtp_server.sendmail(self.sender, [receiver.email], message.as_string())
        except smtplib.SMTPServerDisconnected, e:
            logger.info("%d - Server disconnected, reconnecting - %s" % (
                self.id, e
            ))
            # smtplib bug
            # SMTP.quit() doesn't clear the HELO/EHLO
            # attributes, so on the next connection these
            # commands weren't sent.
            # http://bugs.python.org/issue4142
            smtp_server.helo_resp = None
            smtp_server.ehlo_resp = None
            smtp_server.connect(Site.main.smtp_host, smtplib.SMTP_PORT)
            return smtp_server.sendmail(self.sender, [receiver.email], message.as_string())
        except smtplib.SMTPSenderRefused, e:
            logger.info("%d - Maximum number of messages per connection reached, reconnecting - %s" % (
                self.id, e
            ))
            smtp_server.quit()
            # smtplib bug
            # SMTP.quit() doesn't clear the HELO/EHLO
            # attributes, so on the next connection these
            # commands weren't sent.
            # http://bugs.python.org/issue4142
            smtp_server.helo_resp = None
            smtp_server.ehlo_resp = None
            smtp_server.connect(Site.main.smtp_host, smtplib.SMTP_PORT)
            return smtp_server.sendmail(self.sender, [receiver.email], message.as_string())

    def send(self, smtp_server, template_values, current_context):

        if not self.id in tasks:
            current_user = get_current_user()
            if self.status is None:
                self.pending = self.get_receivers()
                self.total = len(self.pending)
                self.sent = {}
                self.errors = {}
                datastore.commit()

            def process():
                mailing = Mailing.get_instance(self.id)
                mailing._v_template_values = template_values.copy()
                logger.info("%d - Mailing started by user %s (%s)" % (
                    mailing.id, current_user, current_user.email
                ))

                set_current_user(current_user)
                set_language(mailing.language.iso_code)
                context.update(current_context)
                mailing.status = MAILING_STARTED
                processed_emails = 0
                try:
                    for email, receiver in mailing.pending.items():
                        try:                
                            mailing.send_message(smtp_server, receiver)
                        except Exception, e:
                            logger.exception("%d - %s (%s) - %s" % (
                                mailing.id, receiver, email, e
                            ))
                            mailing.errors[email] = e
                        else:
                            logger.info("%d - Email sent to %s (%s)" % (
                                mailing.id, receiver, email
                            ))
                            mailing.sent[email] = receiver
                            del mailing.pending[email]
                            try:
                                del mailing.errors[email]
                                logger.info("%d - Removed %s (%s) from errors" % (
                                    mailing.id, receiver, email
                                ))
                            except KeyError:
                                pass
                        finally:
                            processed_emails += 1
                            if processed_emails >= mailing.emails_per_transaction:
                                mailing._p_changed = True
                                datastore.commit()
                                processed_emails = 0
                finally:
                    if not mailing.pending:
                        mailing.status = MAILING_FINISHED
                    mailing._p_changed = True
                    try:
                        datastore.commit()
                    finally:
                        try:
                            smtp_server.quit()
                        finally:
                            datastore.close()

            task = tasks.task(process, id = self.id)
            task.mailing_id = self.id
            task.user_id = current_user.id

    def get_receivers(self):
        return get_receivers_by_roles(self.roles)


def get_receivers_by_roles(roles):
    receivers = {}
    for role in roles:
        for user in role.users:
            if user.enabled and getattr(user, "confirmed_email", True):
                receivers.setdefault(user.email, user)

    return receivers


# Validations
#------------------------------------------------------------------------------

def document_validation(member, document, context):
    if document and not document.template:
        yield DocumentTemplateRequiredError(
            member,
            document,
            context
        )

def language_validation(cls, instance, context):
    language = instance.get("language")
    document = instance.get("document")

    if language and document and language.iso_code not in document.translations.keys():
        yield LanguageValueError(
            cls.get_member("language"),
            None,
            context
        )

Mailing.document.add_validation(document_validation)
Mailing.add_validation(language_validation)
