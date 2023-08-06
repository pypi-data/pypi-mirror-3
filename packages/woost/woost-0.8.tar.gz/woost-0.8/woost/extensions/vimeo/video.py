#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2009
"""
from cocktail import schema
from cocktail.dateutils import split_seconds
from cocktail.translations import translations
from cocktail.html import Element, Content
from woost.models import Publishable, Controller

def _link_display(parent, obj, member):
    url = parent.get_member_value(obj, member)
    return (
        Content("-") if not url
        else Element("a", href = url, children = [url])
    )


class VimeoVideo(Publishable):

    instantiable = False

    groups_order = [
        "content",
        "video_file_data",
        "stats",
        "vimeo_data"
    ]

    members_order = [
        "title",
        "description",
        "vimeo_tags",
        "duration",
        "width",
        "height",
        "approval_count",
        "views_count",
        "comments_count",
        "vimeo_video_id",
        "uri",
        "vimeo_user_name",
        "vimeo_user_url",
        "upload_date"
    ]

    default_controller = schema.DynamicDefault(
        lambda: Controller.get_instance(qname = "woost.uri_controller")
    )

    # Thumbnail URIs
    small_thumbnail_uri = None
    medium_thumbnail_uri = None
    large_thumbnail_uri = None
    vimeo_user_small_portrait_uri = None
    vimeo_user_medium_portrait_uri = None
    vimeo_user_large_portrait_uri = None

    title = schema.String(
        member_group = "content",
        descriptive = True,
        translated = True,
        required = True
    )

    description = schema.String(
        member_group = "content",
        translated = True,
        edit_control = "woost.views.RichTextEditor"
    )

    vimeo_tags = schema.String(
        member_group = "content",
        editable = False
    )

    duration = schema.Integer(
        member_group = "video_file_data",
        required = True,
        min = 0,
        indexed = True,
        editable = False,
        translate_value = lambda value, language = None, **kwargs:
            "" if not value
            else translations("time span", span = split_seconds(value))
    )

    width = schema.Integer(
        member_group = "video_file_data",
        required = True,
        min = 0,
        indexed = True,
        editable = False,
        listed_by_default = False
    )

    height = schema.Integer(
        member_group = "video_file_data",
        required = True,
        min = 0,
        indexed = True,
        editable = False,
        listed_by_default = False
    )

    approval_count = schema.Integer(
        member_group = "stats",
        required = True,
        min = 0,
        indexed = True,
        editable = False,
        listed_by_default = False
    )

    views_count = schema.Integer(
        member_group = "stats",
        required = True,
        min = 0,
        indexed = True,
        editable = False,
        listed_by_default = False
    )

    comments_count = schema.Integer(
        member_group = "stats",
        required = True,
        min = 0,
        indexed = True,
        editable = False,
        listed_by_default = False
    )

    vimeo_video_id = schema.String(
        member_group = "vimeo_data",
        unique = True,
        required = True,
        indexed = True,
        editable = False,
        text_search = False,
        listed_by_default = False
    )

    uri = schema.String(
        member_group = "vimeo_data",
        required = True,
        editable = False,
        listed_by_default = False,
        display = _link_display
    )

    vimeo_user_name = schema.String(
        member_group = "vimeo_data",
        required = True,
        indexed = True,
        editable = False,
        listed_by_default = False
    )

    vimeo_user_url = schema.String(
        member_group = "vimeo_data",
        required = True,
        editable = False,
        listed_by_default = False,
        display = _link_display
    )

    upload_date = schema.DateTime(
        member_group = "vimeo_data",
        required = True,
        editable = False,
        indexed = True,
        listed_by_default = False
    )

    def get_embed_uri(self):
        return "http://player.vimeo.com/video/%s" % self.vimeo_video_id

