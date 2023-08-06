#!/usr/bin/env python

import gobject
import pygtk
pygtk.require('2.0')
import gtk

COL_ID    = 0
COL_NAME  = 1
COL_LABEL = 2
COL_OBJ   = 3
COL_COLOR = 4
COL_COUNT = 5
COL_SEP   = 6

# TODO: Rename to ProjectView; add a ProjectPage derived from notebook page class
class ProjectPane(gtk.TreeView):
    __gsignals__ = {'selection-changed': (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, ()) }
    DND_ID_PROJECT = 0
    DND_ID_TASK = 1
    DND_TARGETS = [
        ('taskhelm/project-iter-str', gtk.TARGET_SAME_WIDGET, DND_ID_PROJECT),
        ('taskhelm/task-iter-str', gtk.TARGET_SAME_APP, DND_ID_TASK)
        ]
    def __init__(self):
        # TODO: To follow task_list_window, this should be set externally in a ProjectWindow (or ProjectPage?)
        # TODO: Possibly I could create a more general purpose TreeView subclass to use (like from Kiwi?)
        gtk.TreeView.__init__(self)

        self.COL_INDEX = 0
        self.projects = []
        self.updating_projects = False

        # create the TreeViewColumn to display the data
        self.tvcolumn_project = gtk.TreeViewColumn('Project')
        self.tvcolumn_count = gtk.TreeViewColumn('#')

        # add tvcolumn to treeview
        self.set_show_expanders(False)
        self.set_grid_lines(gtk.TREE_VIEW_GRID_LINES_NONE)
        self.set_enable_tree_lines(False)
        self.append_column(self.tvcolumn_project)
        self.append_column(self.tvcolumn_count)

        # create a CellRendererText to render the data
        self.cell = gtk.CellRendererText()
        self.cell_count = gtk.CellRendererText()

        # add the cell to the tvcolumn
        self.tvcolumn_project.pack_start(self.cell, True)
        self.tvcolumn_project.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        self.tvcolumn_project.add_attribute(self.cell, 'text', 0)

        self.tvcolumn_count.pack_start(self.cell_count, True)
        self.tvcolumn_count.set_alignment(0.5)
        self.tvcolumn_count.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
        self.tvcolumn_count.set_fixed_width(20)

        self.tvcolumn_count.add_attribute(self.cell_count, 'text', 1)
        self.tvcolumn_count.add_attribute(self.cell_count, 'xalign', 2)

        # Make it searchable
        self.set_search_column(0)

        # Allow multiple selection
        tree_sel = self.get_selection()
        tree_sel.set_mode(gtk.SELECTION_MULTIPLE)
        tree_sel.connect('changed', self.on_changed)
        tree_sel.select_all()

        # Allow sorting on the column
        self.tvcolumn_project.set_sort_column_id(0)
        self.tvcolumn_count.set_sort_column_id(1)

        # Drag and drop
        self.enable_model_drag_source(
            gtk.gdk.BUTTON1_MASK,
            self.DND_TARGETS,
            gtk.gdk.ACTION_DEFAULT | gtk.gdk.ACTION_MOVE)
        self.enable_model_drag_dest(
            self.DND_TARGETS,
            gtk.gdk.ACTION_DEFAULT)
        self.drag_source_set(
            gtk.gdk.BUTTON1_MASK,
            self.DND_TARGETS,
            gtk.gdk.ACTION_DEFAULT | gtk.gdk.ACTION_MOVE)
        self.drag_dest_set(
            gtk.DEST_DEFAULT_ALL,
            self.DND_TARGETS,
            gtk.gdk.ACTION_DEFAULT | gtk.gdk.ACTION_MOVE)

        # Signals
        self.connect('button-press-event', self.on_button_press_event)
        #self.connect('row-expanded', self.on_row_expanded)
        #self.connect('row-collapsed', self.on_row_collapsed)
        self.connect('drag-drop', self.on_drag_drop)
        self.connect('drag-data-get', self.on_drag_data_get)
        self.connect('drag-data-received', self.on_drag_data_received)

    def update_projects(self, projects):
        # Prevent change handler from getting triggered
        self.updating_projects = True

        project_names =  projects.keys()
        project_names.sort()

        treestore = self.get_model()
        if treestore is None:
            return
        treestore.clear()
        for project_name in project_names:
            piter = treestore.append(None, [project_name, projects[project_name], 1.0])
            #for child in range(3):
            #    self.treestore.append(piter, ['child %i of %s' %
            #                                  (child, parent)])
        self.updating_projects = False

    def on_changed(self, widget):
        if self.updating_projects:
            return
        tree_sel = self.get_selection()
        model, selected_paths = tree_sel.get_selected_rows()
        iters = [model.get_iter(path) for path in selected_paths]
        ts = self.get_model()
        self.projects = [ts.get_value(iter, self.COL_INDEX) for iter in iters]
        self.emit("selection-changed")

    def on_button_press_event(self, treeview, event):
        # TODO: On double-click, launch a project configuration dialog
        pass

    def on_drag_drop(self, treeview, context, selection, info, timestamp):
        self.emit_stop_by_name('drag-drop')

    def on_drag_data_get(self, treeview, context, selection, info, timestamp):
        """Extract data from the source of the DnD operation.

        Here the id of the parent and the id of the selected item
        is passed to the destination.
        """
        selection = treeview.get_selection()
        model, iterator = selection.get_selected()
        iter_str = model.get_string_from_iter(iterator)
        selection.set('taskhelm/project-iter-str', 0, iter_str)

    def on_drag_data_received(self, treeview, context, x, y, selection, info, timestamp):
        # TODO: Move these three into a self.project_tree_model() routine or some such
        model = treeview.get_model()
        model_filter = model.get_model()
        project_tree_model = model_filter.get_model()

        drop_info = treeview.get_dest_row_at_pos(x, y)

        if drop_info:
            path, position = drop_info
            iterator = model.get_iter(path)
            if (position == gtk.TREE_VIEW_DROP_BEFORE or
                position == gtk.TREE_VIEW_DROP_AFTER):
                parent_iter = model.iter_parent(iterator)
            else:
                parent_iter = iterator
        else:
            parent_iter = None

        parent_iter_tagtree = None
        if parent_iterator:
            parent_iter_filter = model.convert_iter_to_child_iter(
                None, parent_iter)
            parent_iter_tagtree = model_filter.convert_iter_to_child_iter(
                parent_iter_filter)

        if info == self.DND_ID_PROJECT:
            drag_iter = model.get_iter_from_string(selection.data)
            drag_iter_filter = model.convert_iter_to_child_iter(None, drag_iter)
            drag_iter_project_tree = model_filter.convert_iter_to_child_iter(
                drag_iter_filter)
            project_tree_model.move_project(
                parent_iter_project_tree, drag_iter_project_tree)
        elif info == self.DND_ID_TASK:
            if not drop_info:
                # Can't drop task onto root
                return
            project = model.get_value(iterator, COL_OBJ)
            src_model = context.get_source_widget().get_model()
            src_str_iters = selection.data.split(',')
            src_iters = [src_model.get_iter_from_string(i) for i in src_str_iters]
            tasks = [src_model.get_value(i, TASKTREE_COL_OBJ) for i in src_iters]
            for task in tasks:
                task.set_project(project.get_name())

        self.emit_stop_by_name('drag-data-received')

if __name__ == "__main__":
    class ProjectWindow:
        def __init__(self):
            # Create a new window
            self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
            self.window.set_title("Project TreeView")
            self.window.set_size_request(300, 600)
            self.window.connect("delete_event", self.delete_event)

            self.project_pane = ProjectPane()

            self.window.add(self.project_pane.treeview)
            self.window.show_all()

        # close the window and quit
        def delete_event(self, widget, event, data=None):
            gtk.main_quit()
            return False

    tvexample = ProjectWindow()
    gtk.main()
