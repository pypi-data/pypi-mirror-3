#!/usr/bin/env python

from gtk.gdk import Screen

def X_is_running():
    '''Returns true if X.org is running'''
    try:
        if Screen().get_display():
            return True
    except RuntimeError:
        pass
    return False

