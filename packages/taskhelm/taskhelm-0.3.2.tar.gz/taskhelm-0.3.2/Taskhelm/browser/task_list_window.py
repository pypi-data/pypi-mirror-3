#!/usr/bin/env python

import gobject
import pygtk
pygtk.require('2.0')
import gtk
import re

if __name__ != "__main__":
    from list_view import TaskListView
    from ..utils.types.priority import priority
    from ..widgets.list_column import Column
    from ..widgets.list_store import DictListStore
    from ..taskwarrior import TaskWarrior
    from ..task import Task
    from ..editor.editor import TaskEditor
    from context_menu import TaskBrowserContextMenu

else:
    import sys, os.path
    sys.path.insert(0, os.path.realpath(os.path.join(
        os.path.dirname(__file__), "../..")))

    from Taskhelm.browser.list_view import TaskListView
    from Taskhelm.utils.types.priority import priority
    from Taskhelm.widgets.list_column import Column
    from Taskhelm.widgets.list_store import DictListStore
    from Taskhelm.taskwarrior import TaskWarrior
    from Taskhelm.task import Task
    from Taskhelm.editor.editor import TaskEditor
    from context_menu import TaskBrowserContextMenu


def compare_priorities_reverse(model, row1, row2, user_data):
    value1 = priority(model.get_value(row1, 3))
    value2 = priority(model.get_value(row2, 3))
    return cmp(value2, value1)

class TaskListWindow(gtk.ScrolledWindow):

    columns = [
        Column('uuid',        str,  'uuid', visible=False ),
        Column('id',          str,  'ID', visible=False ),
        Column('project',     str,  'Project' ),
        Column('priority',    str,  'Priority', sort=compare_priorities_reverse ),
        Column('description', str,  'Description', search=True ),
        Column('tags',        str,  'Tags', visible=False ),
        ]

    def _get_column(self, columnname):
        i = 0
        for c in TaskListWindow.columns:
            if c.name == columnname:
                return i
            i += 1

    def __init__(self, config=None):
        # TODO: Instead of passing config downward, make it a global singleton?
        gtk.ScrolledWindow.__init__(self)

        self._config = config
        self.taskwarrior = TaskWarrior()

        if self.taskwarrior.is_taskwarrior_virgin:
            # This is the user's first time!  Add some default tasks
            # TODO: Call task import /var/lib/taskhelm/default_tasks.json
            pass

        self.liststore = DictListStore(TaskListWindow.columns)

        # add bug data to model
        self.states = self.taskwarrior.priorities
        self.projects = self.taskwarrior.projects
        self.liststore.set_data(self.taskwarrior.pending_tasks)
        self.refilter()
        self.show_states = self.states[:]
        self.show_projects = self.projects[:]
        self.include_tags = None # TODO
        self.exclude_tags = None # TODO
        self.liststore.set_sort_column_id(self._get_column('project'), gtk.SORT_ASCENDING)
        self.liststore.model_filter.set_visible_func(self.visible_cb, self.show_states)
        for col in range(0, len(self.columns)):
            column = self.columns[col]
            if column.sort is not None:
                self.liststore.model_filtersort.set_sort_func(col, column.sort, None)

        # create the TreeView
        self.treeview = TaskListView(TaskListWindow.columns,
                                     taskwarrior=self.taskwarrior,
                                     liststore=self.liststore,
                                     config = self._config)
        self.treeview.connect('data-changed', self.on_data_changed)
        self.treeview.set_model(self.liststore.model_filtersort)
        self.add(self.treeview)

        # create the context menu
        menu = TaskBrowserContextMenu(taskwarrior=self.taskwarrior,
                                      liststore=self.liststore,
                                      config=self._config)
        menu.connect('data-changed', self.treeview.on_data_changed)
        self.treeview.connect_object("event", self.treeview.on_button_press, menu)

    def on_data_changed(self, widget, tid=None):
        self.refresh()

    # visibility determined by state matching active toggle buttons
    def visible_cb(self, model, iter, data):
        priorities = data
        projects = self.show_projects
        include_tags = self.include_tags
        exclude_tags = self.exclude_tags
        valid_priority = True
        valid_project = True
        valid_include_tags = True
        valid_exclude_tags = True
        if priorities:
            valid_priority = model.get_value(iter, self._get_column('priority')) in priorities
        if projects:
            valid_project = model.get_value(iter, self._get_column('project')) in projects
        if include_tags:
            valid_include_tags = model.get_value(iter, self._get_column('tags')) in include_tags
        if exclude_tags:
            valid_exclude_tags = model.get_value(iter, self._get_column('tags')) not in exclude_tags
        return valid_priority and valid_project and valid_include_tags and valid_exclude_tags

    def refilter(self):
        self.liststore.model_filter.refilter()

    def refresh(self):
        self.taskwarrior.refresh()
        self.liststore.set_data(self.taskwarrior.pending_tasks)
        self.emit('data-refreshed')

    def _get_task(self, uuid):
        return Task(uuid=uuid, taskwarrior=self.taskwarrior, config=self._config)

    @property
    def count(self):
        return self.treeview.count

    def set_selection_status_done(self):
        '''Marks selected tasks as done, refreshing the display'''
        # TODO: Does this belong here or in the TaskListView?
        selection = self.treeview.get_selection()
        for uuid in self.get_task_uuids(selection):
            task = self._get_task(uuid)
            print task.set_done()
        self.refresh()

    def _extract_project(self, description):
        re_project_1 = re.compile(r'^(.*)\s*pro[ject]*:([^\s]+)\s*(.*)$')
        m = re_project_1.match(description)
        if m:
            description = "%s %s" %(m.group(1).strip(), m.group(3).strip())
            return m.group(2), description.strip()

        re_project_2 = re.compile(r'^([\w\-\.]+)\s+-\s+(.*)$')
        m = re_project_2.match(description)
        if m:
            return m.group(1), m.group(2).strip()

        return None, description

    def add_task(self, description):
        if not description:
            return False

        project, description = self._extract_project(description)
        self.taskwarrior.add(description, project)
        print self.taskwarrior.last_command
        self.refresh()
        return True

    def get_task_uuids(self, selection):
        return self.treeview.get_task_uuids(selection)

gobject.signal_new('data-refreshed', TaskListWindow, gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ())


if __name__ == "__main__":
    tlw = TaskListWindow()

    print tlw._extract_project("no project here")
    print tlw._extract_project("pro:my-project Task in my project")
    print tlw._extract_project("this pro:my_proj is my project")
    print tlw._extract_project("pro:solo.project")
    print tlw._extract_project("project - foo bar")
    print tlw._extract_project("this-project - is cool")
    print tlw._extract_project("notta-project")

