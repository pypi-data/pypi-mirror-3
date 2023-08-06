#-*- coding: utf-8 -*-
"""

@author:		Jordi Fernández
@contact:		jordi.fernandez@whads.com
@organization:	Whads/Accent SL
@since:			March 2010
"""

from cocktail import schema
from cocktail.translations import translations
from woost.models import (
    Extension,
    extension_translations,
    Site,
    StandardPage,
    Controller,
    Template,
    get_current_user,
    CreatePermission,                                                                                                                                                                                          
    ModifyPermission,
    DeletePermission,
    PermissionExpression
)

translations.define("CampaignMonitorExtension",
    ca = u"Campaign Monitor",
    es = u"Campaign Monitor",
    en = u"Campaign Monitor"
)

translations.define("CampaignMonitorExtension-plural",
    ca = u"Campaign Monitor",
    es = u"Campaign Monitor",
    en = u"Campaign Monitor"
)

class CampaignMonitorExtension(Extension):

    initialized = False

    def __init__(self, **values):
        Extension.__init__(self, **values)
        self.extension_author = u"Whads/Accent SL"
        self.set("description",
            u"""Permet la integració amb el sistema de mailing Campaign Monitor""",
            "ca"
        )
        self.set("description",            
            u"""Permite la integración con el sistema de mailing Campaign Monitor""",
            "es"
        )
        self.set("description",
            u"""Allows the integration with the Campaign Monitor mailing system""",
            "en"
        )

    def _load(self):

        from woost.extensions.campaignmonitor import (
            campaignmonitorlist,
            strings,
            useraction
        )

        from woost.extensions.campaignmonitor.campaignmonitorsubscriptionpage \
            import CampaignMonitorSubscriptionPage

        # Setup the synchronization view
        from woost.controllers.backoffice.backofficecontroller \
            import BackOfficeController
        from woost.extensions.campaignmonitor.synccontroller import \
            SyncCampaignMonitorListsController

        BackOfficeController.sync_campaign_monitor_lists = \
            SyncCampaignMonitorListsController

        # Extension fields
        from woost.extensions.campaignmonitor.campaignmonitorlist \
            import CampaignMonitorList

        CampaignMonitorExtension.add_member(
            schema.String(
                "api_key",
                required = True,
                text_search = False
            )
        )

        CampaignMonitorExtension.add_member(
            schema.String(
                "client_id",
                required = True,
                text_search = False
            )
        )

        CampaignMonitorExtension.add_member(
            schema.Collection(
                "lists",
                items = schema.Reference(
                    type = CampaignMonitorList
                ),
                integral = True,
                related_end = schema.Reference()
            )   
        )

        self.install()

    def _install(self):

        # Subscription controller        
        campaign_monitor_controller = self._create_asset(
            Controller,
            "subscription_controller",
            python_name = 
                "woost.extensions.campaignmonitor.campaignmonitorcontroller."
                "CampaignMonitorController",
            title = extension_translations
        )

        # Unsubscription controller
        unsubscription_controller = self._create_asset(
            Controller,
            "unsubscription_controller",
            python_name = 
                "woost.extensions.campaignmonitor."
                "campaignmonitorunsubscriptioncontroller."
                "CampaignMonitorUnsubscriptionController",
            title = extension_translations
        )

        # Subscription template
        subscription_view = self._create_asset(
            Template,
            "subscription_template",
            identifier =
                "woost.extensions.campaignmonitor."
                "CampaignMonitorSubscriptionView",
            engine = "cocktail",
            title = extension_translations
        )
        
        # Unsubscription template
        subscription_view = self._create_asset(
            Template,
            "unsubscription_template",
            identifier =
                "woost.extensions.campaignmonitor."
                "CampaignMonitorUnsubscriptionView",
            engine = "cocktail",
            title = extension_translations
        )
        
        # Default subscription page
        subscription_page = self._create_asset(
            CampaignMonitorSubscriptionPage,
            "subscription_page",
            title = extension_translations,
            parent = Site.main.home,
            hidden = True
        )

        # Standard Template
        standard_template = Template.get_instance(
            qname = "woost.standard_template"
        )

        # Default pending page
        pending_page = self._create_asset(
            StandardPage,
            "pending_page",
            title = extension_translations,
            body = extension_translations,
            parent = Site.main.home,
            template = standard_template,
            hidden = True
        )

        # Default confirmation success page
        confirmation_success_page = self._create_asset(
            StandardPage,
            "confirmation_success_page",
            title = extension_translations,
            body = extension_translations,
            parent = Site.main.home,
            template = standard_template,
            hidden = True
        )

        # Default unsubscribe page
        unsubscribe_page = self._create_asset(
            StandardPage,
            "unsubscribe_page",
            title = extension_translations,
            body = extension_translations,
            controller = unsubscription_controller,
            template = unsubscription_view,
            parent = Site.main.home,
            hidden = True
        )

    def synchronize_lists(self, restricted = False):                                                                                                                                                      
        """Synchronizes the list of Lists of the given Campaign Monitor account 
        with the site's database.

        The method queries Campaing Monitor API, retrieving the list of
        Lists for the indicated account and comparing it with the set of
        already known Lists (from previous executions of this method). The
        local database will be updated as follows:

            * Lists declared by Campaing Monitor that are not present in the 
              database will generate new instances.
            * Lists that exist on both ends will be updated with the data
              provided by the Campaing Monitor service (only non editable 
              members will be updated, so that data entered by users in the 
              backoffice is preserved).
            * Lists that were instantiated in a previous run but which have
              been deleted at the Campaign Monitor side will be removed from 
              the database.
                
        @param restricted: Indicates if access control should be applied to the
            operations performed by the method.
        @type restricted: bool
        """
        from campaign_monitor_api import CampaignMonitorApi
        from cocktail.controllers import context
        from cocktail.controllers.location import Location
        from woost.extensions.campaignmonitor.campaignmonitorlist import \
            CampaignMonitorList

        if restricted:
            user = get_current_user()

        api = CampaignMonitorApi(
            self.api_key,
            self.client_id
        )

        remote_lists = set()
        
        for list_data in api.client_get_lists():

            list_id = list_data["ListID"]
            cmlist = CampaignMonitorList.get_instance(list_id = list_id)
            remote_lists.add(list_id)

            # Check permissions
            if restricted and not user.has_permission(
                CreatePermission if cmlist is None else ModifyPermission,
                target = (cmlist or CampaignMonitorList)
            ):
                continue

            # Create new lists
            if cmlist is None:
                cmlist = CampaignMonitorList()
                cmlist.insert()
                cmlist.list_id = list_id
                self.lists.append(cmlist)

            # Modify new or updated lists with remote data
            cmlist.title = list_data.get("Name")

            list_detail_data = api.list_get_detail(list_id)

            # Modify remote lists with page urls

            def absolute_uri(publishable, *args, **kwargs):
                location = Location.get_current_host()
                location.path_info = context["cms"].uri(
                    publishable,
                    *args,
                    **kwargs
                )
                return str(location)

            if cmlist.unsubscribe_page:
                unsubscribe_page = "%s?user=[email]" % absolute_uri(cmlist.unsubscribe_page)
            else:
                unsubscribe_page = list_detail_data.get("UnsubscribePage")

            if cmlist.confirmation_success_page:
                confirmation_success_page = absolute_uri(cmlist.confirmation_success_page)
            else:
                confirmation_success_page = list_detail_data.get("ConfirmationSuccessPage")

            api.list_update(
                list_id,
                list_detail_data.get("Title"), 
                unsubscribe_page,
                list_detail_data.get("ConfirmOptIn"), 
                confirmation_success_page
            )

        # Delete lists that have been deleted from the user account
        missing_lists = CampaignMonitorList.select(
            CampaignMonitorList.list_id.not_one_of(remote_lists),
        )

        if restricted:
            missing_lists.add_filter(
                PermissionExpression(user, DeletePermission)
            )

        missing_lists.delete_items()

