#-*- coding: utf-8 -*-
u"""

@author:        Jordi Fernández
@contact:       jordi.fernandez@whads.com
@organization:  Whads/Accent SL
@since:         March 2010
"""
from cocktail import schema
from cocktail.events import event_handler
from cocktail.persistence import datastore
from woost.models import Item, StandardPage

class CampaignMonitorList(Item):

    visible_from_root = False

    members_order = [
        "list_id",
        "pending_page",
        "confirmation_success_page",
        "unsubscribe_page",
    ]   

    default_pending_page = schema.DynamicDefault(
        lambda: StandardPage.get_instance(
            qname = u"woost.extensions.campaignmonitor.pending_page"
        )
    )   

    title = schema.String(
        editable = False,
        listed_by_default = False,
        descriptive = True
    )

    list_id = schema.String(
        unique = True,
        editable = False,
        text_search = False
    )

    unsubscribe_page = schema.Reference(
        type = "woost.models.Publishable",
        related_end = schema.Collection()
    )

    pending_page = schema.Reference(
        required = True,
        type = "woost.models.Publishable",
        related_end = schema.Collection()
    )

    confirmation_success_page = schema.Reference(
        type = "woost.models.Publishable",
        related_end = schema.Collection()
    )

