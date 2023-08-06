#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""
import cherrypy
from simplejson import dumps
from cocktail.pkgutils import resolve
from cocktail.events import event_handler
from cocktail.controllers import view_state
from cocktail.translations import (
    translations,
    get_language,
    set_language
)
from cocktail.html import Element
from cocktail import schema
from woost.models import (
    get_current_user,
    ReadPermission,
    Site
)
from woost.controllers.backoffice.basebackofficecontroller \
    import BaseBackOfficeController
from woost.controllers.backoffice.contentcontroller \
    import ContentController
from woost.controllers.backoffice.deletecontroller import DeleteController
from woost.controllers.backoffice.ordercontroller import OrderController
from woost.controllers.backoffice.movecontroller import MoveController
from woost.controllers.backoffice.renderpreviewcontroller \
    import RenderPreviewController
from woost.controllers.backoffice.changelogcontroller \
    import ChangeLogController
from woost.controllers.backoffice.uploadfilescontroller \
    import UploadFilesController


class BackOfficeController(BaseBackOfficeController):

    _cp_config = BaseBackOfficeController.copy_config()
    _cp_config["rendering.engine"] = "cocktail"
    
    _edit_stacks_manager_class = \
        "woost.controllers.backoffice.editstack.EditStacksManager"

    default_section = "content"

    content = ContentController    
    delete = DeleteController
    order = OrderController
    move = MoveController
    changelog = ChangeLogController
    render_preview = RenderPreviewController
    upload_files = UploadFilesController
    
    def submit(self):
        raise cherrypy.HTTPRedirect(
            self.contextual_uri(self.default_section) + "?" + view_state())

    @event_handler
    def handle_traversed(cls, event):
        controller = event.source
        controller.context["edit_stacks_manager"] = \
            resolve(controller._edit_stacks_manager_class)()

    @event_handler
    def handle_before_request(cls, event):
        user = get_current_user()
        language = \
            user and user.prefered_language or Site.main.backoffice_language
        set_language(language)

    @event_handler
    def handle_after_request(cls, event):
        
        if event.error is None:
            controller = event.source
            edit_stacks_manager = controller.context["edit_stacks_manager"]
            edit_stack = edit_stacks_manager.current_edit_stack
            
            if edit_stack is not None:
                edit_stacks_manager.preserve_edit_stack(edit_stack)

    @cherrypy.expose
    def editor_attachments(self, **kwargs):
        
        cms = self.context["cms"]
        node = self.stack_node
        attachments = schema.get(node.form_data, "attachments", default = None)

        resource_type = self.params.read(schema.String("resource_type"))
            
        language = self.params.read(schema.String("language"))
        
        output = []
        cherrypy.response.headers["Content-Type"] = "text/javascript"

        if attachments:
            for attachment in attachments:
                item = None 
                if resource_type == "linkable" and attachment.resource_type not in ["image","video"]:
                    item = attachment
                elif attachment.resource_type == resource_type:
                    item = attachment
                
                if item:
                    output.append(
                        [
                            item.get("title", language),
                            item.get_uri()
                        ]
                    )

        if resource_type == "image":
            return "var tinyMCEImageList = %s" % (dumps(output))
        elif resource_type == "video":
            return "var tinyMCEMediaList = %s" % (dumps(output))
        else:
            return "var tinyMCELinkList = %s" % (dumps(output))

    @cherrypy.expose
    def keep_alive(self, *args, **kwargs):
        pass
