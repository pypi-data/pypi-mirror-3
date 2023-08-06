#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2009
"""
from threading import local

_thread_data = local()

def get_current_user():
    """Gets the current user for the present context.
    
    The concept of an 'active' user is used in several places to bind certain
    operations (authorization, versioning...) to an individual.

    @rtype: L{User}
    """
    return getattr(_thread_data, "user", None)

def set_current_user(user):
    """Sets the current user for the present context. See L{get_current_user}
    for more information.

    @param user: The user to set as the active user.
    @type user: L{User}
    """
    _thread_data.user = user

