#-*- coding: utf-8 -*-
u"""

@var extensions: A dictionary mapping extensions to MIME types.
@var extensions: dict(str, str)

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
import os
import hashlib
from mimetypes import guess_type
from shutil import copy
from cocktail.events import event_handler
from cocktail.memoryutils import format_bytes
from cocktail import schema
from cocktail.persistence import datastore
from woost import app
from woost.models.publishable import Publishable
from woost.models.controller import Controller
from woost.models.language import Language


class File(Publishable):
 
    instantiable = True

    edit_view = "woost.views.FileFieldsView"
    edit_node_class = \
        "woost.controllers.backoffice.fileeditnode.FileEditNode"

    default_mime_type = None

    default_encoding = None

    default_controller = schema.DynamicDefault(
        lambda: Controller.get_instance(qname = "woost.file_controller")
    )

    members_order = [
        "title",
        "file_name",
        "file_size",
        "file_hash",
        "local_path",
        "image_effects"
    ]

    title = schema.String(
        indexed = True,
        normalized_index = True,
        full_text_indexed = True,
        descriptive = True,
        translated = True,
        member_group = "content"
    )
    
    file_name = schema.String(
        required = True,
        editable = False,
        member_group = "content"
    )

    file_size = schema.Integer(
        required = True,
        editable = False,
        translate_value = lambda size, language = None, **kwargs:
            "" if size in (None, "") else format_bytes(size),
        min = 0,
        member_group = "content"
    )

    file_hash = schema.String(
        visible = False,
        searchable = False,
        text_search = False,
        member_group = "content"
    )

    local_path = schema.String(
        listed_by_default = False,
        text_search = False,
        member_group = "content"
    )
    
    image_effects = schema.String(
        listed_by_default = False,
        searchable = False,
        member_group = "content",
        edit_control = "woost.views.ImageEffectsEditor"
    )

    @property
    def file_extension(self):
        return os.path.splitext(self.file_name)[1]

    @event_handler
    def handle_changed(cls, e):

        if e.member is cls.local_path and e.value:
            file = e.source
            file.file_name = os.path.basename(e.value)
            file.mime_type = guess_type(e.value, strict = True)[0]
            file.file_hash = None
            file.file_size = None

    @property
    def file_path(self):

        file_path = self.local_path

        if file_path:
            if not os.path.isabs(file_path):
                file_path = app.path(file_path)            
        else:            
            file_path = app.path("upload", str(self.id))

        return file_path

    @classmethod
    def from_path(cls,
        path,
        dest = None,
        languages = None,
        hash = None,
        encoding = "utf-8"):
        """Imports a file into the site.
        
        @param path: The path to the file that should be imported.
        @type path: str

        @param dest: The base path where the file should be copied (should match
            the upload folder for the application).
        @type dest: str

        @param languages: The set of languages that the created file will be
            translated into.
        @type languages: str set
       
        @return: The created file.
        @rtype: L{File}
        """
        
        # The default behavior is to translate created files into all the languages
        # defined by the site
        if languages is None:
            languages = Language.codes

        file_name = os.path.split(path)[1]
        title, ext = os.path.splitext(file_name)
        
        if encoding:
            if isinstance(title, str):
                title = title.decode(encoding)
            if isinstance(file_name, str):
                file_name = file_name.decode(encoding)

        title = title.replace("_", " ").replace("-", " ")
        title = title[0].upper() + title[1:]

        file = cls()
        
        file.file_size = os.stat(path).st_size
        file.file_hash = hash or file_hash(path)
        file.file_name = file_name

        # Infer the file's MIME type
        mime_type = guess_type(file_name, strict = False)
        if mime_type:
            file.mime_type = mime_type[0]
        
        for language in languages:
            file.set("title", title, language)

        if dest is None:
            upload_path = file.file_path
        else:
            upload_path = os.path.join(dest, str(file.id))

        copy(path, upload_path)

        return file

    def make_draft(self):
        draft = Publishable.make_draft(self)

        trans = datastore.connection.transaction_manager.get()

        def copy_file(successful, source, destination):
            if successful:
                copy(source, destination)

        trans.addAfterCommitHook(
            copy_file,
            (self.file_path, draft.file_path)
        )

        return draft

    def confirm_draft(self):
        trans = datastore.connection.transaction_manager.get()

        if self.draft_source:
            def copy_file(successful, source, destination):
                if successful:
                    copy(source, destination)

            trans.addAfterCommitHook(
                copy_file,
                (self.file_path, self.draft_source.file_path)
            )

        Publishable.confirm_draft(self)

    @classmethod
    def _should_exclude_in_draft(cls, member):
        return member.name not in (
            "file_name", "file_size", "file_hash", "mime_type"
        ) and (not member.editable or not member.visible)

def file_hash(source, algorithm = "md5", chunk_size = 1024):
    """Obtains a hash for the contents of the given file.

    @param source: The file to obtain the hash for. Can be given as a file
        system path, or as a reference to a file like object.
    @type source: str or file like object

    @param algorithm: The hashing algorithm to use. Takes the same values as
        L{hashlib.new}.
    @type algorithm: str

    @param chunk_size: The size of the file chunks to read from the source, in
        bytes.
    @type chunk_size: int

    @return: The resulting file hash, in binary form.
    @rtype: str
    """
    hash = hashlib.new(algorithm)

    if isinstance(source, basestring):
        should_close = True
        source = open(source, "r")
    else:
        should_close = False

    try:
        while True:
            chunk = source.read(chunk_size)
            if not chunk:
                break
            hash.update(chunk)
    finally:
        if should_close:
            source.close()

    return hash.digest()

