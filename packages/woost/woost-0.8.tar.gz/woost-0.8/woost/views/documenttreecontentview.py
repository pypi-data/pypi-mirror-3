#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			November 2008
"""
from cocktail.html import templates
from woost.models import Site, Document

TreeContentView = templates.get_class("woost.views.TreeContentView")

class DocumentTreeContentView(TreeContentView):
 
    children_collection = Document.children

    def __init__(self, *args, **kwargs):
        TreeContentView.__init__(self, *args, **kwargs)
        home = Site.main.home
        self.root = [home] if home is not None else []

