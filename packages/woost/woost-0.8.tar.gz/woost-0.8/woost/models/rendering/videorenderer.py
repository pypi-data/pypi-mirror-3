#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import os
import datetime
from subprocess import Popen, PIPE
import Image
from woost.models.file import File
from woost.models.rendering.contentrenderer import ContentRenderer
from woost.models.rendering.contentrenderersregistry import content_renderers


class VideoRenderer(ContentRenderer):
    """A content renderer that handles video files."""

    try:                                                                                                                                                                                                       
        p = Popen(["which", "ffmpeg"], stdout=PIPE)
        ffmpeg_path = p.communicate()[0].replace("\n", "") or None
    except:
        ffmpeg_path = None
    try:
        p = Popen(["which", "grep"], stdout=PIPE)
        grep_path = p.communicate()[0].replace("\n", "") or None
    except:
        grep_path = None
    try:
        p = Popen(["which", "cut"], stdout=PIPE)
        cut_path = p.communicate()[0].replace("\n", "") or None
    except:
        cut_path = None
    try:
        p = Popen(["which", "sed"], stdout=PIPE)
        sed_path = p.communicate()[0].replace("\n", "") or None
    except:
        sed_path = None

    def _secs2time(self, s):
        ms = int((s - int(s)) * 1000000)
        s = int(s)
        # Get rid of this line if s will never exceed 86400
        while s >= 24*60*60: s -= 24*60*60
        h = s / (60*60)
        s -= h*60*60
        m = s / 60
        s -= m*60
        return datetime.time(h, m, s, ms)
    
    def _time2secs(self, d):
        return d.hour*60*60 + d.minute*60 + d.second + \
            (float(d.microsecond) / 1000000)

    def can_render(self, item):
        return (
            self.ffmpeg_path 
            and self.grep_path 
            and self.cut_path
            and self.sed_path 
            and isinstance(item, File) 
            and item.resource_type == "video"
        )

    def render(self, item, position = None):
        
        temp_path = mkdtemp()

        try:
            temp_image_file = os.path.join(temp_path, "thumbnail.png")
            
            command1 = "%s -i %s" % (self.ffmpeg_path, item.file_path)
            command2 = "%s Duration | %s -d ' ' -f 4 | %s 's/,//'" % (
                self.grep_path,
                self.cut_path,
                self.sed_path
            )
            p1 = Popen(command1, shell=True, stderr=PIPE)
            p2 = Popen(command2, shell=True, stdin=p1.stderr, stdout=PIPE)
            duration = p2.communicate()[0]

            duration_list = re.split("[.:]", duration)
            video_length = datetime.time(
                int(duration_list[0]), int(duration_list[1]),
                int(duration_list[2]), int(duration_list[3])
            )   

            if position:
                time = self._secs2time(position)
            else:
                seconds = self._time2secs(video_length)
                time = self._secs2time(seconds / 2)
    
            if time > video_length:
                raise ValueError(
                    "Must specify a smaller position than the video duration."
                )
    
            command = u"%s -y -i %s -vframes 1 -ss %s -an -vcodec png -f rawvideo %s " % (
                self.ffmpeg_path, 
                item.file_path, 
                time.strftime("%H:%M:%S"),
                temp_image_file
            )
    
            p = Popen(command.split(), stdout=PIPE)
            p.communicate()
    
            return Image.open(temp_image_file)

        finally:
            rmtree(temp_path)

    def last_change_in_appearence(self, item):
        return os.stat(item.file_path).st_mtime


content_renderers.register(VideoRenderer())

