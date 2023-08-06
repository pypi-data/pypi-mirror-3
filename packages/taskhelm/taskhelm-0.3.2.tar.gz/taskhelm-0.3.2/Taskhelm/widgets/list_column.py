#!/usr/bin/env python

class Column:
    def __init__(self, name, type, label, visible=True, search=False, sort=None):
        self.name = unicode(name)
        self.type = type
        self.label = label
        self.visible = visible
        self.search = search
        self.sort = sort
