#!/usr/bin/env python

def quote(msg):
    """
    Similar to urllib.quote but for glibs GMarkup
    @param msg: string to quote
    @returns: quoted string
    """
    msg = msg.replace('&', '&amp;')
    msg = msg.replace('<', '&lt;')
    msg = msg.replace('>', '&gt;')
    return msg
