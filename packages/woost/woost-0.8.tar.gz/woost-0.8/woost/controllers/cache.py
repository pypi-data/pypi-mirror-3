#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Jordi Fernández <jordi.fernandez@whads.com>
"""
_cache_manager = None


def get_cache_manager():
    return _cache_manager


def set_cache_manager(cache_manager):
    global _cache_manager
    _cache_manager = cache_manager
