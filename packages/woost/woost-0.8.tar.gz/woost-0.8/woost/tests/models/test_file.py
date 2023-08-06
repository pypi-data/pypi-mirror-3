#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2009
"""
import os
from shutil import rmtree
from tempfile import mkdtemp
from woost.tests.models.basetestcase import BaseTestCase


class FileTestCase(BaseTestCase):

    def setUp(self):
        BaseTestCase.setUp(self)
        self.folder = mkdtemp()

    def tearDown(self):
        BaseTestCase.tearDown(self)
        rmtree(self.folder)

    def test_create_file_from_path(self):
        
        from woost.models import File
        from hashlib import md5
        path = os.path.join(self.folder, "foo_bar-spam.css")
        content = """div p {
    color: red;
    font-weight: bold
}"""
        f = open(path, "w")
        f.write(content)
        f.close()

        file = File.from_path(path, self.folder, languages = ["ca", "es"])
        assert isinstance(file, File)

        assert file.file_name == "foo_bar-spam.css"
        assert file.file_size == len(content)
        assert file.file_hash == md5(content).digest() 
        assert file.mime_type == "text/css"
        assert file.get("title", "ca") == "Foo bar spam"
        assert file.get("title", "ca") == "Foo bar spam"

        upload_path = os.path.join(self.folder, str(file.id))
        assert os.path.exists(upload_path)
        assert os.path.exists(path)

        f = open(upload_path, "r")

        try:
            assert f.read() == content
        finally:
            f.close()

