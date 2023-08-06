#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			January 2010
"""
import cherrypy
from woost.models import Style
from woost.controllers.publishablecontroller import PublishableController 


class StylesController(PublishableController):

    def _produce_content(self, backoffice = False):
        
        for style in Style.select():
            declarations = (backoffice and style.admin_declarations) or style.declarations
            yield ".%s{\n%s\n}\n" % (style.class_name, declarations)

