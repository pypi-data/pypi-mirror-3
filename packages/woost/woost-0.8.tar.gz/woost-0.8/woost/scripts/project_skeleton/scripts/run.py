#!/usr/bin/env python
#-*- coding: utf-8 -*-
u"""
Launches the site's application server.
"""
from woost.models.extension import load_extensions
import _PROJECT_MODULE_.models
import _PROJECT_MODULE_.views
from _PROJECT_MODULE_.controllers import _PROJECT_NAME_CMSController

def main():
    load_extensions()
    cms = _PROJECT_NAME_CMSController()
    cms.run()

if __name__ == "__main__":
    main()

