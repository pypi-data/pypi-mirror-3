#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from urllib import urlopen
from httplib import HTTPConnection
from time import mktime, strptime
from cStringIO import StringIO
import Image
from woost.models.uri import URI
from woost.models.rendering.contentrenderer import ContentRenderer
from woost.models.rendering.contentrenderersregistry import content_renderers


class ImageURIRenderer(ContentRenderer):

    def can_render(self, item):
        return isinstance(item, URI) and item.resource_type == "image"

    def get_item_uri(self, item):
        return item.uri

    def render(self, item):
        
        # Open the remote resource
        uri = self.get_item_uri(item)
        http_resource = urlopen(uri)

        # Wrap image data in a buffer
        # (the object returned by urlopen() doesn't support seek(), which is
        # required by PIL)
        buffer = StringIO()
        buffer.write(http_resource.read())
        buffer.seek(0)

        return Image.open(buffer)

    def last_change_in_appearence(self, item):

        uri = self.get_item_uri(item)
        urlparts = urlsplit(uri)
        host = urlparts[1]
        path = urlparts[2] + urlparts[3] + urlparts[4]
        
        http_conn = HTTPConnection(host)
        http_conn.request("HEAD", path)
        http_date = http_conn.getresponse().getheader("last-modified")
        http_conn.close()
        
        if http_date:
            return mktime(strptime(http_date, "%a, %d %b %Y %H:%M:%S %Z"))


content_renderers.register(ImageURIRenderer())

