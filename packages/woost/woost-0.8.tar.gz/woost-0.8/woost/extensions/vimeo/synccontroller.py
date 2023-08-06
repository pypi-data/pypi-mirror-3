#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			February 2010
"""
from __future__ import with_statement
import cherrypy
from cocktail.modeling import cached_getter
from cocktail import schema
from cocktail.persistence import datastore
from cocktail.controllers import FormControllerMixin
from woost.models import changeset_context, get_current_user
from woost.controllers.backoffice.basebackofficecontroller \
    import BaseBackOfficeController
from woost.extensions.vimeo.video import VimeoVideo


class SyncVimeoController(FormControllerMixin, BaseBackOfficeController):

    view_class = "woost.extensions.vimeo.VimeoSynchronizationView"

    def __call__(self, *args, **kwargs):

        if "cancel" in kwargs:
            raise cherrypy.HTTPRedirect(self.contextual_uri())
        
        return BaseBackOfficeController.__call__(self, *args, **kwargs)

    @cached_getter
    def form_model(self):
        from woost.extensions.vimeo import VimeoExtension
        return schema.Schema("VimeoSynchronizationForm", members = [
            schema.String("vimeo_user_name",
                required = True,
                text_search = False,
                default = schema.DynamicDefault(
                    lambda: VimeoExtension.instance.default_vimeo_user_name
                )
            )
        ])

    def submit(self):

        # Read form data
        FormControllerMixin.submit(self)
        
        from woost.extensions.vimeo import VimeoExtension
        extension = VimeoExtension.instance        
        user = get_current_user()

        with changeset_context(author = user) as changeset:
            extension.synchronize(
                self.form_instance["vimeo_user_name"],
                restricted = True
            )

        # Report changed videos
        created = set()
        modified = set()
        deleted = set()

        for change in changeset.changes.itervalues():

            if isinstance(change.target, VimeoVideo):
                action_id = change.action.identifier

                if action_id == "create":
                    created.add(change.target)
                elif action_id == "modify":
                    modified.add(change.target)
                elif action_id == "delete":
                    deleted.add(change.target)

        datastore.commit()

        self.output["created_videos"] = created
        self.output["modified_videos"] = modified
        self.output["deleted_videos"] = deleted

