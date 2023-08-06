#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from woost.models.rendering.effects import image_effects

def apply_effects_chain(image, effects_chain):

    for func, args, kwargs in normalize_effects_chain(effects_chain):
        image = func(image, *args, **kwargs)

    return image

def normalize_effects_chain(effects_chain):
  
    if not effects_chain:
        return []

    if isinstance(effects_chain, basestring):
        effects_chain = effects_chain.split("/")

    return [
        parse_effect(effect) if isinstance(effect, basestring) else effect
        for effect
        in effects_chain
    ]

def parse_effect(effects_string):

    pos = effects_string.find("(")
    if pos == -1:
        effects_name = effects_string
    else:
        effects_name = effects_string[:pos]

    try:
        func = image_effects[effects_name]
    except KeyError:
        raise ValueError("Unknown image effect: %s" % effects_name)

    args = []
    kwargs = {}
    
    if pos != -1:
        if effects_string[-1] != ")":
            raise ValueError(
                "Invalid image effect string: %r" % effects_string
            )

        for arg in effects_string[pos + 1:-1].split(","):
            parts = arg.split("=")
            
            # Positional parameters
            if len(parts) == 1:
                value = _parse_value(arg)
                args.append(value)

            # Keyword parameters
            elif len(parts) == 2:
                key, value = parts
                value = _parse_value(value)
                kwargs[key] = value
            else:
                raise ValueError(
                    "Invalid image effects string: %r" % effects_string
                )

    return func, args, kwargs

def _parse_value(value):

    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'\""):
        return value[1:-1]

    if value in ("True", "False"):
        return bool(value)
    
    if "." in value:
        try:
            value = float(value)
        except ValueError:
            pass
        else:
            return value

    try:
        value = int(value)
    except ValueError:
        pass
    else:
        return value

    raise ValueError(
        "Invalid value for image effect parameter: %r" % value
    )

