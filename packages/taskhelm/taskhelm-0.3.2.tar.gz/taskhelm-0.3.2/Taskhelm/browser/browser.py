#!/usr/bin/env python

import os
import gobject
import pygtk
pygtk.require('2.0')
import gtk

from task_list_window import TaskListWindow
from project_tree import ProjectPane
from ..utils.paths import find_datadir
from ..utils.debug import dbg

class TasksBrowser(object):
    _app_name = "Taskhelm"

    def __init__(self, config=None):
        self._status_bar_statistics = [
            "Showing",
            "Pending",
            "Total",
            "New this week",
            "Done last week",
            "Done this week"]
        self._status_bar_widgets = {}

        # Configuration
        # TODO: Turn configuration into its own class
        self._config = config
        self.opt_show_menu_bar = config.get('show_menu_bar', False) # TODO: Rename these menu_bar_visibility, etc.
        self.opt_show_tool_bar = config.get('show_tool_bar', True)
        self.opt_show_status_bar = config.get('show_status_bar', True)
        self.opt_show_left_pane = config.get('show_left_pane', False)
        self.opt_show_detail_pane = config.get('show_detail_pane', False)
        self.opt_show_documentation = config.get('show_documentation', False)
        self.opt_browser_maximized = config.get('browser_maximized', False)
        self.opt_browser_width = int(config.get('browser_width', -1))
        self.opt_browser_height = int(config.get('browser_height', -1))
        self.opt_browser_pos_x = int(config.get('browser_pos_x', -1))
        self.opt_browser_pos_y = int(config.get('browser_pos_y', -1))
        self.opt_left_pane_width = int(config.get('left_pane_width', -1))
        self.opt_detail_pane_height = int(config.get('detail_pane_height', -1))
        self.opt_projects_collapsed = config.get('projects_collapsed', False) # TODO: Implement
        self.opt_tasks_collapsed = config.get('tasks_collapsed', False) # TODO: Implement
        self.opt_tasks_notes_preview = config.get('tasks_notes_preview', False) # TODO: Implement
        self.opt_tasks_sort = config.get('tasks_sort', None) # TODO: Implement
        self.opt_tasks_filters = config.get('tasks_filters', None) # TODO: Implement
        self.opt_tasks_include_tags = config.get('tasks_include_tags', None)
        self.opt_tasks_exclude_tags = config.get('tasks_exclude_tags', None)

        self.accelerators = gtk.AccelGroup()

        # Top level UI containers
        self.top_vbox = gtk.VBox()
        self.top_hpane = gtk.HPaned()
        inner_vbox = gtk.VBox()
        self.inner_vpane = gtk.VPaned()

        # TODO: Setup the three notebooks

        self.tasklist_window = self._create_tasklist_window()

        # Create UI elements
        self.window = self._create_top_window()
        self.menu_bar = self._create_menu_bar()
        self.tool_bar = self._create_tool_bar()
        self.left_pane = self._create_left_pane()
        self.quick_add_bar = self._create_quick_add_bar()
        self.detail_pane = self._create_detail_pane()
        self.status_bar = self._create_status_bar()

        # Assemble the UI
        self.inner_vpane.pack1(self.tasklist_window, resize=True)
        self.inner_vpane.pack2(self.detail_pane, resize=False)
        inner_vbox.pack_start(self.quick_add_bar, expand=False)
        inner_vbox.pack_end(self.inner_vpane)
        self.top_hpane.pack1(self.left_pane)
        self.top_hpane.pack2(inner_vbox)
        if self.menu_bar is not None:
            self.top_vbox.pack_start(self.menu_bar, expand=False)
        if self.tool_bar is not None:
            self.top_vbox.pack_start(self.tool_bar, expand=False)
        self.top_vbox.pack_start(self.top_hpane, expand=True)
        if self.status_bar is not None:
            self.top_vbox.pack_start(self.status_bar, expand=False)
        self.window.add(self.top_vbox)
        self.window.add_accel_group(self.accelerators)

        # Update positions
        self.top_hpane.set_position(self.opt_left_pane_width)
        self.inner_vpane.set_position(self.opt_detail_pane_height)

        # Where is our data dir?
        datadir = find_datadir('taskhelm')
        assert datadir is not None, "Could not find data dir"

        # Icons
        icon_file = os.path.join(datadir, 'icons', 'helm.svg')
        #gtk.windowset_default_icon_name("icon.png")
        pixbuf = gtk.gdk.pixbuf_new_from_file(icon_file)
        self.window.set_icon(pixbuf)

        # Project name completion
        self.project_list_model = gtk.ListStore(gobject.TYPE_STRING)
        self.project_completion = None
        if self.left_pane is not None:
            for i in self.left_pane.projects:
                self.project_list_model.append([i])
            self.project_completion = gtk.EntryCompletion()
            self.project_completion.set_model(self.project_list_model)
            self.project_completion.set_text_column(0)
            self.project_completion.set_match_func(self.project_match_func, 0)
            self.project_completion.set_inline_completion(True)
            self.project_completion.set_inline_selection(True)
            self.project_completion.set_popup_single_match(False)

        # Refresh data
        self.update_window_title()
        self.update_toolbar()
        self.update_project_list()
        self.update_status_bar()
        self.window.show_all()

    def _create_top_window(self):
        window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        if self.opt_browser_height > -1 and self.opt_browser_width > -1:
            window.set_default_size(self.opt_browser_width, self.opt_browser_height)
        else:
            width = 600
            height = 400
            screen_width, screen_height = gtk.gdk.get_default_root_window().get_size()
            if screen_width > 1024:
                width = min(1024, screen_width * 2 / 3)
            if screen_height > 800:
                height = min(1024, screen_height * 2 / 3)
            window.set_default_size(width, height)

        if self.opt_browser_pos_x > -1 and self.opt_browser_pos_y > -1:
            window.move(self.opt_browser_pos_x, self.opt_browser_pos_y)
        else:
            window.set_position(gtk.WIN_POS_CENTER);

        window.connect("delete-event", self.on_delete)
        window.connect("window-state-event", self.on_window_state)
        window.connect("configure-event", self.on_window_configure)
        window.connect("size-allocate", self.on_size_allocate)
        if self.opt_browser_maximized:
            window.maximize()
        return window

    def _create_menu_bar(self):
        if self.opt_show_menu_bar:
            from menu_bar import TaskBrowserMenuBar
            menu_bar = TaskBrowserMenuBar(
                taskwarrior=self.tasklist_window.taskwarrior)
            menu_bar.connect('data-changed', self.tasklist_window.on_data_changed)
            # TODO: Accelerators:
            #self._add_accelerator_for_widget(agr, "view_sidebar",   "F9")
            #self._add_accelerator_for_widget(agr, "file_quit",      "<Control>q")
            #self._add_accelerator_for_widget(agr, "edit_undo",      "<Control>z")
            #self._add_accelerator_for_widget(agr, "edit_redo",      "<Control>y")
            #self._add_accelerator_for_widget(agr, "new_task_mi",    "<Control>n")
            #self._add_accelerator_for_widget(agr, "new_subtask_mi", "<Control><Shift>n")
            #self._add_accelerator_for_widget(agr, "dismiss_mi",     "<Control>i")
            #self._add_accelerator_for_widget(agr, "delete_mi",      "Cancel")
            #self._add_accelerator_for_widget(agr, "tcm_addtag",     "<Control>t")
            #self._add_accelerator_for_widget(agr, "view_closed",    "<Control>F9")
            #
            # TODO: Also add accelerators <Control>1-9 for adding day waits,
            #       <Alt>1-9 for weeks, and <Control><Alt>1-9 for months

            return menu_bar

    def _create_tool_bar(self):
        # TODO: Break this out into a separate tool_bar class
        #       that can also be shared with task editor
        if not self.opt_show_tool_bar:
            return
        self.bbox = gtk.HBox()
        self.bbox.set_homogeneous(False)
        return self.bbox

    def _create_left_pane(self):
        left_pane = ProjectPane()
        if not self.opt_show_left_pane:
            return left_pane
        treestore = gtk.TreeStore(str, str, int)
        left_pane.set_model(treestore)
        left_pane.connect('selection-changed', self.on_project_selection_changed)
        return left_pane

    def _create_quick_add_bar(self):
        quick_add_hbox = gtk.HBox()
        self.quick_add_entry = gtk.Entry()
        quick_add_hbox.pack_start(self.quick_add_entry)
        add_button = gtk.Button("Add")
        quick_add_hbox.pack_end(add_button, False, 5, 5)
        self.quick_add_entry.connect("activate", self.on_new_task, self, gtk.RESPONSE_OK)
        add_button.connect("clicked", self.on_new_task, self)
        self.add_accelerator(self.quick_add_entry, "<Control>l", signal="grab-focus")
        return quick_add_hbox

    def _create_tasklist_window(self):
        tasklist_window = TaskListWindow(self._config)
        tasklist_window.connect('data-refreshed', self.on_data_refreshed)
        return tasklist_window

    def _create_detail_pane(self):
        detail_pane = gtk.Frame()
        detail_pane.set_shadow_type(gtk.SHADOW_IN)
        detail_pane.set_size_request(-1, 0)
        return detail_pane

    def _create_status_bar(self):
        if not self.opt_show_status_bar:
            return
        statusbar = gtk.HBox()
        statusbar.set_homogeneous(False)

        for key in self._status_bar_statistics:
            self._status_bar_widgets[key] = gtk.Label("%s: ??" %(key))
            statusbar.pack_start(self._status_bar_widgets[key])
            statusbar.set_child_packing(
                self._status_bar_widgets[key],
                True, False, 6, gtk.PACK_START)

        return statusbar

    def add_accelerator(self, widget, accelerator, signal="activate"):
        if accelerator is not None:
            if self.opt_show_documentation:
                print accelerator, widget.get_tooltip_text()
            key, mod = gtk.accelerator_parse(accelerator)
            widget.add_accelerator(signal, self.accelerators, key, mod, gtk.ACCEL_VISIBLE)

    # TODO: This should move into a tool_bar class
    def add_toolbar_button(self, tb, item_name, handler, tooltip_text=None, accelerator=None):
        b = gtk.Button(item_name)
        tb.pack_start(b)
        tb.set_child_packing(b, 0, 0, 0, gtk.PACK_START)
        b.connect("clicked", handler, self)
        if tooltip_text is not None:
            b.set_tooltip_text(tooltip_text)
        self.add_accelerator(b, accelerator)

    # TODO: This should move into a tool_bar class
    def add_toolbar_toggle(self, tb, item_name, handler, tooltip_text=None, accelerator=None):
        b = gtk.ToggleButton(item_name)
        tb.pack_end(b)
        tb.set_child_packing(b, 0, 0, 0, gtk.PACK_END)
        b.set_active(True)
        b.connect('toggled', handler)
        if tooltip_text is not None:
            b.set_tooltip_text(tooltip_text)
        self.add_accelerator(b, accelerator)

    def add_detail_page(self, notebook, label, page):
        notebook.append_page(page, label)
        if notebook.get_n_pages() > 1:
            notebook.set_show_tabs(True)
        page_num = notebook.page_num(page)
        notebook.set_tab_detachable(page, True)
        notebook.set_tab_reorderable(page, True)
        notebook.set_current_page(page_num)
        notebook.show_all()
        return page_num

    def _remove_page(self, notebook, page):
        if page:
            page.hide()
            notebook.remove(page)
        if notebook.get_n_pages() == 1:
            notebook.set_show_tabs(False)
        elif notebook.get_n_pages() == 0:
            notebook.hide()

    def project_match_func(self, completion, key, iter, column):
        model = completion.get_model()
        text = model.get_value(iter, column)
        if text:
            return text.startswith(key)
        return False

    def update_project_list(self):
        if self.left_pane is None:
            return
        projects = self.tasklist_window.taskwarrior.pending_projects
        self.left_pane.update_projects(projects)

    def update_window_title(self):
        count = self.tasklist_window.taskwarrior.num_pending

        if count == 0:
            state = "no pending tasks"
        elif count == 1:
            state = "1 pending task"
        else:
            state = "%d pending tasks" %(count)
        self.window.set_title("%s - %s" %(state, self._app_name))

    def update_toolbar(self):
        # TODO: Clear existing toolbar items
        self.add_toolbar_button(
            self.bbox, "Refresh", self.on_refresh_clicked,
            "Reload the tasks from taskwarrior", "<Control>r")
        self.add_toolbar_button(
            self.bbox, "Done", self.on_done_clicked,
            "Mark the task as completed", "<Control>d")

        # Importance toggles
        states = self.tasklist_window.states
        states.reverse()
        for state in states:
            key = "<Control><Shift>%s" %(state)
            if state == '-':
                key = '<Control><Shift>underscore'
            self.add_toolbar_toggle(
                self.bbox, state, self.on_check_button_toggled,
                "Toggle showing tasks of priority %s" %(state), key)


    def update_configuration(self):
        self._config['left_pane_width'] = self.top_hpane.get_position()
        if self.menu_bar:
            self._config['show_menu_bar'] = self.menu_bar.get_property('visible')
        if self.tool_bar:
            self._config['show_tool_bar'] = self.tool_bar.get_property('visible')
        if self.status_bar:
            self._config['show_status_bar'] = self.status_bar.get_property('visible')
        if self.left_pane:
            self._config['show_left_pane'] = self.left_pane.get_property('visible')
        if self.detail_pane:
            self._config['show_detail_pane'] = self.detail_pane.get_property('visible')
        self._config['browser_maximized'] = self.opt_browser_maximized
        self._config['browser_width'] = self.opt_browser_width
        self._config['browser_height'] = self.opt_browser_height
        self._config['browser_pos_x'] = self.opt_browser_pos_x
        self._config['browser_pos_y'] = self.opt_browser_pos_y
        self._config['left_pane_width'] = self.opt_left_pane_width
        self._config['detail_pane_height'] = self.inner_vpane.get_position()

        # TODO
        # filters
        #sort_column, sort_order = self.task_modelsort.get_sort_column_id()

    def update_status_bar(self):
        for item in self._status_bar_statistics:
            if item == 'Showing':
                count = self.tasklist_window.count
                self._status_bar_widgets[item].set_text("%s: %d" %(item, count))
            else:
                if item in self._status_bar_widgets:
                    count = self.tasklist_window.taskwarrior.get_statistic(item)
                    self._status_bar_widgets[item].set_text("%s: %d" %(item, count))

    def on_delete(self, widget, event, data=None):
        self.update_configuration()
        gtk.main_quit()
        return False

    def on_window_configure(self, widget=None, data=None):
        x, y = self.window.get_position()
        self.opt_browser_pos_x = x
        self.opt_browser_pos_y = y

    def on_size_allocate(self, widget=None, data=None):
        w, h = self.window.get_size()
        self.opt_browser_width = w
        self.opt_browser_height = h

    def on_window_state(self, widget=None, event=None):
        if event.new_window_state == gtk.gdk.WINDOW_STATE_MAXIMIZED:
            self.opt_browser_maximized = True
        else:
            self.opt_browser_maximized = False

    def on_refresh_clicked(self, widget, event, data=None):
        self.tasklist_window.refresh()

    def on_done_clicked(self, widget, event, data=None):
        self.tasklist_window.set_selection_status_done()

    def on_data_refreshed(self, widget=None):
        self.update_window_title()
        self.update_project_list()
        self.update_status_bar()

    # build list of bug states to show and then refilter
    def on_check_button_toggled(self, tb):
        del self.tasklist_window.show_states[:]
        for b in self.bbox.get_children():
            if type(b) is gtk.ToggleButton and b.get_active():
                self.tasklist_window.show_states.append(b.get_label())
        self.tasklist_window.refilter()
        self.on_data_refreshed()

    def on_new_task(self, widget, event, data=None):
        text = self.quick_add_entry.get_text().strip()
        if self.tasklist_window.add_task(text):
            self.quick_add_entry.set_text('')
        return False

    def on_project_selection_changed(self, widget):
        self.tasklist_window.show_projects = widget.projects
        self.tasklist_window.refilter()
        self.update_window_title()
        self.update_status_bar()

    def on_include_tags_selection_changed(self, widget):
        dbg("Widget tags: %s" %(widget.tags))
        self.tasklist_window.include_tags = widget.tags
        self.tasklist_window.refilter()
        self.update_window_title()
        self.update_status_bar()
        # TODO: Should this also filter the project list?

    def on_exclude_tags_selection_changed(self, widget):
        dbg("Widget tags: %s" %(widget.tags))
        self.tasklist_window.exclude_tags = widget.tags
        self.tasklist_window.refilter()
        self.update_window_title()
        self.update_status_bar()
        # TODO: Should this also filter the project list?

    def on_render(self, window, widget, background_area, cell_area, expose_area, flags):
        cr         = window.cairo_create()
        gdkcontext = gtk.gdk.CairoContext(cr)
        gdkcontext.set_antialias(cairo.ANTIALIAS_NONE)

        x_align = self.get_property("xalign")
        y_align = self.get_property("yalign")
        orig_x  = cell_area.x + int((cell_area.width  - 16*vw_tags -\
                                     self.PADDING*2*(vw_tags-1)) * x_align)
        orig_y  = cell_area.y + int((cell_area.height - 16) * y_align)
        # self.draw_icons()
        # self.draw_rounded_rect_icon()

    def on_color_changed(self, widget):
        gtkcolor = widget.get_current_color()
        strcolor = gtk.color_selection_palette_to_string([gtkcolor])
        # Get selected projects
        for project in []:
            # project.set_color(strcolor)
            pass

    def on_colorchooser(self, widget):
        color_dialog = gtk.ColorSelectionDialog('Choose color')
        colorsel = color_dialog.colorsel
        colorsel.connect('color-changed', self.on_color_changed)

        # Get previous color
        init_color = None
        # color = project.get_color()
        color = None
        if color is not None:
            colorspec = gtk.gdk.color_parse(color)
            colorsel.set_previous_color(colorspec)
            colorsel.set_current_color(colorspec)
            init_color = colorsel.get_current_color()
        response = color_dialog.run()
        if response != gtk.RESPONSE_OK and init_color:
            strcolor = gtk.color_selection_palette_to_string([init_color])
            for project_name in self.get_selected_project_names():
                #project.set_color(strcolor)
                pass
        # Reset selection(?)
        color_dialog.destroy()

    def on_left_pane_toggled(self, widget):
        if self.left_pane.get_property('visible'):
            self.left_pane_vpane.set_active(False)
            self.left_pane.hide()
        else:
            self.left_pane_vpane.set_active(True)
            self.left_pane.show()

    # TODO: Why is this function and the previous so different?
    def on_detail_pane_toggled(self, widget):
        if widget.get_active():
            self.show_detail_pane()
        else:
            self.hide_detail_pane()

    def on_toolbar_toggled(self, widget):
        if widget.get_active():
            self.toolbar.show()
        else:
            self.toolbar.hide()

    def show_left_pane(self):
        self.left_pane.show()

    def hide_left_pane(self):
        self.left_pane.hide()

    def show_detail_pane(self):
        self.detail_pane.show()

    def hide_detail_pane(self):
        # TODO: Delete/deref pages and their data?
        # self.remove_page_from_detail_notebook(closed_task_page)
        self.detail_pane.set_active(False)

    def draw_icon(self, icon):
        if not icon:
            return False
        pixbuf = gtk.icon_theme_get_default().load_icon(icon, 16, 0)
        gdkcontext.set_source_pixbuf(pixbuf, rect_x, rect_y)
        gdkcontext.paint()
        return True

    def draw_rounded_rect_icon(self, color=None):
        if color is None:
            color = "#ddd"

        # Draw rounded rectangle
        color = gtk.gdk.color_parse(color)
        gdkcontext.set_source_color(color)
        self.__roundedrect(gdkcontext, rect_x, rect_y, 16, 16, 8)
        gdkcontext.fill()

        # Outer line
        gdkcontext.set_source_rgba(0, 0, 0, 0.20)
        gdkcontext.set_line_width(1.0)
        self.__roundedrec(gdkcontext, rect_x, rect_y, 16, 16, 8)
        gdkcontext.stroke()

    def on_select_project(self, widget=None, row=None, col=None):
        project_list = self.get_selected_project_names()
        for task_list in []: # TODO: task_list objects
            # TODO: Need to add set_filter_* to tasklist views
            task_list.set_filter_projects(project_list)

        self.update_window_title()


    # TODO: For multiple tasklist views, connect signal to cursor changed,
    #       which unselects tasks in the other tasklist views.  It should
    #       also update any toolbar buttons that might not be valid
    #       (i.e. Done), and update statusbar stats.
    # self.done_menu_item.set_sensitive(enable), etc.

    # TODO: Verify when a task is deleted or marked done, the window title
    #       updates.  If not, add on_task_deleted, etc.

    def get_selected_project_names(self):
        if self.left_pane is None:
            return []
        selection = self.left_pane.get_selection()
        if selection is None:
            return []

        project_model, project_iter = selection.get_selected()
        if project_iter is None:
            return []
        project_list = []
        # TODO: iterate through project_iter, extracting project names
        return project_list

    def add_page_to_left_side_notebook(self, icon, page):
        """Adds a new page tab to the left panel.  The tab will
        be added as the last tab.  Also causes the tabs to be
        shown if they're not.
        @param icon: a gtk.Image picture to display on the tab
        @param page: gtk.Frame-based panel to be added
        """
        return self._add_page(self.left_side_notebook, icon, page)

    def add_page_to_main_notebook(self, title, page):
        """Adds a new page tab to the top right main panel.  The tab
        will be added as the last tab.  Also causes the tabs to be
        shown.
        @param title: Short text to use for the tab label
        @param page: gtk.Frame-based panel to be added
        """
        return self._add_page(self.main_notebook, gtk.Label(title), page)

    def add_page_to_detail_notebook(self, title, page):
        """Adds a new page tab to the lower right detail panel.  The
        tab will be added as the last tab.  Also causes the tabs to be
        shown.
        @param title: Short text to use for the tab label
        @param page: gtk.Frame-based panel to be added
        """
        # TODO: Only set this once we have something to show
        #self.detail_pane.set_size_request(-1, 300)

        return self._add_page(self.accessory_notebook, gtk.Label(title), page)

    def remove_page_from_left_side_notebook(self, page):
        """Removes a new page tab from the left panel.  If this leaves
        only one tab in the notebook, the tab selector will be hidden.
        @param page: gtk.Frame-based panel to be removed
        """
        return self._remove_page(self.left_side_notebook, page)

    def remove_page_from_main_notebook(self, page):
        """Removes a new page tab from the top right main panel.  If
        this leaves only one tab in the notebook, the tab selector will
        be hidden.
        @param page: gtk.Frame-based panel to be removed
        """
        return self._remove_page(self.main_notebook, page)

    def remove_page_from_detail_notebook(self, page):
        """Removes a new page tab from the lower right detail panel.
        If this leaves only one tab in the notebook, the tab selector
        will be hidden.
        @param page: gtk.Frame-based panel to be removed
        """
        return self._remove_page(self.detail_notebook, page)

    def hide(self):
        """Hide the browser window"""
        self.window.hide()

    def show(self):
        """Unhide the browser window"""
        self.window.present()
        self.window.show()

    def iconify(self):
        """Minimize the browser"""
        self.window.iconify()

    def is_visible(self):
        """Returns true if the window is currently visible"""
        return self.window.get_property("visible")

    def is_active(self):
        """Returns true if the window is the currently active window"""
        return self.window.get_property("is-active")


if __name__ == "__main__":
    browser = TasksBrowser()
    gtk.main()

