#-*- coding: utf-8 -*-
"""

@author:		Jordi Fernández
@contact:		jordi.fernandez@whads.com
@organization:	Whads/Accent SL
@since:			April 2010
"""
import cherrypy
from datetime import datetime
from campaign_monitor_api import CampaignMonitorApi
from cocktail import schema
from cocktail.modeling import cached_getter
from cocktail.controllers import context
from woost.models import Site, StandardPage
from woost.controllers.documentcontroller import DocumentController
from woost.extensions.campaignmonitor import CampaignMonitorExtension
from woost.extensions.campaignmonitor.campaignmonitorsubscriptionpage \
    import CampaignMonitorSubscriptionPage


class CampaignMonitorUnsubscriptionController(DocumentController):

    subscriber = None
    action = None
    max_seconds = 60 * 60

    def __init__(self, *args, **kwargs):
        self.subscriber = self.params.read(schema.String("user"))
        self.action = self.params.read(schema.String("action"))

        DocumentController.__init__(self, *args, **kwargs)

    def submit(self, *args, **kwargs):

        if self.action == "resubscribe" and self.subscriber:
            self.resubscribe(self.subscriber)

    
    def resubscribe(self, email):
        extension = CampaignMonitorExtension.instance

        api = CampaignMonitorApi(
            extension.api_key,
            extension.client_id
        )

        lists = api.client_get_lists()

        resubscribed_lists = 0
        cm_context = {
            "email": email,
            "lists": []
        }
        for i, list in enumerate(lists):
            try:
                response = api.subscribers_get_single_subscriber(
                    list.get("ListID"),
                    email.encode("utf-8")
                )
            except CampaignMonitorApi.CampaignMonitorApiException:
                continue
            else:
                subscriber = response.get("Subscribers.GetSingleSubscriber")
                name = subscriber[0].get("Name")
                date = subscriber[0].get("Date")
                state = subscriber[0].get("State")
                
                cm_context["lists"].append({
                    "list_id": list.get("ListID"),
                    "name": name,
                    "state": state,
                    "date": date
                })

                if state == "Unsubscribed":
                    date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
                    now = datetime.now()

                    diff = now - date

                    if date > now or diff.seconds < self.max_seconds:
                        custom_fields = subscriber[0].get("CustomFields")

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
                            
                            cm_context["lists"][i].update(**encoded_custom_fields)

                        try:
                            # Resubscribe
                            resubscribed_lists += 1
                            api.subscriber_add_and_resubscribe(
                                list.get("ListID"), 
                                email.encode("utf-8"), 
                                name.encode("utf-8") if name else name,
                                encoded_custom_fields
                            )
                        except CampaignMonitorApi.CampaignMonitorApiException:
                            self.campaign_monitor_errors = True

        uri = None

        if resubscribed_lists == 0:
            uri = self.get_subscription_uri(**cm_context)
        else:
            uri = self.get_pending_uri(**cm_context)

        if uri is None:
            uri = context["cms"].uri(
                Site.main.home
            )
            
        raise cherrypy.HTTPRedirect(uri.encode("utf-8"))

    def get_subscription_uri(self, **kwargs):
        subscription_page = CampaignMonitorSubscriptionPage.get_instance(
            qname = u"woost.extensions.campaignmonitor.subscription_page"
        )
        if subscription_page:
            return context["cms"].uri(subscription_page)

    def get_pending_uri(self, **kwargs):
        pending_page = StandardPage.get_instance(
            qname = u"woost.extensions.campaignmonitor.pending_page"
        )
        if pending_page:
            return context["cms"].uri(pending_page)


    @cached_getter
    def output(self):
        output = DocumentController.output(self)
        output.update(
            subscriber = self.subscriber
        )

        return output
