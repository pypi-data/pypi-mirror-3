#!/usr/bin/env python

# example menu.py

import pygtk
pygtk.require('2.0')
import gtk
import gobject

def make_menu_item(text, cb):
    menu_item = gtk.MenuItem(text)
    menu_item.connect("activate", cb, text)
    #menu_item.connect("clicked", cb, text)
    menu_item.show()
    return menu_item

class TaskBrowserMenuBar(gtk.MenuBar):
    __gsignals__ = {
        'data-changed': (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, ()),
        }

    # TODO: Switch to use of this dict for constructing menus
    STOCK_MENU = {
        'File': ['New', 'Open', 'Close'],
        }

    def __init__(self, taskwarrior=None):
        # Menu Bar #
        gtk.MenuBar.__init__(self)
        if taskwarrior is None:
            ERR("TaskBrowserMenuBar.init:  Undefined taskwarrior")
        self._taskwarrior = taskwarrior
        self.append(self._make_file_menu())
        self.append(self._make_edit_menu())
        self.append(self._make_help_menu())
        self.show()

    def _emit_data_changed(self, tid=None):
        gobject.idle_add(self.emit, 'data-changed')

    # TODO: Need a test
    def _add_menu_item(self, menu, item_name):
        # TODO: Allow passing menu_name (a str)
        menu.append(make_menu_item(item_name, self.on_echo_only))

    # TODO: Need a test
    def _remove_menu_item(self, menu, item_name):
        # TODO: Allow passing menu_name (a str)
        menu.remove(item_name)
        # TODO: If no more items in menu, hide the menu?

    def _make_file_menu(self):
        root_menu = gtk.MenuItem("File")
        menu = gtk.Menu()
        menu.append(make_menu_item("New", self.on_echo_only))
        menu.append(make_menu_item("Open", self.on_echo_only))
        menu.append(make_menu_item("Close", self.on_echo_only))

        root_menu.set_submenu(menu)
        root_menu.show()
        return root_menu

    def _make_edit_menu(self):
        root_menu = gtk.MenuItem("Edit")
        menu = gtk.Menu()
        menu.append(make_menu_item("Cut", self.on_echo_only))
        menu.append(make_menu_item("Paste", self.on_echo_only))
        menu.append(make_menu_item("Undo", self.on_undo))
        menu.append(make_menu_item("Preferences", self.on_echo_only))

        root_menu.set_submenu(menu)
        root_menu.show()
        return root_menu

    def _make_help_menu(self):
        root_menu = gtk.MenuItem("Help")
        menu = gtk.Menu()
        menu.append(make_menu_item("About", self.on_echo_only))

        root_menu.set_submenu(menu)
        root_menu.show()
        return root_menu

    # Print a string when a menu item is selected
    def on_echo_only(self, widget, text):
        print text

    def on_undo(self, widget, string):
        self._taskwarrior.undo()
        self._emit_data_changed()

if __name__ == "__main__":

    class MenuExample:
        def __init__(self):
            # create a new window
            window = gtk.Window(gtk.WINDOW_TOPLEVEL)
            window.set_size_request(200, 100)
            window.set_title("GTK Menu Test")
            window.connect("delete_event", lambda w,e: gtk.main_quit())

            menu_bar = TaskBrowserMenuBar()

            # A vbox to put a menu in:
            vbox = gtk.VBox(False, 0)
            vbox.pack_start(menu_bar, False, False, 2)
            window.add(vbox)
            vbox.show()
            window.show()

    app = MenuExample()
    gtk.main()

