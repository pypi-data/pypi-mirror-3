#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2009
"""
from cocktail.styled import styled

def permission_separator_style(char = u"-", width = 80):
    return styled(char * width, "violet")

def permission_check_style(t, width = 80):
    return u"\n" + styled(t.ljust(width, " "), "white", "violet")

def permission_param_style(key, value):
    return u" " * 4 + styled(key + ":", style = "bold") \
         + u" " + unicode(value)

def role_style(t):
    return u"\n" + (u" " * 4) + styled(t, style = "underline")

def permission_style(t):
    return u" " * 4 + styled(t, "light_gray")

def authorized_style(t):
    return u" " * 4 + styled(t.upper(), "white", "green") + u"\n"

def unauthorized_style(t):
    return u" " * 4 + styled(t.upper(), "white", "red") + u"\n"

def permission_doesnt_match_style(t):
    return u" " * 4 + styled(t, "yellow") + u"\n"

def trigger_style(t):
    return styled(t.ljust(80), "white", "brown")

def trigger_context_style(k, v):
    return styled(" " * 4 + (k + ":").ljust(15), style = "bold") \
        + " " + unicode(v)

def trigger_doesnt_match_style(t):
    return styled(" " * 4 + t, "yellow")

def trigger_match_style(t):
    return " " * 4 + styled(t.upper(), "white", "green")

