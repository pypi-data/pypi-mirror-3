#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			February 2010
"""
import sys
from threading import Condition
from PyQt4.QtCore import QObject, QUrl, SIGNAL
from PyQt4.QtGui import QApplication, QPrinter
from PyQt4.QtNetwork import QNetworkRequest
from PyQt4.QtWebKit import QWebView
 
def renderpdf(url, dest):

    app = QApplication(sys.argv)
    web = QWebView()

    request = QNetworkRequest(QUrl(url))
    request.setRawHeader("X-Rendering-PDF", "true")
    web.load(request)

    printer = QPrinter()
    printer.setPageSize(QPrinter.A4)
    printer.setOutputFormat(QPrinter.PdfFormat)
    printer.setOutputFileName(dest)

    def print_file():
        web.print_(printer)
        QApplication.exit()

    QObject.connect(web, SIGNAL("loadFinished(bool)"), print_file)
    app.exec_()

def main():

    if len(sys.argv) != 3:
        sys.stderr.write("Usage: %s URL DEST\n" % sys.argv[0])
        sys.exit(1)

    url = sys.argv[1]
    dest = sys.argv[2]
    renderpdf(url, dest)

if __name__ == "__main__":
    main()

