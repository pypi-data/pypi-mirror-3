#!/usr/bin/env python

import gobject
import pygtk
pygtk.require('2.0')
import gtk
import pango
import re
import time


class TaskEditor(gtk.Window):
    __gsignals__ = {
        'data-changed': (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (str, )),
        'notes-changed': (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (str, )),
        }
    SAVE_FREQUENCY = 5

    def __init__(self, task, top_level=False):
        assert task, "Undefined task"
        assert task.description, "Undefined task description"
        self._task = task
        self._notes = None
        self.last_saved = time.time()
        self.is_edited = False

        gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)
        self._is_top_level = top_level
        self.set_resizable(True)
        self.connect("destroy", self.on_close_editor)
        self.set_title("Task Editor")
        self.set_border_width(0)
        self.set_geometry_hints(min_width=300, min_height=150)
        self.set_default_size(500, 300)

        root_box = gtk.VBox(False, 0)
        self.add(root_box)
        root_box.show()

        # Upper Tool_bar
        upper_tool_bar = self.create_upper_tool_bar()
        root_box.pack_start(upper_tool_bar, False, True, 0)

        # Text area
        text_area = self.create_text_area()
        root_box.pack_start(text_area)

        # Lower tool_bar
#        lower_tool_bar = self.create_lower_tool_bar()
#        root_box.pack_start(lower_tool_bar, False, True, 0)

        # Put task notes into text buffer
        # TODO: Create a subclass of the text_view - see gtg's taskview
        text_buffer = self.text_view.get_buffer()
        text_buffer.set_text(task.notes)
        pos = text_buffer.get_start_iter()
        tag_title = text_buffer.create_tag(
            "title", foreground="#003366", scale=1.2, underline=1)
        tag_title.set_property('pixels-above-lines', 10)
        tag_title.set_property('pixels-below-lines', 10)
        text_buffer.insert_with_tags(pos, "%s\n" %(task.description), tag_title)
        text_buffer.connect('changed', self.on_edit)

        self.text_view.grab_focus()
        self.show()

    # TODO: Perhaps move this to utils?
    def _validate_date(self, date_text):
        re_date = re.compile("\d\d?/\d\d?/\d\d\d\d")
        if re_date.match(date_text):
            return True
        return False

    def _emit_data_changed(self):
        self.emit('data-changed', self._task.uuid)

    def _emit_notes_changed(self):
        self.emit('notes-changed', self._task.uuid)

    def create_text_area(self):
        self.text_view = gtk.TextView()
        self.text_view.set_editable(True)
        self.text_view.set_cursor_visible(True)
        self.text_view.set_left_margin(4)
        self.text_view.set_right_margin(4)
        self.text_view.set_wrap_mode(gtk.WRAP_WORD)
        self.text_view.show()

        text_area = gtk.ScrolledWindow()
        text_area.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        text_area.add(self.text_view)
        text_area.show()

        return text_area

    def create_upper_tool_bar(self):
        upper_tool_bar = gtk.HBox(False, 10)
        upper_tool_bar.set_border_width(10)
        upper_tool_bar.show()

        button = gtk.Button("Mark as done")
        button.connect("clicked", self.on_task_done)
        upper_tool_bar.pack_start(button, False, True, 0)
        button.show()

        button = gtk.Button("Delete")
        button.connect("clicked", self.on_task_delete)
        upper_tool_bar.pack_start(button, False, True, 0)
        button.show()

        return upper_tool_bar

    def create_lower_tool_bar(self):
        lower_tool_bar = gtk.HBox(False, 10)
        lower_tool_bar.set_border_width(10)
        lower_tool_bar.show()

        label = gtk.Label('Wait until:')
        lower_tool_bar.pack_start(label, False, True, 0)
        label.show()

        wait_date_entry = gtk.Entry()
        if self._task.wait is not None:
            wait_date_entry.set_text(self._task.wait)
        wait_date_entry.connect("changed", self.on_set_wait_date)
        lower_tool_bar.pack_start(wait_date_entry, False, True, 0)
        wait_date_entry.show()

        label = gtk.Label('Due:')
        lower_tool_bar.pack_start(label, False, True, 0)
        label.show()

        due_date_entry = gtk.Entry()
        due_date_entry.connect("changed", self.on_set_due_date)
        lower_tool_bar.pack_start(due_date_entry, False, True, 0)
        due_date_entry.show()

        return lower_tool_bar

    def save(self):
        # TODO: Verify the save succeeded, else do error handling
        text_buffer = self.text_view.get_buffer()
        startiter, enditer = text_buffer.get_bounds()
        notes = text_buffer.get_text(startiter, enditer)
        lines = notes.split('\n')
        if len(lines)<1:
            return

        self.last_saved = time.time()
        self.is_edited = False
        # First line is the description; rest is the actual notes
        if self._task.set_description(lines[0]):
            self._emit_data_changed()
        if self._task.set_notes("\n".join(lines[1:])):
            self._emit_notes_changed()

    def on_edit(self, widget):
        self.is_edited = True

        # Only save if last save was done > 5 sec ago
        difftime = time.time() - self.last_saved
        if difftime > self.SAVE_FREQUENCY:
            self.save()

    def on_close_editor(self, widget):
        # Check for any pending unsaved changes
        if self.is_edited:
            self.save()
        if self._is_top_level:
            gtk.main_quit()
            return False
        else:
            self.destroy()

    def on_task_done(self, widget, data):
        if self._task.set_done():
            self._emit_data_changed()
        print "Task done"
        self.on_close_editor(widget)

    def on_task_delete(self, widget, data):
        # TODO: Pop up a dialog to confirm deletion (maybe?)
        if self._task.delete():
            self._emit_data_changed()
        print "Task delete"
        self.on_close_editor(widget)

    def on_set_due_date(self, widget):
        due_date = widget.get_text()
        if self._validate_date(due_date):
            print "Valid due date %s" %(due_date)
            if task.set_due(due_date):
                self._emit_data_changed()

    def on_set_wait_date(self, widget):
        wait_date = widget.get_text()
        if self._validate_date(wait_date):
            print "Valid wait date %s" %(wait_date)
            if task.set_wait(wait_date):
                self._emit_data_changed()


if __name__ == "__main__":
    import sys, os.path
    sys.path.insert(0, os.path.realpath(os.path.join(
        os.path.dirname(__file__), "../..")))

    from Taskhelm.task import Task

    task = Task('5813dd3c-be66-307c-ed86-326b59e169eb')
    text_view = TaskEditor(task, top_level=True)
    gtk.main()

