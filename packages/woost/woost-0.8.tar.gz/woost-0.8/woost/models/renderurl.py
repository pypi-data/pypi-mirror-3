#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			February 2010
"""
import sys
import os
from optparse import OptionParser
from PyQt4.QtCore import Qt, QObject, QUrl, QSize, SIGNAL
from PyQt4.QtGui import QApplication, QPainter, QPixmap
from PyQt4.QtWebKit import QWebView
 
_formats_by_extension = {
    ".png": "PNG",
    ".bmp": "BMP",
    ".xbm": "XBM",
    ".xpm": "XPM",
    ".jpg": "JPEG",
    ".jpeg": "JPEG",
    ".gif": "GIF"
}

DEFAULT_QUALITY = -1
DEFAULT_MIN_WIDTH = 800
DEFAULT_MIN_HEIGHT = 600

def render_url(url, dest, quality = -1, min_width = 800, min_height = 600):

    format = get_image_format(dest)

    if format is None:
        raise RuntimeError("Can't handle the specified image format")

    app = QApplication(sys.argv)
    web = QWebView()
    web.load(QUrl(url))
 
    def save_image():
        
        try:
            page = web.page()
            frame = page.currentFrame()
            
            # Grow the viewport to make it fit the whole document
            width = min_width
            height = min_height
            
            page.setViewportSize(QSize(width, height))
            
            while frame.scrollBarMaximum(Qt.Horizontal) != 0:
                width += 1
                page.setViewportSize(QSize(width, height))

            while frame.scrollBarMaximum(Qt.Vertical) != 0:
                height += 1
                page.setViewportSize(QSize(width, height))

            # Render the document to an image file
            image = QPixmap(width, height)
            painter = QPainter()
            painter.begin(image)
            frame.render(painter)
            painter.end()        
            image.save(dest, format, quality)

        finally:
            QApplication.exit()

    QObject.connect(web, SIGNAL("loadFinished(bool)"), save_image)
    app.exec_()

def get_image_format(file_name):
    return _formats_by_extension.get(os.path.splitext(file_name)[1])

def main():

    parser = OptionParser()

    parser.add_option("--quality",
        help = u"The quality for the image")
    
    parser.add_option("--min-width",
        help = u"The minimum width for the viewport")
    
    parser.add_option("--min-height",
        help = u"The minimum height for the viewport")
    
    options, args = parser.parse_args()

    if len(args) != 2:
        sys.stderr.write("Usage: %s URL DEST\n" % sys.argv[0])
        sys.exit(1)

    kwargs = {}

    if options.quality:
        kwargs["quality"] = int(options.quality)

    if options.min_width:
        kwargs["min_width"] = int(options.min_width)

    if options.min_height:
        kwargs["min_height"] = int(options.min_height)

    render_url(*args, **kwargs)

if __name__ == "__main__":
    main()

