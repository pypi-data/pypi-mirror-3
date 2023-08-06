#-*- coding: utf-8 -*-
u"""

@author:        Jordi Fernández
@contact:       jordi.fernandez@whads.com
@organization:  Whads/Accent SL
@since:         March 2010
"""
from __future__ import with_statement
import os
import ftplib
from shutil import copy
from datetime import date
from tempfile import mkstemp
from zipfile import ZipFile
from cocktail import schema
from cocktail.events import EventHub, Event
from cocktail.modeling import abstractmethod
from cocktail.translations import get_language
from cocktail.persistence import PersistentMapping
from cocktail.controllers import context as controller_context
from woost import app
from woost.models import Item, File, get_current_user
from woost.models.file import file_hash
from woost.models.changesets import changeset_context


class StaticSiteDestination(Item):
    """A class tasked with publishing a static snapshot of a site's content to
    a concrete location.
    
    This is mostly an abstract class, meant to be extended by subclasses. Each
    subclass should implement exporting to a concrete kind of location or
    media. Subclasses must implement L{write_file} and L{create_folder}, and
    probably L{setup}.

    @var chunk_size: The number of bytes written at once by L{write_file}.
    @type chunk_size: int
    """
    instantiable = False
    visible_from_root = False
    chunk_size = 1024 * 8

    destination_permissions = schema.Collection(
        items = "woost.extensions.staticsite.exportationpermission."
                "ExportationPermission",
        related_key = "destination",
        bidirectional = True
    )

    encoding = schema.String(
        required = True,
        default = "utf-8",
        text_search = False
    )


    def __init__(self, *args, **kwargs):
        Item.__init__(self, *args, **kwargs)
        self.__last_export_hashes = PersistentMapping()

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

    def _export(
        self,
        context,
        status_tracker = None
    ):
        if status_tracker:
            status_tracker.beginning(
                context = context
            )

        for file, file_path in context["snapshoter"].snapshot(
            context["selection"], 
            context = context
        ):
            exported = None

            try:
                exported = self.export_file(
                    file, 
                    file_path, 
                    context
                )
            except Exception, error:

                handled = False

                if status_tracker:
                    e = status_tracker.file_processed(
                        file = file_path,
                        status = "failed",
                        context = context,
                        error = error,
                        error_handled = False
                    )
                    handled = e.error_handled

                if not handled:
                    raise

            else:
                if status_tracker:
                    status_tracker.file_processed(
                        file = file_path,
                        status = "exported" if exported else "not_modified",
                        context = context,
                        error = None,
                        error_handled = False
                    )

    def export(
        self,
        snapshoter,
        selection,
        update_only = False,
        status_tracker = None,
        context = {}
    ):
        """Exports site snapshot to this destination.

        @param snapshoter: The snapshoter used by the exporter during the export
            process.
        @type snapshoter: StaticSiteSnapShoter

        @param update_only: When set to True, items will only be exported if
            they have pending changes that have not been exported to this
            destination yet.
        @type update_only: bool

        @param status_tracker: An object to report events to during the export
            process.
        @type status_tracker: L{StatusTracker}

        @param context: A dictionary used to share any contextual information
            with the exporter.
        @type context: dict
        
        @return: The dictionary used by the exporter during the export
            process to maintain its contextual information.
        @rtype: dict
        """

        controller_context["exporting_static_site"] = True
        context["existing_folders"] = set()
        context.update(
            snapshoter = snapshoter,
            selection = selection,
            update_only = update_only
        )
        self.setup(context)

        try:
            self._export(
                context,
                status_tracker = status_tracker
            )
        finally:
            del controller_context["exporting_static_site"]
            self.cleanup(context)

        return context

    def export_file(self,
        file,
        file_path,
        context):
        """Exports a file.
        
        @param file: The file's contents file to export. Can be specified using 
            a file-like object, or a filesystem path.
        @type file: file-like or str

        @param file_path: The file path, relative to the destination's root.
        @type file_path: str

        @param context: A dictionary where the exporter can place any
            contextual information it many need throgout the export process. It
            will be made available to all L{write_file} calls.
        @type context: dict

        @return: True if the item is exported, False if L{update_only} is set
            to True and the item has no changes to export.
        @rtype: bool
        """

        update_only = context.get("update_only")
        hash = file_hash(file)

        if update_only \
        and hash == self.__last_export_hashes.get(file_path):
            return False

        folder, filename = os.path.split(file_path)

        self.create_path(folder, context)
        self.write_file(file, file_path, context)
        self.__last_export_hashes[file_path] = hash
        return True


    def create_path(self, relative_path, context):
        """Recursively creates all folders in the given path.

        The method will invoke L{create_folder} for each folder in the provided
        path.

        @param relative_path: The path to create, relative to the destination's
            root.
        @type relative_path: unicode

        @param context: The dictionary used by the exporter to maintain any
            contextual information it many need throgout the export process.
        
            If a context is provided and it contains an 'existing_folders' key,
            it should be a set of strings representing paths that are known to
            be present at the destination. If given, folders in the set will be
            skipped, and those that are created will be added to the set. This
            mechanism can be useful when calling this method repeatedly, to
            avoid unnecessary calls to L{create_folder}.
        @type existing_folders: unicode set
        """
        existing_folders = context.get("existing_folders")

        def ascend(folder):
            if folder and \
            (existing_folders is None or folder not in existing_folders):
                ascend(os.path.dirname(folder))
                created = self.create_folder(folder, context)
                if existing_folders and created:
                    existing_folders.add(folder)

        ascend(relative_path)

    @abstractmethod
    def create_folder(self, relative_path, context):
        """Creates a folder on the destination, if it doesn't exist yet.

        @param relative_path: The path of the folder to create, relative to the
            destination's root.
        @type relative_path: unicode

        @param context: The dictionary used by the exporter to maintain any
            contextual information it many need throgout the export process.
        @type context: dict

        @return: True if the folder didn't exist, and was created, False if it
            already existed.
        @rtype: bool
        """

    @abstractmethod
    def write_file(self, file, path, context):
        """Writes a file to the destination.

        @param file: The file to write. Can be a given as a path to a local
            file, or as a file-like object.
        @type file: str or file-like object

        @param path: The relative path within the exporter's designated
            destination where the file should be written. Must include the
            file's name (and extension, if any).
        @type path: str

        @param context: A dictionary used by the exporter to maintain
            contextual information across its operations (ie. an open
            connection to an FTP server, an instance of a ZipFile class, etc).
        @type context: dict
        """

    def view_class(self):
        return "woost.extensions.staticsite.ExportStaticSiteView"

    def output(self):
        return {}


class StatusTracker(object):
    """An object that allows clients to be kept up to date of the progress of
    an L{export operation<StaticSiteDestination.export>}.
    """
    __metaclass__ = EventHub

    beginning = Event(
        """An event triggered after an exporter has finished its preparations
        and is ready to start the export operation.
        
        @ivar context: The L{context<StaticSiteDestination.setup.context>}
            used by the export operation to maintain its state.
        @type context: dict
        """)

    file_processed = Event(
        """An event triggered after file has been processed.

        This event will be triggered at least once for each generated file on
        the exportation process. 

        The event will be triggered regardless of the outcome of the exporting
        process, and even if the item is discarded and not exported. Clients
        can differentiate between these cases using the L{status} attribute.

        @ivar file: The generated file path.
        @type file: str

        @ivar status: The status for the processed file. Will be one of the
            following:
                - ignored: The file is not published or marked as not able
                  to be exported, and has been skipped.
                - not-modified: The file hasn't been modified since the last
                  time it was exported, and the operation has been flagged as
                  "L{update only<StaticSiteDestination.export.update_only>}".
                - exported: The file has been correctly exported.
                - failed: The export attempt raised an exception.
        @type status: str

        @ivar error: Only relevant if L{status} is 'failed'. A reference
            to the exception raised while trying to export the item.
        @type error: L{Exception}

        @ivar error_handled: Only relevant if L{status} is 'failed'. Allows
            the event response code to capture an export error. If set to True,
            the exporter will continue 
        @type error_handled: bool

        @ivar context: The L{context<StaticSiteDestination.setup.context>}
            used by the export operation to maintain its state.
        @type context: dict
        """)


class FolderDestination(StaticSiteDestination):
    """A class that exports a static snapshot of a site's content to a local
    folder.
    """
    instantiable = True
    
    target_folder = schema.String(
        required = True,
        unique = True,
        descriptive = True,
        text_search = False
    )

    def create_folder(self, folder, context):
        full_path = os.path.join(self.target_folder, folder)
        if not os.path.exists(full_path):
            os.mkdir(full_path)
            return True

        return False

    def write_file(self, file, path, context):

        full_path = os.path.join(self.target_folder, path)

        # Copy local files
        if isinstance(file, basestring):
            copy(file, full_path)
        
        # Save data from file-like objects
        else:
            target_file = open(full_path, "wb")
            try:
                while True:
                    chunk = file.read(self.chunk_size)
                    if not chunk:
                        break
                    target_file.write(chunk)
            finally:
                target_file.close()


class FTPDestination(StaticSiteDestination):
    """A class that exports a static snapshot of a site's content to an FTP
    server.
    """
    instantiable = True

    members_order = [
        "ftp_host",
        "ftp_user",
        "ftp_password",
        "ftp_path"
    ]

    ftp_host = schema.String(
        required = True,
        text_search = False
    )

    ftp_user = schema.String(
        text_search = False
    )

    ftp_password = schema.String(
        edit_control = "cocktail.html.PasswordBox",
        text_search = False
    )

    ftp_path = schema.String(
        text_search = False
    )

    def __translate__(self, language, **kwargs):

        if self.draft_source is None:
            
            desc = self.ftp_host
            if desc:
                
                user = self.ftp_user
                if user:
                    desc = user + "@" + desc
                
                path = self.ftp_path
                if path:
                    if not path[0] == "/":
                        path = "/" + path
                    desc += path

                return "ftp://" + desc
                
        return StaticSiteDestination.__translate__(self, language, **kwargs)

    def setup(self, context):
        context["ftp"] = ftplib.FTP(
            self.ftp_host,
            self.ftp_user,
            self.ftp_password
        )

    def cleanup(self, context):
        context["ftp"].quit()

    def write_file(self, file, path, context):
        
        ftp = context["ftp"]
        path = self._get_ftp_path(path)

        # Remove existing files
        try:
            ftp.delete(path)
        except ftplib.error_perm:
            pass
        
        # Handle both local files and file-like objects
        if isinstance(file, basestring):
            file = open(file, "r")
            should_close = True
        else:
            should_close = False
            
        try:
            ftp.storbinary("STOR " + path, file, self.chunk_size)
        finally:
            if should_close:
                file.close()
        
    def create_folder(self, folder, context):
        
        ftp = context["ftp"]
        path = self._get_ftp_path(folder)

        if not self._path_exists(ftp, path):
            ftp.mkd(path)
            return True

        return False

    def _get_ftp_path(self, *args):

        path = self.ftp_path

        if not path:
            path = "/"
        elif path[-1] != "/":
            path += "/"

        path = path + "/".join(arg.strip("/") for arg in args)
        
        try:
            return path.encode(self.encoding)
        except UnicodeEncodeError:
            return path

    def _path_exists(self, ftp, path):

        path = path.rstrip("/")

        if not path:
            return True        
        
        pos = path.rfind("/")
        
        if pos == -1:
            parent = "."
            name = path
        else:
            parent = path[:pos]
            name = path[pos + 1:]

        if not parent.endswith("/"):
            parent = parent + "/" 

        return (parent + name) in ftp.nlst(parent)


class ZipDestination(StaticSiteDestination):
    """A class that exports a static snapshot of a site's content to a ZIP
    file.
    """
    instantiable = True


    def setup(self, context):
        handle, context["temp_file"] = mkstemp('.zip')
        os.close(handle)
        context["zip_file"] = ZipFile(context["temp_file"], 'w')

    def cleanup(self, context):
        os.unlink(context["temp_file"])

    def _export(
        self,
        context,
        status_tracker = None
    ):
        StaticSiteDestination._export(
            self,
            context,
            status_tracker = status_tracker
        )

        # Close the zip file before export it to the CMS
        context["zip_file"].close()        
        upload_path = app.path("upload")

        with changeset_context(get_current_user()):
            file = File.from_path(
                context["temp_file"], 
                upload_path, 
                languages = [get_language()]
            )
            file.title = "export-%s" % date.today().strftime("%Y%m%d")
            file.file_name = file.title + ".zip"
            file.insert()
            context.update(file = file)

    def create_folder(self, folder, context):
        return True

    def write_file(self, file, path, context):

        if isinstance(file, basestring):
            context["zip_file"].write(file, path)
        else:
            try:
                context["zip_file"].writestr(path, file.read())
            finally:
                file.close()

    def view_class(self, context):
        return "woost.extensions.staticsite.ExportStaticSiteZipView"

    def output(self, context):
        output = StaticSiteDestination.output(self)
        output.update(
            file = context["file"]
        )
        return output

