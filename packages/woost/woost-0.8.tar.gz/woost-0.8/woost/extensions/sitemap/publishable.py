#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			February 2010
"""
from decimal import Decimal
from cocktail.translations import translations
from cocktail import schema
from woost.models import Publishable, URI

Publishable.add_member(
    schema.Boolean(
        "sitemap_indexable",
        required = True,
        default = True,
        indexed = True,
        member_group = "sitemap",
        listed_by_default = False
    ),
    append = True
)

URI.default_sitemap_indexable = False

Publishable.add_member(
    schema.String("sitemap_change_frequency",
        enumeration = [
            "always",
            "hourly",
            "daily",
            "weekly",
            "monthly",
            "yearly",
            "never"
        ],
        translate_value = lambda value, language = None, **kwargs:
            "" if not value 
            else translations(
                "woost.extensions.sitemap.change_frequency " + value,
                language,
                **kwargs
            ),
        member_group = "sitemap",
        text_search = False,
        listed_by_default = False
    ),
    append = True
)

Publishable.add_member(
    schema.Decimal("sitemap_priority",
        default = Decimal("0.5"),
        min = 0,
        max = 1,
        listed_by_default = False,
        member_group = "sitemap"
    ),
    append = True
)

