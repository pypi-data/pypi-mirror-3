#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from time import mktime
from cocktail.modeling import abstractmethod


class ContentRenderer(object):

    enabled = True

    @abstractmethod
    def can_render(self, item):
        """Indicates if the renderer is able to render the given item.

        @param item: The item to evaluate.
        @type item: L{Item<woost.models.item.Item>}

        @return: True if the renderer claims to be able to render the item,
            False otherwise.
        @rtype: bool
        """

    @abstractmethod
    def render(self, item, **kwargs):
        """Produces an image for the given item.

        @param item: The item to render.
        @type item: L{Item<woost.models.item.Item>}

        @param kwargs: Additional parameters that can modify the image produced
            by the renderer. These are implementation dependant, and should
            be described by L{rendering_schema}.

        @return: The image for the given item. If a suitable image file
            exists, the method should return a tuple consisting of a string
            pointing to its path and its MIME type. Otherwise, the method
            should craft the image in-memory and return it as an instance of
            the L{Image<Image.Image>} class.
        @rtype: tuple(str, str) or L{Image<Image.Image>}
        """

    def last_change_in_appearence(self, item):
        """Determines the last time an item was modified in a way that may
        alter its rendering.

        This method is used to check wether cached images are still current.

        @param item: The item to evaluate.
        @type item: L{Item<woost.models.item.Item>}

        @return: The timestamp of the last change to the item that could alter
            the resulting image produced by the L{render} method of this
            renderer.
        @rtype: float
        """
        return mktime(item.last_update_time.timetuple())

