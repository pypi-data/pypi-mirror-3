#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""

# Create the default asynchronous file uploader
from cocktail.controllers.asyncupload import AsyncUploader
async_uploader = AsyncUploader()
async_uploader.session_prefix = "woost.async_upload."

