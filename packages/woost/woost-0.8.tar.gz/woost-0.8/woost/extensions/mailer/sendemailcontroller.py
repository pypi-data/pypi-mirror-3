#-*- coding: utf-8 -*-
u"""

@author:		Jordi Fernández
@contact:		jordi.fernandez@whads.com
@organization:	Whads/Accent SL
@since:			September 2010
"""
import smtplib
import cherrypy
from simplejson import dumps
from cocktail import schema
from cocktail.events import event_handler
from cocktail.modeling import cached_getter
from cocktail.translations import set_language
from cocktail.controllers.location import Location
from woost.models import Site, User, get_current_user
from woost.models.permission import ReadPermission
from woost.controllers.backoffice.editcontroller import EditController
from woost.extensions.mailer.mailing import Mailing, MAILING_STARTED, MAILING_FINISHED, tasks
from woost.extensions.mailer.sendemailpermission import SendEmailPermission


class SendEmailController(EditController):

    view_class = "woost.extensions.mailer.SendEmailView"
    section = "send_email"
    task_id = None

    @event_handler
    def handle_traversed(cls, event):
        user = get_current_user()
        user.require_permission(SendEmailPermission)

    @cached_getter
    def smtp_server(self):
        site = Site.main
        smtp = smtplib.SMTP(site.smtp_host, smtplib.SMTP_PORT)

        if site.smtp_user and site.smtp_password:
            smtp.login(
                str(site.smtp_user),
                str(site.smtp_password)
            )

        return smtp

    @cached_getter
    def submitted(self):
        return self.action is not None \
            or self.mailer_action in ("test", "send")

    @cached_getter
    def mailer_action(self):
        mailing = self.context["cms_item"]
        mailer_action = self.params.read(schema.String("mailer_action"))

        if mailer_action in ("test", "send") and mailing.status == MAILING_FINISHED:
            raise cherrypy.HTTPError(403, "Forbidden")

        if mailer_action is None:
            if mailing.status is None:
                mailer_action = "confirmation"
            elif mailing.status == MAILING_STARTED:
                mailer_action = "send"
            elif mailing.status == MAILING_FINISHED:
                mailer_action = "show"

        # A mailer action is required
        assert mailer_action

        return mailer_action

    @cherrypy.expose
    def mailing_state(self, task_id, *args, **kwargs):
        cherrypy.response.headers["Content-Type"] = "application/json"

        task = tasks.get(int(task_id))

        # If task is expired show the status from the mailing object
        if task is None:
            mailing = self.context["cms_item"]
        else:
            mailing = Mailing.get_instance(task.mailing_id)

        if mailing is None:
            return dumps({})

        user = get_current_user()
        if not user.has_permission(ReadPermission, target = mailing):
            raise cherrypy.HTTPError(403, "Forbidden")

        tasks.remove_expired_tasks()

        return dumps({
            "sent": len(mailing.sent),
            "errors": len(mailing.errors),
            "total": mailing.total,
            "completed": task and task.completed or True
        })

    def submit(self):

        mailing = self.context["cms_item"]

        if self.mailer_action == "test":

            # Send a test email
            mailing._v_template_values = {
                "cms": self.context["cms"],
                "base_url": unicode(Location.get_current_host()).rstrip("/")
            }
            test_email = self.params.read(schema.String("test_email"))
            # Create a fake user
            receiver = User(email = test_email)
            set_language(mailing.language.iso_code)
            mailing.send_message(self.smtp_server, receiver)

        elif self.mailer_action == "send":

            # Send the mailing
            self.task_id = mailing.id
            template_values = {
                "cms": self.context["cms"],
                "base_url": unicode(Location.get_current_host()).rstrip("/")
            }
            mailing.send(self.smtp_server, template_values, self.context.copy())

        else:
            EditController.submit(self)

    @cached_getter
    def output(self):
        output = EditController.output(self)
        
        if self.task_id:
            task_id = self.task_id
        else:
            task_id = self.context["cms_item"] and self.context["cms_item"].id or None

        output.update(
            action = self.mailer_action,
            task_id = task_id
        )
        return output

