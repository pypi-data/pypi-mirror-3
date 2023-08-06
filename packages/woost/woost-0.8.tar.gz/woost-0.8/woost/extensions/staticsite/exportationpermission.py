#-*- coding: utf-8 -*-
"""

@author:		Jordi Fernández
@contact:		jordi.fernandez@whads.com
@organization:	Whads/Accent SL
@since:			March 2010
"""
from cocktail.translations import translations
from cocktail import schema
from cocktail.html import templates
from woost.models.messagestyles import permission_doesnt_match_style
from woost.models.permission import Permission


class ExportationPermission(Permission):
    """Permission to execute a site's exportation to a destination."""

    instantiable = True

    def _destination_edit_control(parent, obj, member):
        display = templates.new("cocktail.html.DropdownSelector")
        display.empty_label = translations(
            "woost.extensions.staticsite any destination"
        )
        return display

    destination = schema.Reference(
        type = "woost.extensions.staticsite.staticsitedestination.StaticSiteDestination",
        related_key = "destination_permissions",
        bidirectional = True,
        edit_control = _destination_edit_control
    )

    del _destination_edit_control

    def match(self, destination, verbose = False):
        
        if self.destination and destination is not self.destination:
            print permission_doesnt_match_style("destination doesn't match")
            return False

        return Permission.match(self, verbose)

