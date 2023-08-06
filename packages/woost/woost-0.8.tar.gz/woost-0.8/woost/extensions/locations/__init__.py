#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from time import time
from simplejson import loads
from urllib import urlopen
from cocktail.iteration import first
from cocktail.translations import translations
from cocktail import schema
from cocktail.persistence import transaction
from woost.models import Extension

translations.define("LocationsExtension",
    ca = u"Localitats",
    es = u"Localidad",
    en = u"Locations"
)

translations.define("LocationsExtension.service_uri",
    ca = u"URL del repositori de dades",
    es = u"URL del repositorio de datos",
    en = u"URL of the data repository"
)

translations.define("LocationsExtension.update_frequency",
    ca = u"Freqüència d'actualització",
    es = u"Frecuencia de actualización",
    en = u"Update frequency"
)

translations.define("LocationsExtension.update_frequency-explanation",
    ca = u"El nombre de dies entre actualitzacions de la llista de localitats."
         u" Deixar en blanc per desactivar les actualitzacions.",
    es = u"El número de días entre actualizaciones de la lista de localidades."
         u" Dejar en blanco para desactivar las actualizaciones.",
    en = u"Number of days between updates to the list of locations. "
         u"Leave blank to disable updates."
)

translations.define("LocationsExtension.updated_location_types",
    ca = u"Tipus de localització a obtenir",
    es = u"Tipos de localización a obtener",
    en = u"Location types included in updates"
)

translations.define("LocationsExtension.updated_subset",
    ca = u"Subconjunt de localitats a actualitzar",
    es = u"Subconjunto de localidades a actualizar",
    en = u"Subset of locations included in updates"
)

translations.define("LocationsExtension.updated_subset-explanation",
    ca = u"Llistat de codis qualificats de localitat (per exemple, EU-ES-CT, "
         u"EU-ES-CV per seleccionar Catalunya i la Comunitat Valenciana).",
    es = u"Listado de códigos cualificados de localidad (por ejemplo, "
         u"EU-ES-CT, EU-ES-CV para seleccionar Cataluña y la Comunidad "
         u"Valenciana).",
    en = u"List of qualified location codes (ie. EU-ES-CT, EU-ES-CV to "
         u"select Catalonia and the Valencian Country)."
)

SECONDS_IN_A_DAY = 60 * 60 * 24


class LocationsExtension(Extension):

    def __init__(self, **values):
        Extension.__init__(self, **values)
        self.extension_author = u"Whads/Accent SL"
        self.set("description",
            u"""Proporciona accés a la llista de països del món i les seves
            regions, actualitzada a través d'Internet.""",
            "ca"
        )
        self.set("description",            
            u"""Proporciona acceso a la lista de países del mundo y sus
            regiones, actualizada a través de Internet.""",
            "es"
        )
        self.set("description",
            u"""Provides a list of world countries and their regions, 
            automatically updated from the Internet.""",
            "en"
        )

    last_update = None

    members_order = [
        "service_uri",
        "update_frequency",
        "updated_location_types",
        "updated_subset"
    ]

    service_uri = schema.String(
        required = True,
        default = "http://services.woost.info/locations",
        text_search = False
    )

    update_frequency = schema.Integer(
        min = 1,
        default = 15
    )

    updated_location_types = schema.Collection(
        edit_inline = True,
        default = [
            "continent",
            "country",
            "autonomous_community",
            "province",
            "town"
        ],
        items = schema.String(
            required = True,
            enumeration = [
                "continent", 
                "country", 
                "autonomous_community",
                "province",
                "town"
            ],            
            translate_value = lambda value, language = None, **kwargs:
                "" if not value 
                else translations(
                    "woost.extensions.locations.location_types." + value,
                    language,
                    **kwargs
                )
        ),
        text_search = False
    )

    updated_subset = schema.Collection(
        items = schema.String(
            required = True
        ),
        edit_control = "cocktail.html.TextArea"
    )

    def _load(self):        
        from woost.extensions.locations import location, strings

        if self.should_update():
            transaction(
                self.sync_locations, 
                desist = lambda: not self.should_update()
            )

    def should_update(self):

        if self.last_update is None:
            return True

        if self.update_frequency is None:
            return False

        return time() - self.last_update >= self.update_frequency * SECONDS_IN_A_DAY

    def sync_locations(self):
        """Populate the locations database with the data provided by the web
        service.
        """
        text_data = urlopen(self.service_uri).read()
        json_data = loads(text_data)

        for record in json_data:
            self._process_record(record)
            
        self.last_update = time()

    def _process_record(self, record, parent = None, context = None):
        
        from woost.extensions.locations.location import Location

        context = context.copy() if context else {}
        code = record["code"]
        location = None

        if "full_code" in context:
            context["full_code"] += "-" + code
        else:
            context["full_code"] = code

        if self._should_add_location(record, parent, context):

            # Update an existing location
            if parent: 
                location = first(
                    child
                    for child in parent.locations
                    if child.code == code
                )
            else:
                location = first(Location.select([
                    Location.parent.equal(None),
                    Location.code.equal(code)
                ]))

            # Create a new location
            if location is None:
                location = Location()
                location.parent = parent
                location.code = code
                location.insert()

            location.location_type = record["type"]

            for lang, value in record["name"].iteritems():
                if isinstance(value, str):
                    value = value.decode("utf-8")
                location.set("location_name", value, lang)

        # Process child records
        children = record.get("locations")
        if children:
            for child_record in children:
                self._process_record(child_record, location, context)

    def _should_add_location(self, record, parent, context):

        # Filter by tree subset
        if self.updated_subset:
            if not context.get("inside_subset") \
            and context["full_code"] not in self.updated_subset:
                return False
            else:
                context["inside_subset"] = True

        # Filter by location type
        if record["type"] not in self.updated_location_types:
            return False

        return True

