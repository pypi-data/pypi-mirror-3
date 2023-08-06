#-*- coding: utf-8 -*-
"""

@author:		Jordi Fernández
@contact:		jordi.fernandez@whads.com
@organization:	Whads/Accent SL
@since:			March 2010
"""
import cherrypy
from campaign_monitor_api import CampaignMonitorApi
from cocktail import schema
from cocktail.modeling import cached_getter
from cocktail.pkgutils import import_object
from cocktail.controllers import FormProcessor, Form
from woost.controllers.documentcontroller import DocumentController
from woost.extensions.campaignmonitor import CampaignMonitorExtension


class CampaignMonitorController(FormProcessor, DocumentController):

    class SubscriptionForm(Form):

        campaign_monitor_errors = None

        @cached_getter
        def model(self):
            return import_object(self.controller.context["publishable"].subscription_form)

        @cached_getter
        def schema(self):
            form_schema = Form.schema(self)
            publishable = self.controller.context["publishable"]

            form_schema.add_member(schema.Reference(
                "list",
                type = "woost.extensions.campaignmonitor.campaignmonitorlist."
                    "CampaignMonitorList",
                required = True,
                enumeration = self.available_lists,
                default = self.available_lists[0]
            ))

            return form_schema

        @cached_getter
        def available_lists(self):
            
            lists = getattr(
                self.controller.context["publishable"],
                "lists",
                None
            )

            if not lists:
                raise ValueError(
                    "No Campaign Monitor lists defined for %s" % self
                )

            return lists

        @cached_getter
        def custom_fields(self):
            return {}

        def submit(self):
            Form.submit(self)

            extension = CampaignMonitorExtension.instance
            cmlist = self.data["list"]
            email = self.data["email"].encode("utf-8")
            name = self.data.get("name")
            name = name.encode("utf-8") if name else ""
     
            api = CampaignMonitorApi(
                extension.api_key,
                extension.client_id
            )

            try:
                user_subscribed = api.subscribers_get_is_subscribed(
                    cmlist.list_id,
                    email
                )
            except CampaignMonitorApi.CampaignMonitorApiException:
                user_subscribed = False

            # Obtain custom fields
            new_custom_fields = self.custom_fields

            if user_subscribed:
                response = api.subscribers_get_single_subscriber(
                    cmlist.list_id,
                    email
                )
                subscriber = response.get("Subscribers.GetSingleSubscriber")
                custom_fields = subscriber[0].get("CustomFields")
            else:
                custom_fields = {}

            custom_fields.update(**new_custom_fields)

            # Encode custom fields
            encoded_custom_fields = {}
            for key, value in custom_fields.items():
                encoded_key = (
                    key.encode("utf-8") if isinstance(key, unicode) else key
                )
                encoded_value = (
                    value.encode("utf-8") if isinstance(value, unicode) else value
                )
                encoded_custom_fields[encoded_key] = encoded_value

            try:
                api.subscriber_add_and_resubscribe(
                    cmlist.list_id,
                    email,
                    name,
                    encoded_custom_fields
                )
            except CampaignMonitorApi.CampaignMonitorApiException:
                # TODO: Capture the error code and show the correct message
                self.campaign_monitor_errors = True
            else:

                if user_subscribed and cmlist.confirmation_success_page:
                    uri = self.get_confirmation_uri(cmlist, email = email, name = name, **encoded_custom_fields)
                elif not user_subscribed and cmlist.pending_page:                
                    uri = self.get_pending_uri(cmlist, email = email, name = name, **encoded_custom_fields)
                else:
                    uri = self.get_default_uri(cmlist, email = email, name = name, **encoded_custom_fields)

                raise cherrypy.HTTPRedirect(uri.encode("utf-8"))
                
        def get_confirmation_uri(self, cmlist, **kwargs):
            return self.controller.context["cms"].uri(cmlist.confirmation_success_page)
            
        def get_pending_uri(self, cmlist, **kwargs):        
            return self.controller.context["cms"].uri(cmlist.pending_page)
            
        def get_default_uri(self, cmlist, **kwargs):
            return self.controller.context["cms"].uri(self.controller.context["publishable"])
  

