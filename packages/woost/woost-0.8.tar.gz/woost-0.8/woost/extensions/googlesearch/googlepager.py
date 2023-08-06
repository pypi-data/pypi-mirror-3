#-*- coding: utf-8 -*-
"""

@author:		Marc Pérez
@contact:		marc.perez@whads.com
@organization:	Whads/Accent SL
@since:			December 2009
"""

from cocktail.translations import translations

from cocktail.html.pager import Pager
from cocktail.html import Element

class GooglePager(Pager):

    def create_button(self, name):
        button = Element("a")
        button.add_class(name)
        if name == "next":
            button.append(translations("googlesearch next"))
        if name == "previous":
            button.append(translations("googlesearch previous"))
        return button


