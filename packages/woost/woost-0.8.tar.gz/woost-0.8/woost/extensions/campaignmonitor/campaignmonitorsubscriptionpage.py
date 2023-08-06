#-*- coding: utf-8 -*-
u"""

@author:        Jordi Fernández
@contact:       jordi.fernandez@whads.com
@organization:  Whads/Accent SL
@since:         March 2010
"""
from cocktail import schema
from woost.models import Document, Template, Controller
from woost.extensions.campaignmonitor.campaignmonitorlist import \
    CampaignMonitorList


class CampaignMonitorSubscriptionPage(Document):
    
    members_order = "lists", "subscription_form", "body"

    default_template = schema.DynamicDefault(
        lambda: Template.get_instance(
            qname = u"woost.extensions.campaignmonitor.subscription_template"
        )
    )   

    default_controller = schema.DynamicDefault(
        lambda: Controller.get_instance(
            qname = u"woost.extensions.campaignmonitor.subscription_controller"
        )
    )

    body = schema.String(
        translated = True,
        listed_by_default = False,    
        edit_control = "woost.views.RichTextEditor",                                                                                                                                                           
        member_group = "content"
    )

    lists = schema.Collection(
        items = schema.Reference(
            type = CampaignMonitorList
        ),
        edit_inline = True,
        member_group = "content",
        listed_by_default = False
    )   

    subscription_form = schema.String(
        member_group = "content",
        default = \
            "woost.extensions.campaignmonitor.subscriptionform.SubscriptionForm",
        text_search = False
    )

