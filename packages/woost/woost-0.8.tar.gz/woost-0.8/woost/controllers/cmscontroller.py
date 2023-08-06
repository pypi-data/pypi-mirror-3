#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
import os.path
from string import ascii_letters
from sha import sha
from random import choice
from warnings import warn

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

import rfc822
import cherrypy
from cherrypy.lib.cptools import validate_since
from pkg_resources import resource_filename, iter_entry_points
from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options
from beaker.middleware import SessionMiddleware
from cocktail.events import Event, event_handler
from cocktail.translations import get_language, set_language
from cocktail.controllers import (
    Dispatcher, 
    Location, 
    folder_publisher,
    try_decode,
    session
)
from cocktail.controllers.asyncupload import AsyncUploadController
from cocktail.controllers.uriutils import percent_encode
from cocktail.persistence import datastore
from woost import app
from woost.models import (
    Item,
    Publishable,
    URI,
    Site,
    ReadPermission,
    ReadTranslationPermission,
    AuthorizationError,
    get_current_user
)
from woost.models.icons import IconResolver
from woost.controllers.asyncupload import async_uploader
from woost.controllers import get_cache_manager, set_cache_manager
from woost.controllers.basecmscontroller import BaseCMSController
from woost.controllers.language import LanguageModule
from woost.controllers.authentication import (
    AuthenticationModule,
    AuthenticationFailedError
)
from woost.controllers.imagescontroller import ImagesController
from woost.controllers.imageeffectscontroller import ImageEffectsController


class CMSController(BaseCMSController):
    
    application_settings = None

    # Application events
    item_saved = Event(doc = """
        An event triggered after an item is inserted or modified.

        @ivar item: The saved item.
        @type item: L{Item<woost.models.Item>}

        @ivar user: The user who saved the item.
        @type user: L{User<woost.models.user.User>}

        @ivar is_new: True for an insertion, False for a modification.
        @type is_new: bool

        @ivar change: The revision describing the changes to the item.
        @type change: L{Change<woost.models.Change>}
        """)

    item_deleted = Event(doc = """
        An event triggered after an item is deleted.

        @ivar item: The deleted item.
        @type item: L{Item<woost.models.Item>}

        @ivar user: The user who deleted the item.
        @type user: L{User<woost.models.user.User>}

        @ivar change: The revision describing the changes to the item.
        @type change: L{Change<woost.models.Change>}
        """)

    producing_output = Event(doc = """
        An event triggered to allow setting site-wide output for controllers.

        @ivar controller: The controller that is producing the output.
        @type controller: L{BaseCMSController
                            <woost.controllers.basecmscontroller
                            .BaseCMSController>}

        @ivar output: The output for the controller. Event handlers can modify
            it as required.
        @type output: dict
        """)

    # Application modules
    LanguageModule = LanguageModule
    AuthenticationModule = AuthenticationModule

    # Webserver configuration
    virtual_path = "/"

    # Enable / disable confirmation dialogs when closing an edit session. This
    # setting exists mainly to disable the dialogs on selenium test runs.
    closing_item_requires_confirmation = True

    # A dummy controller for CherryPy, that triggers the cocktail dispatcher.
    # This is done so dynamic dispatching (using the resolve() method of
    # request handlers) can depend on session setup and other requirements
    # being available beforehand.
    class ApplicationContainer(object):

        def __init__(self, cms):
            self.__cms = cms
            self.__dispatcher = Dispatcher()

            # Set the default location for file-based sessions
            sconf = session.config
            using_file_sessions = (sconf.get("session.type") == "file")
            using_dbm_sessions = (sconf.get("session.type") == "dbm")
            lock_dir_missing = (
                not using_file_sessions 
                and not sconf.get("session.lock_dir")
            )
            data_dir_missing = (
                (
                    using_file_sessions 
                    or (using_dbm_sessions and not
                        sconf.get("session.dbm_dir"))
                )
                and not sconf.get("session.data_dir")
            )

            if lock_dir_missing or data_dir_missing:
                
                session_path = app.path("sessions")
                if not os.path.exists(session_path):
                    os.mkdir(session_path)

                if lock_dir_missing:
                    sconf["session.lock_dir"] = session_path

                if data_dir_missing:
                    sconf["session.data_dir"] = session_path

            if not sconf.get("session.secret"):

                session_key_path = app.path(".session_key")
                if os.path.exists(session_key_path):
                    with open(session_key_path, "r") as session_key_file:
                        session_key = session_key_file.readline()
                else:
                    with open(session_key_path, "w") as session_key_file:
                        session_key = sha("".join(
                            choice(ascii_letters) 
                            for i in range(10)
                        )).hexdigest()
                        session_key_file.write(session_key)

                sconf["session.secret"] = session_key

            # If the cache manager doesn't exist, create it
            if not get_cache_manager():
                cache_path = app.path('cache')

                if not os.path.exists(cache_path):
                    os.mkdir(cache_path)

                cache_manager = CacheManager(
                    **parse_cache_config_options({
                        'cache.lock_dir': cache_path,
                        'cache.regions': 'woost_cache',
                        'cache.woost_cache.type': 'memory'
                    })
                )
                set_cache_manager(cache_manager)

            # Create the folders for uploaded files
            upload_path = app.path("upload")
            if not os.path.exists(upload_path):
                os.mkdir(upload_path)

            temp_path = app.path("upload", "temp")
            if not os.path.exists(temp_path):
                os.mkdir(temp_path)

            async_uploader.temp_folder = temp_path

        @cherrypy.expose
        def default(self, *args, **kwargs):
            # All requests are forwarded to the nested dispatcher:
            return self.__dispatcher.respond(args, self.__cms)

        # Static resources
        resources = folder_publisher(
            resource_filename("woost.views", "resources")
        )
        
        cocktail = folder_publisher(
            resource_filename("cocktail.html", "resources")
        )

    def session_middleware(self, app):
        return SessionMiddleware(app, session.config)

    def __init__(self, *args, **kwargs):
    
        BaseCMSController.__init__(self, *args, **kwargs)

        self.language = self.LanguageModule(self)
        self.authentication = self.AuthenticationModule(self)

    def run(self, block = True):
                
        self.mount()
    
        if hasattr(cherrypy.engine, "signal_handler"):
            cherrypy.engine.signal_handler.subscribe()

        if hasattr(cherrypy.engine, "console_control_handler"):
            cherrypy.engine.console_control_handler.subscribe()
    
        cherrypy.engine.start()
        
        if block:
            cherrypy.engine.block()
        else:
            cherrypy.engine.wait(cherrypy.engine.states.STARTED)            

    def mount(self):

        app = cherrypy.Application(self.ApplicationContainer(self))

        # Session middleware
        app.wsgiapp.pipeline.append(
            ("beaker_session", self.session_middleware)
        )

        return cherrypy.tree.mount(
            app,
            self.virtual_path,
            self.application_settings
        )

    def resolve(self, path):
        
        # Allow application modules (ie. language) to process the URI before
        # resolving the requested publishable item
        self._process_path(path)
 
        site = Site.main
        request = cherrypy.request
        unicode_path = [try_decode(step) for step in path]

        # Item resolution
        path_resolution = site.resolve_path(unicode_path)

        if path_resolution:
            publishable = path_resolution.item

            for step in path_resolution.matching_path:
                path.pop(0)

            self.canonical_redirection(path_resolution)        
        else:
            publishable = site.home
        
        self.context["publishable"] = publishable

        # HTTP/HTTPS check
        self._apply_https_policy(publishable)

        # Controller resolution
        controller = publishable.resolve_controller()

        if controller is None:
            raise cherrypy.NotFound()

        # Add the selected language to the current URI
        if publishable.per_language_publication:
            if not request.language_specified:
                location = Location.get_current()
                location.path_info = "/" + get_language() + location.path_info
                location.go()

        # Remove the language selection from the current URI
        elif request.language_specified:
            location = Location.get_current()
            location.path_info = \
                "/" + "/".join(location.path_info.strip("/").split("/")[1:])
            location.go()

        return controller

    def canonical_redirection(self, path_resolution):
        """Redirect the current request to the canonical URL for the selected
        publishable element.
        """        
        site = Site.main
        publishable = path_resolution.item

        # Find the canonical path for the element
        canonical_path = site.get_path(publishable)

        if canonical_path is None:
            return

        canonical_path = canonical_path.strip("/")
        canonical_path = (
            canonical_path.split("/")
            if canonical_path
            else []
        )

        # The current request matches the canonical path, do nothing
        if canonical_path == path_resolution.matching_path:
            return

        canonical_uri = "".join(
            percent_encode(c) for c in "/" + "/".join(
                step for step in (
                    canonical_path
                    + path_resolution.extra_path
                )
            )
        )

        if publishable.per_language_publication:
            canonical_uri = \
                self.language.translate_uri(canonical_uri)

        if cherrypy.request.query_string:
            canonical_uri = canonical_uri + \
                "?" + cherrypy.request.query_string

        raise cherrypy.HTTPRedirect(canonical_uri)

    def _process_path(self, path):

        # Invoke the language module to set the active language
        self.language.process_request(path)

    def uri(self, publishable, *args, **kwargs):
        """Obtains the canonical absolute URI for the given item.

        @param publishable: The item to obtain the canonical URI for.
        @type publishable: L{Publishable<woost.models.publishable.Publishable>}

        @param args: Additional path components to append to the produced URI.
        @type args: unicode

        @param kwargs: Key/value pairs to append to the produced URI as query
            string parameters.
        @type kwargs: (unicode, unicode)

        @return: The item's canonical URI, or None if no matching URI can be
            constructed.
        @rtype: unicode
        """
        warn(
            "CMS.uri() is deprecated, use Publishable.get_uri() instead",
            DeprecationWarning,
            stacklevel = 2
        )

        # User defined URIs
        if isinstance(publishable, URI):
            uri = publishable.uri

        # Regular elements
        else:
            uri = Site.main.get_path(publishable)
            
            if uri is not None:
                
                if publishable.per_language_publication:
                    uri = self.language.translate_uri(uri)

                uri = self.application_uri(uri, *args, **kwargs)
 
        if uri:
            uri = "".join(percent_encode(c) for c in uri)

        return uri

    def translate_uri(self, path = None, language = None):
        return self.application_uri(
            self.language.translate_uri(path = path, language = language)
        )

    def image_uri(self, element, factory = "default"):

        if not isinstance(element, (int, basestring)):
            if isinstance(element, type) \
            or not getattr(element, "is_inserted", False):
                element = element.full_name
            elif hasattr(element, "id"):
                element = element.id

        return self.application_uri("images", element, factory)

    def validate_publishable(self, publishable):

        if not publishable.is_published():
            raise cherrypy.NotFound()

        user = get_current_user()
        
        user.require_permission(ReadPermission, target = publishable)
        user.require_permission(
            ReadTranslationPermission,
            language = get_language()
        )

    @event_handler
    def handle_traversed(cls, event):

        datastore.sync()

        cms = event.source
        
        cms.context.update(
            cms = cms,
            publishable = None
        )

        # Set the default language as soon as possible
        language = cms.language.infer_language()
        set_language(language)

        # Invoke the authentication module
        cms.authentication.process_request()

    @event_handler
    def handle_before_request(cls, event):
        
        cms = event.source

        # Validate access to the requested item
        publishable = cms.context.get("publishable")
        if publishable is not None:
            cms.validate_publishable(publishable)

            # Set the content type and encoding
            content_type = publishable.mime_type
            if content_type:
                encoding = publishable.encoding
                if encoding:
                    content_type += ";charset=" + encoding
                cherrypy.response.headers["Content-Type"] = content_type

            # TODO: encode / decode the request based on the 'encoding' member?

    @event_handler
    def handle_producing_output(cls, event):
        # Set application wide output parameters
        cms = event.source
        event.output.update(
            cms = cms,
            site = Site.main,
            user = get_current_user(),
            publishable = event.controller.context.get("publishable")
        )

    @event_handler
    def handle_exception_raised(cls, event):

        error = event.exception
        controller = event.source

        content_type = cherrypy.response.headers.get("Content-Type")
        pos = content_type.find(";")

        if pos != -1:
            content_type = content_type[:pos]

        if content_type in ("text/html", "text/xhtml"):

            error_page, status = event.source.get_error_page(error)

            if status:
                cherrypy.request.status = status

            if error_page:
                event.handled = True

                # HTTP/HTTPS check
                controller._apply_https_policy(error_page)

                controller.context.update(
                    original_publishable = controller.context["publishable"],
                    publishable = error_page
                )
                
                response = cherrypy.response
                response.status = status 
                
                error_controller = error_page.resolve_controller()

                # Instantiate class based controllers
                if isinstance(error_controller, type):
                    error_controller = error_controller()
                    error_controller._rendering_format = "html"

                response.body = error_controller()
    
    def get_error_page(self, error):
        """Produces a custom error page for the indicated exception.

        @param error: The exception to describe.
        @type error: Exception

        @return: A tuple comprised of a publishable item to delegate to and an
            HTTP status to set on the response. Either component can be None,
            so that no custom error page is shown, or that the status is not
            changed, respectively.
        @rtype: (L{Document<woost.models.Document>}, int)
        """
        site = Site.main
        is_http_error = isinstance(error, cherrypy.HTTPError)

        # Page not found
        if is_http_error and error.status == 404:
            return site.not_found_error_page, 404
        
        # Access forbidden:
        # The default behavior is to show a login page for anonymous users, and
        # a 403 error message for authenticated users.
        elif is_http_error and error.status == 403 \
        or isinstance(error, (AuthorizationError, AuthenticationFailedError)):
            if get_current_user().anonymous:

                publishable = self.context["publishable"]

                while publishable is not None:
                    login_page = publishable.login_page
                    if login_page is not None:
                        return login_page, 200
                    publishable = publishable.parent

                return site.login_page, 200
            else:
                return site.forbidden_error_page, 403
        
        # Generic error
        elif is_http_error and error.status == 500 \
        or not is_http_error:
            return site.generic_error_page, 500

        return None, None

    def _apply_https_policy(self, publishable):
        
        site = Site.main
        policy = site.https_policy

        if policy == "always":
            Location.require_https()
        elif policy == "never":
            Location.require_http()
        elif policy == "per_page":
            if publishable.requires_https \
            or not get_current_user().anonymous:
                Location.require_https()
            elif not site.https_persistence:
                Location.require_http()

    @event_handler
    def handle_after_request(cls, event):
        datastore.abort()

    images = ImagesController
    image_effects = ImageEffectsController

    async_upload = AsyncUploadController()
    async_upload.uploader = async_uploader

