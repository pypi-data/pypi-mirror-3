#-*- coding: utf-8 -*-
"""

@author:		Jordi Fernández
@contact:		jordi.fernandez@whads.com
@organization:	Whads/Accent SL
@since:			March 2010
"""
import os
from shutil import rmtree
from subprocess import Popen, PIPE
from cocktail import schema
from cocktail.controllers import context as controller_context
from cocktail.modeling import abstractmethod, getter
from cocktail.translations import translations
from cocktail.controllers.location import Location
from woost import app
from woost.models import Item


class StaticSiteSnapShoter(Item):
    """A class tasked with creating a static snapshot of a site's content to
    a concrete location.
    
    This is mostly an abstract class, meant to be extended by subclasses. Each
    subclass should implement the static snapshot creation. 
    """
    instantiable = False
    visible_from_root = False
    integral = True

    def setup(self, context):
        """Prepares the exporter for an export process.

        The object of this method is to allow exporters to perform any
        initialization they require before writing files to their destination.

        @param context: A dictionary where the exporter can place any
            contextual information it many need throgout the export process. It
            will be made available to all L{write_file} calls.
        @type context: dict
        """

    def cleanup(self, context):
        """Frees resources after an export operation.

        This method is guaranteed to be called after the export operation is
        over, even if an exception was raised during its execution.

        @param context: The dictionary used by the exporter during the export
            process to maintain its contextual information.
        @type context: dict
        """

    def snapshot(self, items, context = {}):
        """ Generates the snapshot of a site's content 

        @param items: The list of items which the exportation will start.
        @type items: L{Publishable}

        @param context: A dictionary used to share any contextual information
            with the snapshoter.
        @type context: dict
        """
        self.setup(context)

        try:
            for item in items:
                for file_data in self._snapshot(
                    item,
                    context = context
                ):
                    yield file_data
        finally:
            self.cleanup(context)

    @abstractmethod
    def _snapshot(self, root, context = {}):
        """ Generates the snapshot of a site's content 

        @param root: The item which the exportation will statrt.
        @type root: Publishable

        @param context: A dictionary used to share any contextual information
            with the snapshoter.
        @type context: dict
        """

class WgetSnapShoter(StaticSiteSnapShoter):
    """ A class that creates a static snapshot of a site's content using wget """
    instantiable = True

    file_names_mode = schema.String(                                          
        required = True,
        default = "unix",
        text_search = False,
        enumeration = frozenset(("unix", "windows")),
        translate_value = lambda value, **kwargs:    
            u"" if not value else translations(
                "woost.extensions.staticsite.staticsitesnapshoter.WgetSnapShoter.file_names_mode " + value,
                **kwargs
            )
    )

    @getter
    def snapshot_path(self):
        return app.path("snapshots", str(self.id))

    def _get_cmd(self, context):
        cmd = "wget --mirror"

        if not context.get("follow_links"):
            cmd += " --level 1"

        cmd += " --page-requisites --html-extension \
                --convert-links --no-host-directories \
                --no-check-certificate --directory-prefix=%s \
                --restrict-file-names=%s %s"

        return cmd

    def _snapshot(self, root, context = {}):

        cmd = self._get_cmd(context)

        uri = self._get_uri(root, context)

        cmd = cmd % (
            self.snapshot_path, 
            self.file_names_mode, 
            uri
        )

        p = Popen(cmd, shell=True, stdout=PIPE)
        p.communicate()

        for root, dirs, files in os.walk(self.snapshot_path):
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, self.snapshot_path)
                yield (file_path, relative_path)

    def _get_uri(self, item, context):
        location = Location.get_current_host()                              
        location.path_info = controller_context["cms"].uri(item)
        
        return unicode(location).encode("utf-8")

    def cleanup(self, context):
	if os.path.exists(self.snapshot_path):
 	       rmtree(self.snapshot_path)



