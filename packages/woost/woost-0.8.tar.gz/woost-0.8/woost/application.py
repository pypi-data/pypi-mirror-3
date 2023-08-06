#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import os
from pkg_resources import resource_filename


class Application(object):
    
    __root = None
    __icon_resolver = None

    def path(self, *args):
        return os.path.join(self.root, *args)

    def _get_package(self):
        return self.__package

    def _set_package(self, package):
        self.__package = package
        self.root = resource_filename(package, "")

    package = property(_get_package, _set_package)

    def _get_root(self):
        return self.__root

    def _set_root(self, root):
        
        if self.__root:            
            try:
                self.icon_resolver.icon_repositories.remove(
                    self.path("views", "resources", "images", "icons")
                )
            except:
                pass

        self.__root = root

        if root:
            # Add an application specific icon repository
            self.icon_resolver.icon_repositories.insert(
                0, self.path("views", "resources", "images", "icons")
            )

    root = property(_get_root, _set_root)

    @property
    def icon_resolver(self):
        if self.__icon_resolver is None:
            from woost.iconresolver import IconResolver
            self.__icon_resolver = IconResolver()
        return self.__icon_resolver

