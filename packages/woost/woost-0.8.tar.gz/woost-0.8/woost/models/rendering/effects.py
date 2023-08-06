#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import Image
import ImageEnhance
import ImageFilter
from cocktail.modeling import OrderedDict
from woost.models.file import File

image_effects = OrderedDict()

def image_effect(func):
    image_effects[func.func_name] = func
    return func

def resolve_px(value, size):
    if isinstance(value, float):        
        value = int(size * value)
    if value < 0:
        value = size + value
    return value

def resolve_color(value):

    if isinstance(value, basestring):

        if len(value) in (3, 4):
            value = tuple(int(d * 2, 16) for d in value)
        elif len(value) == 6:
            value = (
                int(value[0:2], 16),
                int(value[2:4], 16),
                int(value[4:6], 16)
            )
        elif len(value) == 8:
            value = (
                int(value[0:2], 16),
                int(value[2:4], 16),
                int(value[4:6], 16),
                int(value[6:8], 16)
            )
        else:
            raise ValueError("Invalid color: " + value)

    return value

@image_effect
def thumbnail(image, width = None, height = None, filter = Image.ANTIALIAS):
    
    im_width, im_height = image.size

    if width is None:
        width = im_width

    if height is None:
        height = im_height

    image.thumbnail(
        (resolve_px(width, im_width),
         resolve_px(height, im_height)),
        filter
    )
    return image

@image_effect
def crop(image, x1, y1, x2, y2):

    width, height = image.size

    return image.crop((
        resolve_px(x1, width),
        resolve_px(y1, height),
        resolve_px(x2, width),
        resolve_px(y2, height)
    ))

@image_effect
def fill(image, width, height, crop = "center", filter = Image.ANTIALIAS):

    source_width, source_height = image.size
    source_ratio = float(source_width) / source_height
    target_ratio = float(width) / height

    if source_ratio > target_ratio:
        target_width = int(height * source_ratio)
        target_height = height
    else:
        target_width = width
        target_height = int(width * (1 / source_ratio))

    image = image.resize((target_width, target_height), filter)

    if crop:
        if crop == "center":
            offset_x = (target_width - width) / 2
            offset_y = (target_height - height) / 2
            image = image.crop((
                offset_x,
                offset_y,
                width + offset_x,
                height + offset_y
            ))
        else:
            raise ValueError("crop = %s not implemented" % crop)

    return image

@image_effect
def rotate(image, angle, expand = True, filter = Image.BICUBIC):
    return image.rotate(angle, filter, expand)

@image_effect
def color(image, level):
    return ImageEnhance.Color(image).enhance(level)

@image_effect
def brightness(image, level):
    return ImageEnhance.Brightness(image).enhance(level)

@image_effect
def contrast(image, level):
    return ImageEnhance.Contrast(image).enhance(level)

@image_effect
def sharpness(image, level):
    return ImageEnhance.Sharpness(image).enhance(level)

@image_effect
def frame(
    image,
    edge = 1,
    edge_color = (0,0,0),
    padding = 0,
    padding_color = (255,255,255)
):
    edge_color = resolve_color(edge_color)
    padding_color = resolve_color(padding_color)

    # Create the canvas
    width, height = image.size
    offset = edge + padding
    canvas = Image.new("RGBA", (width + offset * 2, height + offset * 2))    

    # Paint the border
    if edge:
        canvas.paste(edge_color, None)

    # Paint the padding color
    canvas.paste(
        padding_color,
        (edge,
         edge,
         width + offset * 2 - edge,
         height + offset * 2 - edge)
    )
    
    # Paste the original image over the frame
    canvas.paste(
        image,
        (offset, offset),
        image if image.mode in ("1", "L", "RGBA") else None
    )

    return canvas

@image_effect
def shadow(
    image,
    offset = 5,
    color = (70,70,70),
    padding = 8,
    iterations = 3):   
    
    # Create the backdrop image -- a box in the background colour with a 
    # shadow on it.
    total_width = image.size[0] + abs(offset) + 2 * padding
    total_height = image.size[1] + abs(offset) + 2 * padding
    back = Image.new("RGBA", (total_width, total_height))

    # Place the shadow, taking into account the offset from the image
    shadow_left = padding + max(offset, 0)
    shadow_top = padding + max(offset, 0)
    color = resolve_color(color)
    back.paste(color, [
        shadow_left,
        shadow_top,
        shadow_left + image.size[0], 
        shadow_top + image.size[1]
    ])

    # Apply the filter to blur the edges of the shadow.  Since a small kernel
    # is used, the filter must be applied repeatedly to get a decent blur.
    for n in range(iterations):
        back = back.filter(ImageFilter.BLUR)

    # Paste the input image onto the shadow backdrop
    image_left = padding - min(offset, 0)
    image_top = padding - min(offset, 0)
    back.paste(
        image,
        (image_left, image_top),
        image if image.mode in ("1", "L", "RGBA") else None
    )

    return back

@image_effect
def reduce_opacity(image, opacity):
    """An image effect that reduces the opacity of the given image."""

    if opacity < 0 or opacity > 1:
        raise ValueError(
            "The 'opacity' parameter of the 'reduce_opacity' image effect "
            "must be a floating point number between 0 and 1: got %s instead"
            % opacity
        )
    
    if image.mode != 'RGBA':
        image = image.convert('RGBA')
    else:
        image = image.copy()

    alpha = image.split()[3]
    alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
    image.putalpha(alpha)
    return image

@image_effect
def watermark(image, mark_image, position = "middle", opacity = 1):

    if isinstance(mark_image, File):
        mark_image = Image.open(mark.file_path)

    if opacity < 1:
        mark_image = reduce_opacity(mark_image, opacity)

    if image.mode != 'RGBA':
        image = image.convert('RGBA')
    
    # Create a transparent layer the size of the image and draw the
    # watermark in that layer.
    layer = Image.new('RGBA', image.size, (0,0,0,0))
    
    if position == 'tile':
        for y in range(0, image.size[1], mark_image.size[1]):
            for x in range(0, image.size[0], mark_image.size[0]):
                layer.paste(mark_image, (x, y), mark_image)
    elif position == 'scale':
        # scale, but preserve the aspect ratio
        ratio = min(
            float(image.size[0]) / mark_image.size[0],
            float(image.size[1]) / mark_image.size[1]
        )
        w = int(mark_image.size[0] * ratio)
        h = int(mark_image.size[1] * ratio)
        mark_image = mark_image.resize((w, h))
        layer.paste(
            mark_image,
            ((image.size[0] - w) / 2, (image.size[1] - h) / 2),
            mark_image
        )
    elif position == 'middle':        
        layer.paste(
            mark_image,
            (
                (image.size[0] - mark_image.size[0]) / 2,
                (image.size[1] - mark_image.size[1]) / 2
            ),
            mark_image
        )
    else:
        raise ValueError(
            "Must specify position parameter [tile,scale,middle]."
        )
    #TODO
    # top-left      top         top-right
    # left          middle      right
    # bottom-left   bottom      bottom-right
    # margin

    # composite the watermark with the layer
    return Image.composite(layer, image, layer)

@image_effect
def flip(image, direction):
    return image.transpose(direction)

@image_effect
def fit(image, width, height, crop = "center", filter = Image.ANTIALIAS):

    if image.size[0] > width or image.size[1] > height:
        if image.size[0] >= image.size[1]:
            image = fill(image, width, height, crop, filter)
        else:
            image.thumbnail((width, height), filter)

    return image

@image_effect
def align(
    image, 
    width = None, 
    height = None, 
    halign = "center", 
    valign = "center", 
    background = None):

    needs_halign = (width and image.size[0] < width)
    needs_valign = (height and image.size[1] < height)

    if needs_halign or needs_valign:
        
        if background:
            background = resolve_color(background)
        elif image.mode == "RGBA":
            background = (0,0,0,0)

        copy = Image.new(
            "RGBA" if background and len(background) == 4 else "RGB",
            (
                width or image.size[0],
                height or image.size[1]
            ), 
            background
        )

        x = 0
        y = 0
            
        if needs_halign:
            if halign == "left":
                pass
            elif halign == "center":
                x = width / 2 - image.size[0] / 2
            elif halign == "right":
                x = width - image.size[0]
            else:
                raise ValueError(
                    "Invalid parameter: align(halign = %r)" % halign
                )

        if needs_valign:
            if valign == "top":
                pass
            elif valign == "center":
                y = height / 2 - image.size[1] / 2
            elif valign == "bottom":
                y = height - image.size[1]
            else:
                raise ValueError(
                    "Invalid parameter: align(valign = %r)" % valign
                )       

        copy.paste(image, (x, y), image if image.mode == "RGBA" else None)
        return copy

    return image

