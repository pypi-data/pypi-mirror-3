#-*- coding: utf-8 -*-
"""

@author:		Xavier Torras
@contact:		xavier.torras@whads.com
@organization:	Whads/Accent SL
@since:			Febrary 2010
"""
from datetime import datetime
from simplejson import loads
import urllib2
from cocktail.events import event_handler
from cocktail.translations import translations
from cocktail import schema
from woost.models import (
    Extension,
    get_current_user,
    CreatePermission,
    ModifyPermission,
    DeletePermission,
    PermissionExpression
)

translations.define("VimeoExtension",
    ca = u"Vimeo",
    es = u"Vimeo",
    en = u"Vimeo"
)

translations.define("VimeoExtension-plural",
    ca = u"Vimeo",
    es = u"Vimeo",
    en = u"Vimeo"
)

translations.define("VimeoExtension.default_vimeo_user_name",
    ca = u"Nom d'usuari Vimeo per defecte",
    es = u"Nombre de usuario Vimeo por defecto",
    en = u"Default Vimeo Username"
)


class VimeoExtension(Extension):

    def __init__(self, **values):
        Extension.__init__(self, **values)
        self.extension_author = u"Whads/Accent SL"
        self.set("description",
            u"""Permet integrar vídeos allotjats a vimeo.com""",
            "ca"
        )
        self.set("description",
            u"""Permite integrar videos alojados en vimeo.com""",
            "es"
        )
        self.set("description",
            u"""Publish videos from vimeo.com""",
            "en"
        )

    default_vimeo_user_name = schema.String()

    def _load(self):
        
        # Load extension models, translations and UI extensions
        from woost.extensions.vimeo import (
            video,
            strings,
            useraction,
            vimeovideorenderer,
            migration
        )

        # Setup the synchronization view
        from woost.controllers.backoffice.backofficecontroller \
            import BackOfficeController
        from woost.extensions.vimeo.synccontroller import SyncVimeoController

        BackOfficeController.sync_vimeo = SyncVimeoController

    def synchronize(self, user_name, restricted = False):
        """Synchronizes the list of videos of the given Vimeo account with the
        site's database.

        The method queries Vimeo's public HTTP API, retrieving the list of
        videos for the indicated account and comparing it with the set of
        already known videos (from previous executions of this method). The
        local database will be updated as follows:

            * Videos declared by Vimeo that are not present in the database
              will generate new instances.
            * Videos that exist on both ends will be updated with the data
              provided by the Vimeo service (only non editable members will be
              updated, so that data entered by users in the backoffice is
              preserved).
            * Videos that were instantiated in a previous run but which have
              been deleted at the Vimeo side will be removed from the database.
                
        @param user_name: The Vimeo account to load the videos from.
        @type user_name: str

        @param restricted: Indicates if access control should be applied to the
            operations performed by the method.
        @type restricted: bool
        """
        from woost.extensions.vimeo.video import VimeoVideo
        
        if restricted:
            user = get_current_user()

        # Request the data from Vimeo's simple API
        service_uri = "http://vimeo.com/api/v2/%s/videos.json"
        request = urllib2.Request(service_uri % user_name)
        request.add_header('Referer', '')
        request.add_header('User-Agent', 'woost.extensions.vimeo')
        response = urllib2.urlopen(request).read()

        # Parse JSON data
        remote_videos = set()

        for video_data in loads(response):
            
            video_id = video_data["id"]
            video = VimeoVideo.get_instance(vimeo_video_id = video_id)
            remote_videos.add(video_id)
            
            # Check permissions
            if restricted and not user.has_permission(
                CreatePermission if video is None else ModifyPermission,
                target = (video or VimeoVideo)
            ):
                continue

            # Create new videos
            if video is None:
                is_new = True
                video = VimeoVideo()                
                video.insert()
                video.vimeo_video_id = video_data["id"]
                video.vimeo_user_name = video_data["user_name"]
                video.title = video_data["title"]
                video.description = video_data["description"]

            # Modify new or updated videos
            video.small_thumbnail_uri = video_data["thumbnail_small"]
            video.medium_thumbnail_uri = video_data["thumbnail_medium"]
            video.large_thumbnail_uri = video_data["thumbnail_large"]
            video.vimeo_user_small_portrait_uri = video_data["user_portrait_small"]
            video.vimeo_user_medium_portrait_uri = video_data["user_portrait_medium"]
            video.vimeo_user_large_portrait_uri = video_data["user_portrait_large"]
            video.vimeo_user_url = video_data["user_url"]
            video.uri = video_data["url"]
            video.vimeo_tags = video_data["tags"]
            video.duration = int(video_data["duration"])
            video.width = int(video_data["width"])
            video.height = int(video_data["height"])
            video.upload_date = datetime.strptime(
                video_data["upload_date"],
                "%Y-%m-%d %H:%M:%S"
            )
            video.approval_count = int(video_data["stats_number_of_likes"])
            video.views_count = int(video_data["stats_number_of_plays"])
            video.comments_count = int(video_data["stats_number_of_comments"])

        # Delete videos that have been deleted from the user account
        missing_videos = VimeoVideo.select([
            VimeoVideo.vimeo_user_name.equal(user_name),
            VimeoVideo.vimeo_video_id.not_one_of(remote_videos),
        ])
        missing_videos.verbose = True
        
        if restricted:
            missing_videos.add_filter(
                PermissionExpression(user, DeletePermission)
            )

        missing_videos.delete_items()

