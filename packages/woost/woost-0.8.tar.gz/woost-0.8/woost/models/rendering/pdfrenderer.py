#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import os
from shutil import rmtree
from tempfile import mkdtemp
from subprocess import Popen, PIPE
from time import time, sleep
import Image
from woost.models.file import File
from woost.models.rendering.contentrenderer import ContentRenderer
from woost.models.rendering.contentrenderersregistry import content_renderers


class PDFRenderer(ContentRenderer):
    """A content renderer that handles pdf files."""

    timeout = 20

    try:
        p = Popen(["which", "convert"], stdout=PIPE)
        convert_path = p.communicate()[0].replace("\n", "") or None
    except:
        convert_path = None

    def can_render(self, item):
        return (
            self.convert_path 
            and isinstance(item, File) 
            and item.resource_type == "document"
            and item.file_name.split(".")[-1].lower() == "pdf"
        )

    def render(self, item, page = 0):

        timeout = self.timeout
        
        # Increase the timeout for bigger files
        size = item.file_size
        if size:
            timeout += size / (10 * 1024 * 1024)

        RESOLUTION = 0.25
        temp_path = mkdtemp()

        try:
            temp_image_file = os.path.join(temp_path, "thumbnail.png")

            command = u'%s -type TrueColor "%s[%d]" %s' % ( 
                self.convert_path, item.file_path, page, temp_image_file
            )

            p = Popen(command, shell=True, stdout=PIPE)
            start = time()

            while p.poll() is None:
                if time() - start > timeout:
                    p.terminate()
                    raise IOError("Timeout was reached")
                sleep(RESOLUTION)

            return Image.open(temp_image_file)

        finally:
            rmtree(temp_path)

    def last_change_in_appearence(self, item):
        return os.stat(item.file_path).st_mtime


content_renderers.register(PDFRenderer())

