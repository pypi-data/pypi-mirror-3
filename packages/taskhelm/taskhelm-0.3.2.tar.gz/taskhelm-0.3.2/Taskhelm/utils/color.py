#!/usr/bin/env python
# Derived from GTG's colors.py

from gtk.gdk import (
    Color,
    color_parse
    )

def blend(fg, bg, alpha):
    return int(fg*alpha + bg*(1-alpha))

def alpha_from_brightness(fg_brightness, bg_brightness):
    return (1 - abs(fg_brightness - bg_brightness)/65535.0)/2.0

def color_average(colors, bg=None):
    """Given a list of colors, return the average blended with bg

    @param colors can be either a list of gtk.gdk.Color objects or color
    strings (e.g. '#ffffff')
    @param bg is the background color to be applied.
    @return a gtk.gdk.Color object with the averaged value"""
    red = 0
    green = 0
    blue = 0

    if type(colors) is str:
        return color_parse(str)
    elif type(colors) is not list:
        return colors

    for color in colors:
        if type(color) is str:
            color = color_parse(color)
        red += color.red
        green += color.green
        blue += color.blue

    num_colors = len(colors)
    if num_colors > 0:
        red = int(red / num_colors)
        green = int(green / num_colors)
        blue = int(blue / num_colors)
        fg_brightness = (red + green + blue) / 3.0

        if bg is None:
            bg = color_parse('#ffffff')
        bg_brightness = (bg.red + bg.green + bg.blue) / 3.0

        alpha = alpha_from_brightness(fg_brightness, bg_brightness)
        red = blend(red, bg.red, alpha)
        green = blend(green, bg.green, alpha)
        blue = blend(blue, bg.blue, alpha)

    return Color(red, green, blue)

if __name__ == "__main__":
    a = Color(0,0,0)
    b = Color(1,10000,1)
    c = Color(10000,10000,10000)
    print color_average([])
    print color_average(['#ffffff'])
    print color_average(['#000'])
    print color_average(['#fff', '#000'])
    print color_average(['#f00', '#0f0', '#00f'])
    print color_average([a])
    print color_average([c])
    print color_average([a, b, c])
