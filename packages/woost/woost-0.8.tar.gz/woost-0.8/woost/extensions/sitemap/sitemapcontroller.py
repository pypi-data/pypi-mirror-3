#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			February 2010
"""
from cocktail.modeling import cached_getter
from cocktail.controllers import Location
from woost.models import Publishable
from woost.controllers import BaseCMSController


class SitemapController(BaseCMSController):

    namespace = "http://www.sitemaps.org/schemas/sitemap/0.9"

    @cached_getter
    def items(self):
        return Publishable.select_accessible([
            Publishable.sitemap_indexable.equal(True)
        ])

    def __call__(self):
        
        output = []
        write = output.append

        write(u"<?xml version='1.0' encoding='utf-8'?>")
        write(u"<urlset xmlns='%s'>" % self.namespace)

        base_url = str(Location.get_current_host()).rstrip(u"/")
        uri = self.context["cms"].uri

        for item in self.items:
            write(u"\t<url>")
            
            item_uri = base_url + u"/" + uri(item).lstrip(u"/")
            write(u"\t\t<loc>%s</loc>" % item_uri)
            
            date = item.last_update_time.strftime("%Y-%m-%d")
            write(u"\t\t<lastmod>%s</lastmod>" % date)
            
            frequency = item.sitemap_change_frequency
            if frequency:
                write(u"\t\t<changefreq>%s</changefreq>" % frequency)

            priority = item.sitemap_priority
            if priority:
                write(u"\t\t<priority>%s</priority>" % priority)

            write(u"\t</url>") 
        
        write(u"</urlset>")
        return u"\n".join(output)

