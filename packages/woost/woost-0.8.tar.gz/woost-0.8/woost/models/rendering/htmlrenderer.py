#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import os
import Image
from tempfile import mkdtemp
from shutil import rmtree
from subprocess import Popen
from woost.models.publishable import Publishable
from woost.models.user import User
from woost.models.rendering.contentrenderer import ContentRenderer
from woost.models.rendering.contentrenderersregistry import content_renderers


class HTMLRenderer(ContentRenderer):
    """A content renderer that handles XHTML/HTML pages."""

    enabled = False

    mime_types = set([
        "text/html",
        "text/xhtml",
        "application/xhtml"
    ])

    def can_render(self, item):
        return (
            isinstance(item, Publishable)
            and item.mime_type in self.mime_types            
            and item.is_accessible(
                user = User.get_instance(qname = "woost.anonymous_user")
            )
        )

    def render(self, item, window_width = None, window_height = None):

        temp_path = mkdtemp()

        try:
            temp_image_file = os.path.join(temp_path, "thumbnail.png")
            
            command = "python -m woost.models.rendering.renderurl %s %s" \
                % (item.get_uri(host = "."), temp_image_file)
            
            if window_width is not None:
                command += " --min-width %d" % window_width
            
            if window_height is not None:
                command += " --min-width %d" % window_height 

            Popen(command, shell = True).wait()
            return Image.open(temp_image_file)

        finally:
            rmtree(temp_path)


try:
    import PyQt4.QtWebKit
except ImportError:
    pass
else:
    content_renderers.register(HTMLRenderer())

