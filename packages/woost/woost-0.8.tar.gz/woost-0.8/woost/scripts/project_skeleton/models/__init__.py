#-*- coding: utf-8 -*-
u"""
Site specific models.
"""
from woost.models import Template
Template.engine.default = "_TEMPLATE_ENGINE_"
del Template

from _PROJECT_MODULE_.models import migration

