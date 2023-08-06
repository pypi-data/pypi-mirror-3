#-*- coding: utf-8 -*-
import cherrypy
from woost.models.extension import load_extensions
import _PROJECT_MODULE_.models
import _PROJECT_MODULE_.views
from _PROJECT_MODULE_.controllers import _PROJECT_NAME_CMS

load_extensions()
cms = _PROJECT_NAME_CMS()
application = cms.mount()

