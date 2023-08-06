#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from threading import Lock
import Image
from cocktail.modeling import ListWrapper
from woost.models.rendering.effectschain import (
    apply_effects_chain,
    normalize_effects_chain
)


class ContentRenderersRegistry(ListWrapper):

    def __init__(self, items = None):
        ListWrapper.__init__(self, items)
        self.__lock = Lock()

    def register(self, renderer, after = None, before = None):
        """Add a new content renderer to the registry.

        By default, renderers are appended at the end of the registry. The
        L{after} or L{before} parameters can be used to specify the position in
        the registry where the renderer should be inserted. This can be
        important, since renderer are tried in registration order

        @param renderer: The renderer to register.
        @type renderer: L{ContentRenderer}
        """
        with self.__lock:

            marker = after or before

            if marker is None:
                self._items.append(renderer)            
            else:
                if after and before:
                    raise ValueError(
                        "Can't register content renderer '%s' specifying both "
                        "'after' and 'before' parameters"
                        % renderer
                    )

                # Find the requested position
                if isinstance(marker, type):

                    # Find the first instance of the given type
                    for pos, registered_renderer in enumerate(self._items):
                        if isinstance(registered_renderer, marker):
                            break
                    else:
                        pos = -1
                else:
                    # Find an specific instance
                    try:
                        pos = self._items.index(marker)
                    except IndexError:
                        pos = -1

                if pos == -1:
                    self._items.append(renderer)
                elif before:
                    self._items.insert(pos, renderer)
                else:
                    self._items.insert(pos + 1, renderer)  

    def render(self,
        item,
        effects = None,
        apply_item_effects = True,
        **kwargs):

        # Composite the effects defined by the rendered item with the
        # additional effects required for the current rendering operation
        if apply_item_effects and not isinstance(item, type):
            item_effects = getattr(item, "image_effects", None)
            if item_effects:
                effects = (
                    normalize_effects_chain(item_effects)
                  + normalize_effects_chain(effects)
                )

        # Look for the first renderer that can handle the item
        for renderer in self:
            if renderer.enabled and renderer.can_render(item):
                image = renderer.render(item, **kwargs)
                
                # Apply rendering effects
                if effects:
                    if isinstance(image, basestring):
                        image = Image.open(image)
                    image = apply_effects_chain(image, effects)
                
                return image


content_renderers = ContentRenderersRegistry()
icon_renderers = ContentRenderersRegistry()

