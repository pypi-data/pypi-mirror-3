#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2009
"""
import re
import sys
from time import time
from simplejson import loads
from urllib import urlopen
from cocktail.translations import translations
from cocktail import schema
from cocktail.persistence import datastore
from woost.models import Extension, Language

translations.define("CountriesExtension",
    ca = u"Països",
    es = u"Países",
    en = u"Countries"
)

translations.define("CountriesExtension-plural",
    ca = u"Països",
    es = u"Países",
    en = u"Countries"
)

translations.define("CountriesExtension.update_frequency",
    ca = u"Freqüència d'actualització",
    es = u"Frecuencia de actualización",
    en = u"Update frequency"
)

translations.define("CountriesExtension.update_frequency-explanation",
    ca = u"El nombre de dies entre actualitzacions de la llista de paisos",
    es = u"El número de días entre actualizaciones de la lista de países",
    en = u"Number of days between updates to the country list"
)

SECONDS_IN_A_DAY = 60 * 60 * 24


class CountriesExtension(Extension):

    def __init__(self, **values):
        Extension.__init__(self, **values)
        self.extension_author = u"Whads/Accent SL"
        self.set("description",
            u"""Proporciona accés a la llista de països del món,
            actualitzada a través d'Internet.""",
            "ca"
        )
        self.set("description",            
            u"""Proporciona acceso a la lista de países del mundo, actualizada
            a través de Internet.""",
            "es"
        )
        self.set("description",
            u"""Provides a list of world countries, automatically updated from
            the Internet.""",
            "en"
        )

    last_update = None

    update_frequency = schema.Integer(
        min = 1,
        required = True,
        default = 15
    )

    def _load(self):
        
        from woost.extensions.countries import country, strings

        now = time()
        
        if self.last_update is None \
        or now - self.last_update >= self.update_frequency * SECONDS_IN_A_DAY:
            try:
                self.update_country_list()
            except:
                pass
            else:
                self.last_update = now
                datastore.commit()

    def update_country_list(self):
        from woost.extensions.countries.country import Country
        error = None
        
        database_modified = False
        service_uri = "http://www.lonelydrops.com/drops/1.0/list/%s/countries"
    
        data_expr = re.compile(
            r"var\s+drops_countries_[a-z]{2}\s*=\s*([^;]+)",
            re.DOTALL
        )
        json_property_normalization = re.compile(
            r"([a-zA-Z_$][a-zA-Z_$0-9]*)(?=\s*:)"
        )

        for language in Language.codes:
            try:
                javascript = urlopen(service_uri % language).read()
            except Exception, error:
                pass
            else:
                match = data_expr.search(javascript)

                if not match:
                    sys.stderr.write(
                        "The country list provider returned data in an "
                        "unexpected format (requested translation: %s)" % language
                    )
                    continue

                json = match.group(1)
                json = json_property_normalization.sub(r'"\1"', json)
                
                try:
                    data = loads(json)
                except Exception, error:
                    sys.stderr.write(
                        "The country list provider returned invalid data: %s"
                        "(requested translation: %s)\n" % (error, language)
                    )
                    continue

                for country_data in data:

                    # Ignore continents
                    if country_data.get("isParent"):
                        continue

                    name = country_data["label"]
                    iso_code = country_data["value"].lower()
                    country = Country.get_instance(iso_code = iso_code)

                    # New country
                    if country is None:
                        country = Country()
                        country.iso_code = iso_code
                        country.set("country_name", name, language)
                        country.insert()
                        database_modified = True

                    # Modified country
                    elif country.get("country_name", language) != name:
                        country.set("country_name", name, language)
                        database_modified = True
        
        if error:
            raise error

        return database_modified

