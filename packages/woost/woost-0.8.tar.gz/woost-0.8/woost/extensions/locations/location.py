#-*- coding: utf-8 -*-
u"""Defines the `Location` class.

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.iteration import first
from cocktail.translations import translations
from cocktail import schema
from woost.models import Item
from woost.controllers.backoffice.contentviews import global_content_views


class Location(Item):

    members_order = [
        "location_name",
        "location_type",
        "code",
        "parent",
        "locations"
    ]

    location_name = schema.String(
        translated = True,
        descriptive = True,
        required = True,
        indexed = True,
        normalized_index = True,
        full_text_indexed = True
    )

    location_type = schema.String(
        required = True,
        indexed = True,
        enumeration = [
            "continent",
            "country",
            "autonomous_community",
            "province",
            "town"
        ],
        text_search = False,
        translate_value = lambda value, language = None, **kwargs:
            "" if not value 
            else translations(
                "woost.extensions.locations.location_types." + value,
                language,
                **kwargs
            ),
        edit_control = "cocktail.html.DropdownSelector"
    )

    code = schema.String(
        required = True,
        indexed = True,
        text_search = False
    )

    parent = schema.Reference(
        type = "woost.extensions.locations.location.Location",
        bidirectional = True,
        cycles_allowed = False
    )

    locations = schema.Collection(
        items = "woost.extensions.locations.location.Location",
        bidirectional = True,
        cascade_delete = True
    )

    def descend(self, include_self = False):
        """Iterates over the location's descendants.
        
        :param include_self: If set to True, the location itself is yielded as
            the first element in the iteration.
        :type include_self: bool

        :return: An iterable sequence containing the location's flattened tree.
        :rtype: `Location`
        """
        if include_self:
            yield self
        for location in self.locations:
            for descendant in location.descend(True):
                yield descendant

    def descends_from(self, ascendant):
        """Indicates if the location descends from a given location.

        :param ascendant: The hypothetical container of the location.
        :type ascendant: `Location`

        :return: True if the location is, or is contained within the given
            location or one of its descendants, False otherwise.
        :rtype: bool
        """
        location = self

        while location is not None:
            if location is ascendant:
                return True
            else:
                location = location.parent

        return False

    def get_child_location(self, code):
        """Retrieves the contained location that matches the indicated code.

        :param code: The code of the location to retrieve.
        :type code: str

        :return: The specified location, or None if it wasn't found.
        :rtype: `Location`
        """
        for child in self.locations:
            if child.code == code:
                return child
            for descendant in child.locations:
                match = descendant.get_child_location(code)
                if match:
                    return match

    @classmethod
    def by_code(cls, *code):

        if not code or not code[0]:
            raise ValueError(
                "Location.by_code() requires one or more location codes"
            )

        location = first(cls.select([Location.code.equal(code[0])]))

        for x in code[1:]:
            if location is None:
                return None
            location = location.get_child_location(x)
        
        return location

    def list_level(self, depth):
        
        if depth == 1:
            return self.locations
        else:
            descendants = []
            for location in self.locations:
                descendants.extend(location.list_level(depth - 1))
            return descendants


global_content_views.add(
    Location,
    "woost.views.TreeContentView",
    is_default = True,
    inherited = False,
    params = {
        "children_collection": Location.locations
    }
)

