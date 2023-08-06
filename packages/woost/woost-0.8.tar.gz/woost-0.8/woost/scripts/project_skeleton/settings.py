#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""

from woost import app
app.package = "_PROJECT_MODULE_"

# Application server configuration
import cherrypy
cherrypy.config.update({
    "global": {
        "server.socket_host": "_WEBSERVER_HOST_",
        "server.socket_port": _WEBSERVER_PORT_,
        "tools.encode.on": True,
        "tools.encode.encoding": "utf-8",
        "tools.decode.on": True,
        "tools.decode.encoding": 'utf-8'
    }
})

# Object store provider
from cocktail.persistence import datastore
from ZEO.ClientStorage import ClientStorage
db_host = "_DATABASE_HOST_"
db_port = _DATABASE_PORT_
datastore.storage = lambda: ClientStorage((db_host, db_port))

# Use file based sessions
from cocktail.controllers import session
session.config["session.type"] = "file"

# Uncomment the code below to enable the interactive debugger
# WARNING: *THE CODE BELOW MUST BE COMMENTED ON A PRODUCTION ENVIRONMENT*
#from paste import evalexception
#from _PROJECT_MODULE_.controllers import _PROJECT_NAME_CMS
#
#cherrypy.config.update({
#    "global": {
#        "request.throw_errors": True,
#    }   
#})  
#
#_PROJECT_NAME_CMS.application_settings = { 
#    "/": {
#        "wsgi.pipeline": (('evalexc', evalexception.EvalException),),
#        "wsgi.evalexc.global_conf": {}, 
#        "wsgi.evalexc.xmlhttp_key": "_xml",
#    }   
#}   

