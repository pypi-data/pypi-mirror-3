#-*- coding: utf-8 -*-
"""

@author:		Jordi Fernández
@contact:		jordi.fernandez@whads.com
@organization:	Whads/Accent SL
@since:			March 2010
"""
from __future__ import with_statement
import cherrypy
from cocktail.persistence import datastore
from woost.models import changeset_context, get_current_user
from woost.controllers.backoffice.basebackofficecontroller \
    import BaseBackOfficeController
from woost.extensions.campaignmonitor import CampaignMonitorExtension 
from woost.extensions.campaignmonitor.campaignmonitorlist import \
    CampaignMonitorList


class SyncCampaignMonitorListsController(BaseBackOfficeController):

    view_class = "woost.extensions.campaignmonitor.CampaignMonitorListsSynchronizationView"

    def __call__(self, *args, **kwargs):

        if "cancel" in kwargs:
            raise cherrypy.HTTPRedirect(self.edit_uri(
                CampaignMonitorExtension.instance, 
                "lists", 
                edit_stack = None
            ))
        
        return BaseBackOfficeController.__call__(self, *args, **kwargs)

    def submit(self):

        from woost.extensions.campaignmonitor import CampaignMonitorExtension
        extension = CampaignMonitorExtension.instance    
        user = get_current_user()

        with changeset_context(author = user) as changeset:
            extension.synchronize_lists(
                restricted = True
            )

            # Report changed lists
            created = set()
            modified = set()
            deleted = set()

            for change in changeset.changes.itervalues():

                if isinstance(change.target, CampaignMonitorList):
                    action_id = change.action.identifier

                    if action_id == "create":
                        created.add(change.target)
                    elif action_id == "modify":
                        modified.add(change.target)
                    elif action_id == "delete":
                        deleted.add(change.target)

        datastore.commit()

        self.output["created_lists"] = created
        self.output["modified_lists"] = modified
        self.output["deleted_lists"] = deleted

