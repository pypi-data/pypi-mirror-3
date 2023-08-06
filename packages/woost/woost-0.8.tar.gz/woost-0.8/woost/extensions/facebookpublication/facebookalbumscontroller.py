#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import sys
import cherrypy
from cocktail.events import event_handler
from cocktail.translations import (
    translations,
    language_context,
    get_language
)
from cocktail import schema
from cocktail.persistence import datastore
from cocktail.controllers import (
    request_property,
    get_parameter,
    Location
)
from woost.models import File, Language, get_current_user
from woost.controllers.notifications import notify_user
from woost.controllers.backoffice.basebackofficecontroller \
    import BaseBackOfficeController
from woost.extensions.facebookpublication import FacebookPublicationExtension
from woost.extensions.facebookpublication.facebookpublicationtarget \
    import FacebookPublicationTarget
from woost.extensions.facebookpublication.facebookpublicationpermission \
    import FacebookPublicationPermission


class FacebookAlbumsController(BaseBackOfficeController):

    notice_summary_threshold = 4
    view_class = "woost.extensions.facebookpublication.FacebookAlbumsView"

    @request_property
    def form_schema(self):
        return schema.Schema("FacebookAlbumsForm", members = [
            schema.String("album_title",
                required = True                
            ),
            schema.String("album_description",                
                edit_control = "cocktail.html.TextArea"
            ),
            schema.Collection("subset",
                items = schema.Reference(
                    type = File,
                    relation_constraints = [File.resource_type.equal("image")],
                    required = True,
                    enumeration = lambda ctx: self.selection
                ),
                min = 1,
                default = schema.DynamicDefault(lambda: self.selection)
            ),
            schema.Collection("photo_languages",
                min = 1,
                items = schema.String(
                    required = True,
                    enumeration = lambda ctx: Language.codes,
                    translate_value = lambda value, language = None, **kwargs:
                        "" if not value 
                           else translations(value, language, **kwargs)
                ),
                default = schema.DynamicDefault(lambda: Language.codes)
            ),
            schema.Boolean("generate_story",
                required = True,
                default = True
            ),
            schema.Collection("publication_targets",
                items = schema.Reference(
                    type = FacebookPublicationTarget,
                    required = True,
                    enumeration = lambda ctx: self.allowed_publication_targets
                ),
                min = 1,
                default = schema.DynamicDefault(
                    lambda: self.allowed_publication_targets
                )
            )
        ])

    @request_property
    def form_data(self):
        return get_parameter(
            self.form_schema,
            errors = "ignore",
            undefined = "set_none" if self.submitted else "set_default",
            implicit_booleans = self.submitted
        )

    @request_property
    def form_errors(self):
        return schema.ErrorList(
            []
            if not self.submitted
            else self.form_schema.get_errors(self.form_data)
        )

    @event_handler
    def handle_before_request(cls, e):
        
        controller = e.source
        
        if not controller.allowed_publication_targets:
            raise cherrypy.HTTPError(403, "Forbidden")

    @request_property
    def allowed_publication_targets(self):
            
        from woost.extensions.facebookpublication \
            import FacebookPublicationExtension

        user = get_current_user()

        return [fb_target
                for fb_target in FacebookPublicationExtension.instance.targets
                if fb_target.auth_token
                and all(
                    user.has_permission(
                        FacebookPublicationPermission,
                        target = publishable,
                        publication_target = fb_target
                    )
                    for publishable in self.selection
                )]

    @request_property
    def selection(self):
        return get_parameter(
            schema.Collection("selection", 
                items = schema.Reference(
                    type = File,
                    required = True
                ),
                min = 1
            ),
            errors = "raise"
        )

    @request_property
    def submitted(self):
        return cherrypy.request.method == "POST"

    @request_property
    def valid(self):
        return self.action != "publish" \
            or self.form_schema.validate(self.form_data)

    @request_property
    def action(self):
        return cherrypy.request.params.get("action")

    def submit(self):
        
        if self.action == "close":
            self.go_back()

        form_data = self.form_data
        subset = form_data["subset"]
        album_title = form_data["album_title"]
        album_description = form_data["album_description"]
        photo_languages = set(form_data["photo_languages"])
        generate_story = form_data["generate_story"]
        targets = form_data["publication_targets"]

        results = self.results

        for target in targets:
            album_data = None
            try:
                album_data = target.publish_album(
                    album_title,
                    subset,
                    album_description = album_description,
                    photo_languages = photo_languages,
                    generate_story = generate_story
                )
            except Exception, ex:
                results.append((target, album_data, ex))
            else:
                results.append((target, album_data, None))

    @request_property
    def results(self):
        return []

    @request_property
    def output(self):
        output = BaseBackOfficeController.output(self)
        output.update(
            form_schema = self.form_schema,
            form_data = self.form_data,
            form_errors = self.form_errors,
            results = self.results
        )
        return output

