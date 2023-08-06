#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import cherrypy
import os
from tempfile import mkdtemp
from zipfile import ZipFile
from shutil import copyfileobj
from cocktail.modeling import cached_getter
from cocktail import schema
from cocktail.persistence import datastore
from cocktail.controllers import get_parameter
from cocktail.controllers.fileupload import FileUpload
from woost.models import (
    get_current_user, 
    changeset_context,
    File
)
from woost.controllers.backoffice.basebackofficecontroller \
    import BaseBackOfficeController


class UploadFilesController(BaseBackOfficeController):

    view_class = "woost.views.BackOfficeUploadFilesView"
    imported_files = None

    @cached_getter
    def form_schema(self):

        form_schema = schema.Schema("UploadFilesForm")
        
        upload = FileUpload("upload", required = True)
        upload["mime_type"].enumeration = [
            "application/zip",
            "application/x-zip-compressed"
        ]
        form_schema.add_member(upload)

        return form_schema

    @cached_getter
    def form_data(self):
        return get_parameter(self.form_schema, errors = "ignore")

    @cached_getter
    def form_errors(self):
        return schema.ErrorList(
            self.form_schema.get_errors(self.form_data)
                if self.submitted
                else []
        )

    @cached_getter
    def valid(self):
        return not self.form_errors

    @cached_getter
    def submitted(self):
        return cherrypy.request.method == "POST"
    
    def submit(self):
        
        self.imported_files = []
        
        file = self.form_data["upload"]["file"]
        zip_file = ZipFile(file)
        
        upload_path = self.context["cms"].upload_path
        temp_dir = mkdtemp()

        try:
            with changeset_context(get_current_user()):
                for file_path in zip_file.namelist():

                    file_name = os.path.basename(file_path)
                    
                    # Skip directories
                    if not file_name:
                        continue

                    source = zip_file.open(file_path)
                    temp_file = os.path.join(temp_dir, file_name)
                    dest = open(temp_file, "wb")
                    copyfileobj(source, dest)
                    source.close()
                    dest.close()

                    try:
                        imported_file = File.from_path(
                            temp_file,
                            upload_path
                        )
                        imported_file.insert()
                        self.imported_files.append(imported_file)
                    finally:
                        os.remove(temp_file)

            datastore.commit()
        finally:
            os.rmdir(temp_dir)

    @cached_getter
    def output(self):
        output = BaseBackOfficeController.output(self)
        output.update(
            form_data = self.form_data,
            form_schema = self.form_schema,
            form_errors = self.form_errors,
            imported_files = self.imported_files
        )
        return output

