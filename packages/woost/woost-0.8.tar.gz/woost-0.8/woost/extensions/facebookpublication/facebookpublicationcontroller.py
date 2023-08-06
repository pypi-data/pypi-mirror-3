#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import sys
import cherrypy
from cocktail.iteration import first
from cocktail.events import event_handler
from cocktail.translations import translations, language_context
from cocktail import schema
from cocktail.persistence import datastore
from cocktail.controllers import (
    request_property,
    get_parameter,
    Location
)
from woost.models import Publishable, get_current_user
from woost.controllers.notifications import notify_user
from woost.controllers.backoffice.basebackofficecontroller \
    import BaseBackOfficeController
from woost.extensions.opengraph import OpenGraphExtension
from woost.extensions.facebookpublication import FacebookPublicationExtension
from woost.extensions.facebookpublication.facebookpublicationtarget \
    import FacebookPublicationTarget
from woost.extensions.facebookpublication.facebookpublicationpermission \
    import FacebookPublicationPermission


class FacebookPublicationController(BaseBackOfficeController):

    notice_summary_threshold = 4
    view_class = "woost.extensions.facebookpublication.FacebookPublicationView"

    @request_property
    def form_schema(self):
        return schema.Schema("FacebookPublicationForm", members = [
            schema.Collection("subset",
                items = schema.Reference(
                    type = Publishable,
                    required = True,
                    enumeration = lambda ctx: self.selection
                ),
                min = 1,
                default = schema.DynamicDefault(lambda: self.selection)
            ),
            schema.Collection("published_languages",
                items = schema.String(
                    translate_value = lambda value, language = None, **kwargs:
                        "" if not value 
                           else translations(value, language, **kwargs),
                    enumeration = lambda ctx: self.eligible_languages
                ),
                min = 1,
                default = schema.DynamicDefault(
                    lambda: self.eligible_languages
                )
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
            undefined = "set_none" if self.submitted else "set_default"
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
    def eligible_languages(self):

        selection_languages = set()

        for publishable in self.selection:
            selection_languages.update(publishable.translations.iterkeys())

        target_languages = set()

        for target in self.allowed_publication_targets:
            target_languages.update(target.languages)

        return selection_languages & target_languages

    @request_property
    def selection(self):
        return get_parameter(
            schema.Collection("selection", 
                items = schema.Reference(
                    type = Publishable,
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
        languages = set(form_data["published_languages"])
        targets = form_data["publication_targets"]
        check = (self.action == "check")

        results = self.results

        if check:
            og = OpenGraphExtension.instance

        for target in targets:
            
            if check:
                posts = target.feed_posts()

            for publishable in subset:
                for language in sorted(languages & set(target.languages)):
                    if check:
                        try:
                            with language_context(language):
                                uri = og.get_properties(publishable)["og:url"]

                            results.append((
                                publishable, 
                                target,
                                language,
                                first(
                                    post
                                    for post in posts 
                                    if post.get("link") == uri
                                )
                            ))
                        except Exception, ex:
                            results.append((publishable, target, language, ex))
                    else:
                        try:
                            with language_context(language):
                                target.publish(publishable)
                        except Exception, ex:
                            results.append((publishable, target, language, ex))
                        else:
                            results.append((publishable, target, language, None))

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
            results = self.results,
            action = self.action
        )
        return output

