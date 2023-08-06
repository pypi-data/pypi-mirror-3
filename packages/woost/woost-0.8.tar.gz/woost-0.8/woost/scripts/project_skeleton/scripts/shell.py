#!/usr/bin/env python
#-*- coding: utf-8 -*-
u"""A convenience script that can be launched through ipython or vanilla python
with the -i flag, to have quick access to the project's data.
"""
from __future__ import with_statement
from cocktail.translations import *
from cocktail.persistence import *
from woost import app
from woost.models import *
from woost.models.extension import load_extensions
from _PROJECT_MODULE_.models import *

site = Site.main

DEFAULT_LANGUAGE = site.default_language
set_language(DEFAULT_LANGUAGE)
load_extensions()

