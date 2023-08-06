#!/usr/bin/env python
#-*- coding: utf-8 -*-
u"""
Initializes the site's database.

*******************************************************************************
WARNING: this will clear all existing data, so use with care!
*******************************************************************************

The site's initialization is run automatically by the site installer, so
calling this script manually should seldomly be necessary. That said, it can be
useful during development (ie. to setup working copies from version control, or
to reset a site's state after some changes).
"""

# Load project settings
import _PROJECT_MODULE_
    
from woost.models.initialization import main

if __name__ == "__main__":
    main()

