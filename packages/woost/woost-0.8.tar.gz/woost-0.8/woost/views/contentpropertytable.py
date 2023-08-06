#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			February 2009
"""
from cocktail.html import templates
from woost.views.contentdisplaymixin import ContentDisplayMixin

PropertyTable = templates.get_class("cocktail.html.PropertyTable")


class ContentPropertyTable(ContentDisplayMixin, PropertyTable):

    def __init__(self, *args, **kwargs):
        PropertyTable.__init__(self, *args, **kwargs)
        ContentDisplayMixin.__init__(self)

