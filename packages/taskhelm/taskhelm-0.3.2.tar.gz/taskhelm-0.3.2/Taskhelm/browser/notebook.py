#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk

# TODO: show_closed_pane / hide_closed_pane
# TODO: on_toolbar_togged / on_toggle_quickadd
# TODO: on_quickadd_activate
# TODO: hide / show / iconify / is_visible / is_active

class NotebookPane:
    '''Base class for panes that can contain pages of sub-windows'''
    def __init__(self, title=None):
        self.title = title

    def hide(self):
        pass

    def show(self):
        pass

    def add_page(self):
        pass

    def remove_page(self):
        pass

