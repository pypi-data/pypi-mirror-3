#-*- coding: utf-8 -*-
u"""Migration of the site's schema.

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.persistence import MigrationStep


if __name__ == "__main__":
    import _PROJECT_NAME_
    from cocktail.persistence import migrate
    migrate()

