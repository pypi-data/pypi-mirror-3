#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2009
"""
import __builtin__
from datetime import datetime
import cherrypy
from cocktail.controllers.location import Location
from cocktail.translations import translations, get_language
from woost.models import (
    Feed,
    Site,
    PermissionExpression,
    ReadPermission,
    get_current_user
)
from woost.controllers.publishablecontroller import PublishableController


class FeedController(PublishableController):

    def _produce_content(self, **kwargs):

        site = Site.main
        cms = self.context["cms"]
        feed = self.context["publishable"]
        
        location = Location.get_current()
        location.relative = False

        def rfc822_date(date):
            tz = "Z" if site.timezone is None else site.timezone
            return date.strftime("%d %%s %Y %H:%M:%S %%s") % (
                ("Jan", "Feb", "Mar", "Apr", "May", "Jun",
                 "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")[date.month - 1],
                tz
            )

        params = {
            "title": feed.title,
            "url": unicode(location),
            "description": feed.description,
            "language": get_language(),
            "now": rfc822_date(datetime.now())
        }

        location.path_info = self.application_uri()
        location.query_string = None
        base_url = unicode(location)
        params["base_url"] = base_url
        
        output = []
        output.append(u"""<?xml version='1.0' encoding='utf-8'?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
    <channel>
        <title><![CDATA[%(title)s]]></title>
        <link><![CDATA[%(base_url)s]]></link>
        <description><![CDATA[%(description)s]]></description>
        <language>%(language)s</language>
        <pubDate>%(now)s</pubDate>
        <atom:link href="%(url)s" rel="self" type="application/rss+xml" />
""" % params)
        
        if feed.image:
            image_uri = feed.image.uri
            
            if image_uri.startswith("/"):
                image_uri = base_url + image_uri[1:]

            params["image_url"] = image_uri
            output.append(u"""
        <image>
            <url>%(image_url)s</url>
            <title>%(title)s</title>
            <link>%(base_url)s</link>
        </image>""" % params)

        if feed.ttl:
            output.append(u"""
        <ttl>%d</ttl>""" % feed.ttl)

        context = {
            "__builtins__": __builtin__,
            "feed": feed,
            "language": get_language(),
            "cms": cms,
            "translations": translations
        }

        items = feed.select_items()
        items.add_filter(PermissionExpression(
            get_current_user(),
            ReadPermission)
        )

        # Compile the expressions for item contents
        item_title_code = compile(
            feed.item_title_expression,
            "Feed #%d item_title_expression" % feed.id,
            "eval"
        )

        item_link_code = compile(
            feed.item_link_expression,
            "Feed #%d item_link_expression" % feed.id,
            "eval"
        )

        item_publication_date_code = compile(
            feed.item_publication_date_expression,
            "Feed #%d item_publication_date_expression" % feed.id,
            "eval"
        )

        item_description_code = compile(
            feed.item_description_expression,
            "Feed #%d item_description_expression" % feed.id,
            "eval"
        )
       
        for item in items:
            context["item"] = item
            
            title = eval(item_title_code, context)            
            if not title:
                continue
            
            link = eval(item_link_code, context)
            if not link:
                continue

            if link.startswith("/"):
                link = base_url + link[1:]
            
            output.append(
u"""        <item>
            <title><![CDATA[%(title)s]]></title>
            <url><![CDATA[%(url)s]]></url>
            <guid isPermaLink="true"><![CDATA[%(url)s]]></guid>
        """ % {
                "title": title,
                "url": link
            })
            
            pub_date = eval(item_publication_date_code, context)
            if pub_date:
                output.append(
u"""            <pubDate><![CDATA[%s]]></pubDate>""" % rfc822_date(pub_date))

            description = eval(item_description_code, context)
            if description:
                output.append(
u"""            <description><![CDATA[%s]]></description>""" % description)

            output.append(
u"""        </item>""")

        output.append(u"""
    </channel>
</rss>""")
        return u"\n".join(output).encode("utf-8")

