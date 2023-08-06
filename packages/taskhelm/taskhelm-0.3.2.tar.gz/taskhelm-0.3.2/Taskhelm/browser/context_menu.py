#!/usr/bin/env python

# Task action context menu

import gobject
import pygtk
pygtk.require('2.0')
import gtk

if __name__ != "__main__":
    from ..task import Task
    from ..editor.editor import TaskEditor
    from ..utils.debug import dbg

def total_tasks_in_period(schedule, start_date, period_length):
    count = 0
    for offset in range(0, period_length):
        day = start_date + timedelta(days=offset)
        if day in schedule:
            count += schedule[day]
    return count

# TODO: Perhaps the handlers should be moved to TaskListView?
#       Then they'd be more easily reusable in other parts of the UI
#       It'd eliminate the need to carry a lot of globals here
class TaskBrowserContextMenu(gtk.Menu):
    __gsignals__ = {
        'data-changed': (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, ()),
        }

    def __init__(self, liststore=None, taskwarrior=None, config=None):
        gtk.Menu.__init__(self)
        if taskwarrior is None:
            ERR("TaskBrowserContextMenu.init:  Undefined taskwarrior")
        self._taskwarrior = taskwarrior
        self._liststore   = liststore
        self._config      = config

    def _emit_data_changed(self, tid=None):
        gobject.idle_add(self.emit, 'data-changed')

    def _clear_menu_items(self):
        for c in self.get_children():
            self.remove(c)

    def _add_menu_item(self, text, callback, uuids, data=None):
        '''Adds a menu item that triggers the given callback when clicked

        Passes the given list of uuids at time of triggering.  If no uuids
        are specified, it simply echos the command name to stdout instead.'''
        menu_item = gtk.MenuItem(text)
        if uuids is not None:
            menu_item.connect("activate", callback, uuids, data)
        else:
            menu_item.connect("activate", self.on_echo_only, text)
        menu_item.show()
        self.append(menu_item)

    def _add_priority_submenu(self, uuids):
        text = "Priority..."
        submenu = gtk.Menu()
        for priority in self._taskwarrior.priorities:
            submenu_item = gtk.MenuItem(priority)
            submenu_item.show()
            submenu.append(submenu_item)
            if uuids is not None:
                submenu_item.connect("activate", self.on_task_set_priority, uuids, priority)
            else:
                submenu_item.connect("activate", self.on_echo_only, text)

        menu_item = gtk.MenuItem(text)
        menu_item.set_submenu(submenu)
        menu_item.show()
        self.append(menu_item)

    def _add_wait_submenu(self, uuids):
        text = "Wait..."
        submenu = gtk.Menu()

        wait_periods = {}
        wait_periods['minutes'] = {'waits': ['1'], 'single':'min',   'plural':'min',    'designator':'min'}
        wait_periods['hours']   = {'waits': ['1'], 'single':'hr',    'plural':'hrs',    'designator':'hr'}
        wait_periods['days']    = {'waits': ['1'], 'single':'day',   'plural':'days',   'designator':'d'}
        wait_periods['weeks']   = {'waits': ['1'], 'single':'week',  'plural':'weeks',  'designator':'wk'}
        wait_periods['months']  = {'waits': ['1'], 'single':'month', 'plural':'months', 'designator':'month'}
        wait_periods['years']   = {'waits': ['1'], 'single':'year',  'plural':'years',  'designator':'yr'}

        if self._config is not None:
            wait_periods['minutes']['waits'] = self._config.get('waits.minutes', [])
            wait_periods['hours']['waits']   = self._config.get('waits.hours',   [])
            wait_periods['days']['waits']    = self._config.get('waits.days',    [])
            wait_periods['weeks']['waits']   = self._config.get('waits.weeks',   [])
            wait_periods['months']['waits']  = self._config.get('waits.months',  [])
            wait_periods['years']['waits']   = self._config.get('waits.years',   [])

        schedule = self._taskwarrior.waiting_tasks_schedule
        schedule_days = schedule.keys()
        schedule_days.sort()

        for p in ['minutes', 'hours', 'days', 'weeks', 'months', 'years']:
            periods = wait_periods[p]
            for wait in periods['waits']:
                if not wait.isdigit():
                    continue

                wait = int(wait)
                if wait == 0:
                    continue
                elif wait == 1:
                    period = periods['single']
                else:
                    period = periods['plural']

                count_str = ''
                if p == 'days':
                    day = schedule_days[wait-1]
                    count = len(schedule[day])
                    if count > 0:
                        count_str = " (%d)" %(count)
                elif p == 'weeks':
                    count = 0
                    for weekday in range(0,7):
                        day_num = wait*7+weekday
                        if len(schedule_days) > day_num:
                            day = schedule_days[day_num]
                            count += len(schedule[day])
                    if count > 0:
                        count_str = " (%d)" %(count)
                elif p == 'months':
                    count = 0
                    for day_of_month in range(0,30):
                        day_num = wait*30+day_of_month
                        if len(schedule_days) > day_num:
                            day = schedule_days[day_num]
                            count += len(schedule[day])
                    if count > 0:
                        count_str = " (%d)" %(count)

                submenu_item = gtk.MenuItem("%d %s %s" %(wait, period, count_str))
                submenu_item.show()
                submenu.append(submenu_item)
                if uuids is not None:
                    submenu_item.connect("activate", self.on_task_set_wait, uuids,
                                         wait, periods['designator'])
                else:
                    submenu_item.connect("activate", self.on_echo_only, text)

        menu_item = gtk.MenuItem(text)
        menu_item.set_submenu(submenu)
        menu_item.show()
        self.append(menu_item)

    def _add_project_submenu(self, uuids):
        text = "Project..."
        submenu = gtk.Menu()
        if self._config is not None and 'projects' in self._config.keys():
            projects = self._config['projects']
        elif len(self._taskwarrior.projects) > 0:
            projects = self._taskwarrior.projects
        else:
            projects = ['work', 'taskhelm', 'yardwork', 'office']
        for project in projects:
            submenu_item = gtk.MenuItem(project)
            submenu_item.show()
            submenu.append(submenu_item)
            if uuids is not None:
                submenu_item.connect("activate", self.on_task_set_project, uuids, project)
            else:
                submenu_item.connect("activate", self.on_echo_only, text)

        menu_item = gtk.MenuItem(text)
        menu_item.set_submenu(submenu)
        menu_item.show()
        self.append(menu_item)

    def set_uuids(self, uuids=None):
        # Out with the old...
        self._clear_menu_items()

        # In with the new...
        self._add_menu_item('Start',                   self.on_task_start,        uuids)
        self._add_menu_item('Stop',                    self.on_task_stop,         uuids)

        self._add_priority_submenu(uuids)
        self._add_project_submenu(uuids)
        self._add_wait_submenu(uuids)

        self._add_menu_item('Edit',                  self.on_task_edit,           uuids)
        self._add_menu_item('Done',                  self.on_task_done,           uuids)
        self._add_menu_item('Delete',                self.on_task_delete,         uuids)

    def _get_task(self, uuid):
        dbg("_get_task: self._taskwarrior = %s" %(self._taskwarrior))
        return Task(uuid=uuid, taskwarrior=self._taskwarrior, config=self._config)

    def on_echo_only(self, widget, text):
        print text

    def on_task_start(self, widget, uuids, data=None):
        # TODO: Can we start the whole selection at once?
        for uuid in uuids:
            task = self._get_task(uuid)
            task.set_start()
            dbg("start %s" %(uuid))
            dbg(self._taskwarrior.last_command)
        self._emit_data_changed()

    def on_task_stop(self, widget, uuids, data=None):
        # TODO: Can we start the whole selection at once?
        for uuid in uuids:
            task = self._get_task(uuid)
            task.set_stop()
            dbg("start %s" %(uuid))
            dbg(self._taskwarrior.last_command)
        self._emit_data_changed()

    def on_task_set_priority(self, widget, uuids, priority):
        if priority is not None:
            self._taskwarrior.set_priority(uuids, priority)
            self._emit_data_changed()

    def on_task_set_project(self, widget, uuids, project_name):
        if project_name is not None:
            self._taskwarrior.set_project(uuids, project_name)
            self._emit_data_changed()

    def on_task_edit(self, widget, uuids, data=None):
        for uuid in uuids:
            task = Task(uuid)
            text_view = TaskEditor(task)
            # Propagate changes from editor(s) back up to browser
            task_view.connect('data-changed', self._emit_data_changed)

    def on_task_set_wait(self, widget, uuids, wait_time_qty, wait_time_period):
        self._taskwarrior.set_wait(uuids, wait_time_qty, wait_time_period)
        dbg(self._taskwarrior.last_command)
        self._emit_data_changed()

    def on_task_done(self, widget, uuids, data=None):
        # TODO: All at once
        for uuid in uuids:
            dbg("on_task_done: Getting task")
            task = self._get_task(uuid)
            dbg("on_task_done: set_done()")
            task.set_done()
            dbg("done %s" %(uuid))
        self._emit_data_changed()

    def on_task_delete(self, widget, uuids, data=None):
        self._taskwarrior.delete(uuids)
        self._emit_data_changed()


if __name__ == "__main__":
    import sys, os.path
    sys.path.insert(0, os.path.realpath(os.path.join(
        os.path.dirname(__file__), "../..")))

    from Taskhelm.taskwarrior import TaskWarrior

    class Example:
        def __init__(self):
            # create a new window
            window = gtk.Window(gtk.WINDOW_TOPLEVEL)
            window.set_size_request(200, 100)
            window.set_title("GTK Menu Test")
            window.connect("delete_event", lambda w,e: gtk.main_quit())

            taskwarrior = TaskWarrior()

            # Init the menu-widget, and remember -- never
            # show() the menu widget!!
            # This is the menu that holds the menu items, the one that
            # will pop up when you click on the "Root Menu" in the app
            menu = TaskBrowserContextMenu()
            menu.setup(taskwarrior=taskwarrior)

            # This is the root menu, and will be the label
            # displayed on the menu bar.  There won't be a signal handler attached,
            # as it only pops up the rest of the menu when pressed.
            root_menu = gtk.MenuItem("Root Menu")
            root_menu.show()

            # Now we specify that we want our newly created "menu" to be the
            # menu for the "root menu"
            root_menu.set_submenu(menu)

            # A vbox to put a menu and a button in:
            vbox = gtk.VBox(False, 0)
            window.add(vbox)
            vbox.show()

            # Create a menu-bar to hold the menus and add it to our main window
            menu_bar = gtk.MenuBar()
            vbox.pack_start(menu_bar, False, False, 2)
            menu_bar.show()

            # Create a button to which to attach menu as a popup
            button = gtk.Button("press me")
            button.connect_object("event", self.button_press, menu)
            vbox.pack_end(button, True, True, 2)
            button.show()

            # And finally we append the menu-item to the menu-bar -- this is the
            # "root" menu-item I have been raving about =)
            menu_bar.append (root_menu)

            # always display the window as the last step so it all splashes on
            # the screen at once.
            window.show()

        # Respond to a button-press by posting a menu passed in as widget.
        #
        # Note that the "widget" argument is the menu being posted, NOT
        # the button that was pressed.
        def button_press(self, widget, event):
            if event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
                widget.popup(None, None, None, event.button, event.time)
                # Tell calling code that we have handled this event the buck
                # stops here.
                return True
            # Tell calling code that we have not handled this event pass it on.
            return False

    Example()
    gtk.main()
