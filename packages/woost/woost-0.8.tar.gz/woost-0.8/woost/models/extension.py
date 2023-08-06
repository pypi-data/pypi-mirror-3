#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			December 2008
"""
from pkg_resources import iter_entry_points
from threading import RLock
from ZODB.POSException import ConflictError
from cocktail.iteration import first
from cocktail.modeling import classgetter
from cocktail.events import Event, event_handler
from cocktail.pkgutils import resolve
from cocktail.translations import translations
from cocktail import schema
from cocktail.persistence import datastore, transaction
from woost.models.item import Item
from woost.models.language import Language

extension_translations = object()
_loaded_extensions = set()
_extensions_lock = RLock()

def load_extensions():
    """Load all available extensions.
    
    This is tipically called during application start up, and follows this
    sequence:

        * New available extensions are installed
        * Previously installed exceptions that are no longer available are
          uninstalled
        * All installed and enabled extensions are initialized
    """
    with _extensions_lock:

        for entry_point in iter_entry_points("woost.extensions"):

            extension_type = entry_point.load()
            extension = extension_type.instance

            # Create an instance of each new extension
            if extension is None:
                def create_extension_instance():
                    extension = extension_type()
                    extension.insert()

                transaction(
                    create_extension_instance,
                    max_attempts = 5,
                    desist = lambda: extension_type.instance is not None
                )

            # Load enabled extensions
            elif extension.enabled:
                extension.load()


class Extension(Item):
    """Base model for Woost extensions."""

    instantiable = False
    collapsed_backoffice_menu = True
    edit_node_class = "woost.controllers.backoffice.extensioneditnode." \
                      "ExtensionEditNode"

    installed = False
    
    @property
    def loaded(self):
        return self.__class__ in _loaded_extensions

    member_order = (
        "extension_author",
        "license",
        "web_page",
        "description",
        "enabled"
    )

    extension_author = schema.String(
        editable = False,
        listed_by_default = False
    )

    license = schema.String(
        editable = False,
        listed_by_default = False
    )

    web_page = schema.String(
        editable = False
    )

    description = schema.String(
        editable = False,
        translated = True
    )

    enabled = schema.Boolean(
        required = True,
        default = False
    )
 
    loading = Event("""An event triggered during application start up.""")

    installing = Event(
        """An event triggered when an extension creates its assets, the first
        time it is loaded.
        """
    )

    @classgetter
    def instance(cls):
        return first(cls.select())

    def __translate__(self, language, **kwargs):
        return translations(self.__class__.name)

    def load(self):
        with _extensions_lock:
            if self.__class__ not in _loaded_extensions:
                _loaded_extensions.add(self.__class__)
                self._load()
                self.loading()

    def _load(self):
        pass

    def install(self):
        if not self.installed:
            def install_extension():
                self._install()
                self.installing()
                self.installed = True
            
            transaction(install_extension, desist = lambda: self.installed)

    def _install(self):
        pass

    def _create_asset(self, cls, id, **values):
        """Convenience method for creating content when installing an
        extension.        
        """
        asset = cls()
        cls.qname = qname = self.full_name.rsplit(".", 1)[0] + "." + id
        
        if values:
            for key, value in values.iteritems():
                if value is extension_translations:
                    for language in Language.codes:
                        value = translations(qname + "." + key, language)
                        if value:
                            asset.set(key, value, language)
                else:
                    asset.set(key, value)

        asset.insert()
        return asset

