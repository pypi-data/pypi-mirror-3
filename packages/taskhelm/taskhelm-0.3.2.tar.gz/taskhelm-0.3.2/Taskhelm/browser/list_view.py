#!/usr/bin/env python

import gobject
import pygtk
pygtk.require('2.0')
import gtk
import pango

if __name__ != "__main__":
    from ..task import Task
    from ..editor.editor import TaskEditor

class TaskListView(gtk.TreeView):
    __gsignals__ = {'data-changed': (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, ()) }

    # TODO: Is liststore even needed?
    def __init__(self, columns=None, taskwarrior=None,
                 liststore=None, config=None):
        gtk.TreeView.__init__(self)
        self._taskwarrior = taskwarrior

        self.COL_INDEX = 0
        self._config = config

        # create the TreeViewColumns to display the data
        n = 0
        for col in columns:
            tvcol = gtk.TreeViewColumn(col.label)
            cell = gtk.CellRendererText()
            # TODO: These all work, now to determine what to set based on a column's contents
            #cell.set_property("background", "#456")
            #cell.set_property("foreground", "#f0f")
            #cell.set_property("strikethrough", True)
            #cell.set_property("underline", True)

            tvcol.cell = cell
            tvcol.pack_start(cell, True)
            tvcol.set_attributes(cell, text=n, font=liststore.COL_FONT)
            tvcol.set_visible(col.visible)

            # make treeview sortable and searchable
            tvcol.set_sort_column_id(n)
            if col.search:
                self.set_search_column(n)

            self.append_column(tvcol)
            n = n + 1

        # Permit multiple selection
        tree_sel = self.get_selection()
        tree_sel.set_mode(gtk.SELECTION_MULTIPLE)

    def get_task_uuids(self, selection):
        '''Returns the list of selected task UUIDs'''
        model, selected_paths = selection.get_selected_rows()
        iters = [model.get_iter(path) for path in selected_paths]
        ts = self.get_model()
        return [ts.get_value(iter, self.COL_INDEX) for iter in iters]

    def on_button_press(self, widget, event):
        # Left mouse button double-click
        if event.type == gtk.gdk._2BUTTON_PRESS and event.button == 1:
            selection = self.get_selection()
            uuids = self.get_task_uuids(selection)
            for uuid in uuids:
                task = Task(uuid, config=self._config, taskwarrior=self._taskwarrior)
                text_view = TaskEditor(task)
                text_view.connect('data-changed', self.on_data_changed)

        # Right mouse button click
        elif event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            x = int(event.x)
            y = int(event.y)

            path_info = self.get_path_at_pos(x,y)
            if path_info is not None:
                path, col, cell_x, cell_y = path_info
                selection = self.get_selection()
                if selection.count_selected_rows() <= 0:
                    self.set_cursor(path, col, 0)
                    uuids = []
                else:
                    selection.select_path(path)
                    uuids = self.get_task_uuids(selection)

                widget.set_uuids(uuids=uuids)
                self.grab_focus()
                widget.popup(None, None, None, event.button, event.time)
            return True
        return False

    def on_data_changed(self, widget, tid=None):
        self.emit("data-changed")

    @property
    def count(self):
        model = self.get_model()
        if model is None:
            return 0
        return model.iter_n_children(None)
