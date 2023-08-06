#!/usr/bin/env python

def clamp(x, low, high):
    """
    Ensures that x is between the limits set by low and high.
    For example,
    * clamp(5, 10, 15) is 10.
    * clamp(15, 5, 10) is 10.
    * clamp(20, 15, 25) is 20.

    @param    x: the value to clamp.
    @param  low: the minimum value allowed.
    @param high: the maximum value allowed.
    @returns: the clamped value
    """

    return min(max(x, low), high)

