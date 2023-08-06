#-*- coding: utf-8 -*-
u"""

@author:		Javier Marrero
@contact:		javier.marrero@whads.com
@organization:	Whads/Accent SL
@since:			February 2009
"""
import cherrypy
from cocktail.events import event_handler
from cocktail.translations import translations
from woost.controllers.backoffice.editstack import EditNode
from woost.controllers.notifications import notify_user


class ExtensionEditNode(EditNode):

    def item_saved_notification(self, is_new, change):                                
        if change and "enabled" in change.changed_members:
            notify_user(
                translations(
                    "woost.controllers.backoffice.ExtensionEditNode "
                    "%s extension needs reloading"
                    % ("enabled" if self.item.enabled else "disabled"),
                    extension = self.item
                ),
                "notice",
                transient = False
            )
        else:
            EditNode.item_saved_notification(self, is_new, change)

