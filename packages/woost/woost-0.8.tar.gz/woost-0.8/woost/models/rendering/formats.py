#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""

default_format = "JPEG"

# Mappings between MIME types and PIL formats
formats_by_mime_type = {
    "image/jpeg": "JPEG",
    "image/pjpeg": "JPEG",
    "image/png": "PNG",
    "image/x-png": "PNG",
    "image/gif": "GIF",
    "image/tiff": "TIFF"
}

mime_types_by_format = dict(
    (v, k)
    for k, v in formats_by_mime_type.iteritems()
)

formats_by_extension = {
    "jpg": "JPEG",
    "jpeg": "JPEG",
    "png": "PNG",
    "gif": "GIF",
    "tiff": "TIFF"
}

extensions_by_format = dict(
    (v, k)
    for k, v in formats_by_extension.iteritems()
)

