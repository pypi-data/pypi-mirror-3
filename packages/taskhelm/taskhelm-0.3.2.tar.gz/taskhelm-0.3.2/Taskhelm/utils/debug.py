#!/usr/bin/env python

import sys

ENABLED = False

def dbg(msg):
    if ENABLED:
        sys.stderr.write("%s\n" %(msg))

def ERR(msg):
    sys.stderr.write("Error: %s\n" %(msg))


