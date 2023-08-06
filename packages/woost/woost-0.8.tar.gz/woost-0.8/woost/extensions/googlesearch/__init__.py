#-*- coding: utf-8 -*-
"""

@author:		Marc Pérez
@contact:		marc.perez@whads.com
@organization:	Whads/Accent SL
@since:			December 2009
"""
from cocktail.modeling import ListWrapper
from cocktail.translations import translations, get_language
from cocktail import schema
from woost.models import Extension, Language

translations.define("GoogleSearchExtension",
    ca = u"Cercador de Google",
    es = u"Buscador de Google",
    en = u"Google search"
)

translations.define("GoogleSearchExtension-plural",
    ca = u"Cercadors de Google",
    es = u"Buscadores de Google",
    en = u"Google search"
)

translations.define("GoogleSearchExtension.search_engine_id",
    ca = u"Identificador del motor de cerca",
    es = u"Indentificador del motor de busqueda",
    en = u"Search engine id"
)

translations.define("GoogleSearchExtension.results_per_page",
    ca = u"Número de resultats per pàgina",
    es = u"Número de resultados por página",
    en = u"Results number per page"
)

class GoogleSearchExtension(Extension):

    url_template = (
        "http://www.google.com/cse"
        "?cx=%(search_engine_id)s"
        "&query=%(query)s"
        "&start=%(page)d"
        "&num=%(page_size)d"
        "&lr=%(language)s"
        "&filter=%(filter)d"
        "&client=google-csbe"
        "&output=xml_no_dtd"
        "&ie=utf8"
        "&oe=utf8"
    )

    def __init__(self, **values):
        Extension.__init__(self, **values)
        self.extension_author = u"Whads/Accent SL"
        self.set("description",
            u"""Proporciona els elements essencials per implementar el cercador
            de Google""",
            "ca"
        )
        self.set("description",
            u"""Proporciona los elementos esenciales para implementar el 
            buscador de Google""",
            "es"
        )
        self.set("description",
            u"""Provides the essential elements to set up Google Search""",
            "en"
        )

    search_engine_id = schema.String(
        required = True,
        text_search = False
    )

    results_per_page = schema.Integer(
        min = 1,
        max = 20
    )

    def _load(self):
        from woost.extensions.googlesearch import strings

    def search(self,
        query,
        page = 0,
        page_size = 10,
        language = None,
        filter = True):
        """Returns Google CSE results for the given query.
        
        @param query: The query to search.
        @type query: unicode

        @param page: The ordinal index of the results page to return, starting
            at 0.
        @type page: int

        @param page_size: The maximum number of results per page.
        @type page_size: int

        @param language: Restricts search results to matches for the given
            language. The language must be indicated using a two letter ISO
            language code.
        @type language: str

        @param filter: Indicates if Google should apply filtering over the
            search results (ie. to remove redundant matches).
        @type filter: bool

        @return: The results for the given query.
        @rtype: L{GoogleSearchResultsList}
        """
        from xml.sax import parseString
        from xml.sax.handler import ContentHandler
        from urllib import urlopen, quote_plus

        page_size = self.results_per_page or 10

        cse_url = self.url_template % {
            "search_engine_id": self.search_engine_id,
            "query": quote_plus(query.encode("utf-8")),
            "page": page * page_size,
            "page_size": page_size,
            "language": language or get_language(),
            "filter": int(bool(filter))
        }

        f = urlopen(cse_url)
        xml_response = f.read()
        f.close()

        results = []

        READING_TOTAL_COUNT = 1
        READING_TITLE = 2
        READING_URL = 3
        READING_CONTEXT = 4

        class SAXContentHandler(ContentHandler):
            result_count = 0
            current_result = None
            status = None

            def startElement(self, name, attrs):
                if name == "M":
                    self.status = READING_TOTAL_COUNT
                elif name == "T":
                    self.status = READING_TITLE
                elif name == "U":
                    self.status = READING_URL
                elif name == "S":
                    self.status = READING_CONTEXT
                elif name == "R":
                    result = GoogleSearchResult()
                    results.append(result)
                    self.current_result = result
                    
            def endElement(self, name):
                self.status = None
                if name == "R":
                    self.current_result = None

            def characters(self, content):
                if self.status == READING_TOTAL_COUNT:
                    self.result_count = int(content)
                elif self.status == READING_TITLE:
                    self.current_result.title += content
                elif self.status == READING_URL:
                    self.current_result.url += content
                elif self.status == READING_CONTEXT:
                    self.current_result.context += content
                    self.current_result.context = self.current_result.context.replace('<br>','')

        sax_handler = SAXContentHandler()
        parseString(xml_response, sax_handler)

        return GoogleSearchResultsList(
            results,
            page,
            page_size,
            sax_handler.result_count
        )
        

class GoogleSearchResult(object):
    title = ""
    url = ""
    context = ""


class GoogleSearchResultsList(ListWrapper):
    
    def __init__(self, results, page, page_size, result_count):
        ListWrapper.__init__(self, results)
        self.page = page
        self.page_size = page_size
        self.result_count = result_count

