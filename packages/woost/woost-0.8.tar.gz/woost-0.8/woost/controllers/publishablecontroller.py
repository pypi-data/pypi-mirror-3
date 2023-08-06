#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from __future__ import with_statement
from types import GeneratorType
from threading import Lock
from time import time, mktime
from hashlib import md5
import cherrypy
from cherrypy.lib import cptools, http
from woost.controllers import BaseCMSController, get_cache_manager


class PublishableController(BaseCMSController):
    """Base controller for all publishable items (documents, files, etc)."""

    cache_enabled = True

    cached_headers = (
        "Content-Type",
        "Content-Length",
        "Content-Disposition",
        "Content-Encoding",
        "Last-Modified"
    )

    class __metaclass__(BaseCMSController.__class__):

        def __init__(cls, name, bases, members):
            BaseCMSController.__class__.__init__(cls, name, bases, members)
            cls._cached_responses = {}
            cls._cached_responses_lock = Lock()

    def __call__(self, **kwargs):
        
        if self.cache_enabled and cherrypy.request.method == "GET":
            content = self._apply_cache(kwargs)
            if content is not None:
                return content

        return self._produce_content(**kwargs)

    def _apply_cache(self, kwargs):

        if "original_publishable" in self.context:
            return

        request = cherrypy.request
        response = cherrypy.response
        publishable = self.context["publishable"]

        caching_context = {
            "request": request,
            "controller": self
        }
        policy = publishable.get_effective_caching_policy(**caching_context)

        if policy is not None and policy.cache_enabled:

            # Find the unique cache identifier for the requested content
            cache_key = repr(policy.get_content_cache_key(
                publishable,
                **caching_context
            ))

            # Find the last time that the requested element (or its related
            # content) was modified
            content_last_update = policy.get_content_last_update(
                publishable,
                **caching_context
            )
            
            # Client side cache
            timestamp = None
            
            if content_last_update:
                timestamp = mktime(content_last_update.timetuple())
                etag_hash = md5()
                etag_hash.update(cache_key)
                etag_hash.update(repr(timestamp))
                response.headers["ETag"] = etag_hash.hexdigest()
                cptools.validate_etags()

            # Server side cache
            if policy.server_side_cache:
                
                cached_response = \
                    self._get_cached_content(cache_key, policy, timestamp)
                
                if cached_response:
                    headers, content = cached_response
                    cherrypy.response.headers.update(headers)
                else:
                    content = self._produce_cached_content(
                        cache_key,
                        **kwargs)

                return content

    def _get_cached_content(self, cache_key, policy, timestamp = None):

        publishable = self.context["publishable"]
        cache = get_cache_manager().get_cache_region(
            'cached_content', 'woost_cache'
        )

        # Look for a cached response for the specified key
        cached_response = None
        cache_hash = md5(cache_key).hexdigest()

        if cache.has_key(cache_hash):
            cache_entry = cache.get(cache_hash)

            if cache_entry:
                entry_creation_time, cached_response, cached_key = cache_entry

                valid_key = (cached_key == cache_key)

                # Validate entry expiration
                expiration = policy.cache_expiration
                expired = (expiration is not None
                           and time() - entry_creation_time > expiration * 60)
                
                current = timestamp is None or entry_creation_time >= timestamp

                if expired or not current or not valid_key:
                    cache.remove(cache_hash)
                    cached_response = None
        
        return cached_response

    def _produce_cached_content(self, cache_key, **kwargs):

        cache = get_cache_manager().get_cache_region(
            'cached_content', 'woost_cache'
        )
        content = self._produce_content(**kwargs)

        if isinstance(content, GeneratorType):
            content = "".join(content)

        # Collect headers that should be included in the cache
        headers = {}
        response_headers = cherrypy.response.headers
        
        for header_name in self.cached_headers:
            header_value = response_headers.get(header_name)
            if header_value:
                headers[header_name] = header_value

        # Store the response in the cache
        entry_creation_time = time()
        cached_response = (headers, content)
        cache_hash = md5(cache_key).hexdigest()
        cache.put(cache_hash, (entry_creation_time, cached_response, cache_key))

        return content

    def _produce_content(self, **kwargs):
        return BaseCMSController.__call__(self, **kwargs)

