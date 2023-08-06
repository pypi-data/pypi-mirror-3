#!/usr/bin/env python
import os
import sys
import gtk
import pygtk

class NewTaskDialog(gtk.Dialog):
    def __init__(self, taskwarrior=None):
        gtk.Dialog.__init__(self,
                            "Add Task",
                            None,
                            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                            (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                             gtk.STOCK_OK, gtk.RESPONSE_OK))
        self._taskwarrior = taskwarrior
        self.set_geometry_hints(min_width=500)

        # Text entry area for the new task
        self.entry = gtk.Entry()
        self.entry.connect("activate", self.on_add_task, self, gtk.RESPONSE_OK)

        hbox = gtk.HBox()
        hbox.pack_start(gtk.Label("New Task:"), False, 5, 5)
        hbox.pack_end(self.entry)

        self.vbox.pack_end(hbox, True, True, 0)
        self.show_all()

    def text(self):
        return self.entry.get_text()

    def on_add_task(self, entry, dialog, response):
        self.response(response)

    def main(self):
        response = self.run()
        if response != gtk.RESPONSE_OK:
            return 1
        desc = dlg.text()
        dlg.destroy()
        if self._taskwarrior is not None:
            tw.add(desc)
            return desc
        return None

if __name__ == '__main__':
    import sys, os.path
    sys.path.insert(0, os.path.realpath(os.path.join(
        os.path.dirname(__file__), "../..")))
    from Taskhelm.taskwarrior import TaskWarrior

    tw = TaskWarrior()
    dlg = NewTaskDialog(taskwarrior=tw)
    desc = dlg.main()
    if not desc:
        sys.exit(1)

    print tw.last_command
    sys.exit(0)

