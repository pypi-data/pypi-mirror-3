#!/usr/bin/env python

'''Class wrapper around a taskwarrior task'''

import os.path
import gobject

from taskwarrior import TaskWarrior
from utils.debug import (dbg, ERR)

class Task(object):
    '''Class wrapper around a taskwarrior task'''
    def __init__(self, uuid=None, taskwarrior=None, config=None):
        # TODO: config as a static global
        self.__uuid = uuid
        self.__description = None
        self.__annotations = None
        self.__priority = None
        self.__status = None
        self.__project = None
        self.__tags = None
        self.__due = None
        self.__start = None
        self.__end = None
        self.__entry = None
        self.__wait = None
        self.__recur = None
        self.__imask = None
        self.__parent = None

        self._taskwarrior = taskwarrior
        self._idle_jobs = []
        self._description_idle_jobs = []
        self._config = config

        if self._taskwarrior is None:
            self.refresh()
        else:
            self.reload()

    ##############################
    ### Helpers
    ##############################
    def reload(self):
        '''Update this with current info'''
        if self.uuid is not None:
            dbg("Task:  Loading %s from taskwarrior" %(self.uuid))
            data = self.taskwarrior.get(self.uuid)
            assert data, "Could not find UUID %s in taskwarrior" % (self.uuid)
            self.from_dict(data)

    def refresh(self):
        '''Reload all data from taskwarrior and update this with current info'''
        self.taskwarrior.refresh()
        self.reload()

    @property
    def taskwarrior(self):
        '''The cached TaskWarrior instance'''
        if self._taskwarrior is None:
            dbg("taskwarrior object regenerating...")
            self._taskwarrior = TaskWarrior()
        assert self._taskwarrior
        return self._taskwarrior

    ##############################
    ### Data I/O
    ##############################
    def to_dict(self):
        '''Convert to a pure dict usable with JSON'''
        data = {}
        for key, val in self.__dict__.items():
            if key[0:1] == '__':
                data[key] = val
        return data

    def from_dict(self, data):
        '''Update this task object using data in the dict'''
        if data is None:
            return None
        for key, val in data.items():
            key_cache = "_Task__%s" % (key)
            if key_cache in self.__dict__.keys():
                self.__dict__[key_cache] = val
            elif key in ['id']:
                # Ignore these keys
                pass
            else:
                ERR("unrecognized task property %s=%s" % (key, val))

    @property
    def uuid(self):
        return self.__uuid

    @property
    def tid(self):
        '''Invoke taskwarrior to get the current ID number for this task'''
        tids = self.taskwarrior.uuids_to_ids(self.uuid)
        if tids is None:
            return '-'
        elif type(tids) == list:
            return tids[0]
        else:
            return tids

    ##############################
    ### Adding/deleting
    ##############################
    def delete(self):
        return self.taskwarrior.delete(self.tid)

    ##############################
    ### Notes
    ##############################
    @property
    def notes_dirname(self):
        default_location = '%s/.task/notes' % (os.path.expanduser('~'))
        if self._config is not None:
            location = self._config.get('notes.location', default_location)
            location = os.path.expanduser(location)
            return location
        return default_location

    @property
    def notes_filename(self):
        # TODO: Detect if it is a recurring task, and if so use
        #  the parent uuid
        return '%s/%s.txt' % (self.notes_dirname, self.uuid)

    def has_notes(self):
        return os.path.isfile(self.notes_filename)

    def get_notes(self):
        '''Loads and returns the notes for the task'''
        notes = None
        if self.has_notes():
            try:
                infile = open(self.notes_filename, 'r')
                if infile:
                    notes = infile.read()
                    infile.close()
            except:
                # File probably doesn't exist anymore, but it's cool...
                dbg("Could not load notes file %s" % (self.notes_filename))
                notes = None

        # Always return a defined string, at least blank
        if notes is None:
            return ''
        else:
            return notes
    def set_notes(self, text):
        if self.notes.strip() == text.strip():
            # Notes weren't actually changed
            return False
        if not os.path.exists(self.notes_dirname):
            os.makedirs(self.notes_dirname)

        # Delete any pending saves
        for job in self._idle_jobs:
            gobject.source_remove(job)

        # Create job to save the notes when there's a spare moment
        job = gobject.idle_add(self._idle_set_notes, text)
        self._idle_jobs.append(job)

        # Check if task is already annotated
        if self.annotations is not None:
            for annotation in self.annotations:
                if annotation[u'description'] == u'Notes':
                    return True

        # If not, add an annotation indicating the task has notes
        retval = self.taskwarrior.annotate(self.tid, "Notes")
        dbg("%s %s" %(self.taskwarrior.last_command, retval))
        return retval
    notes = property(get_notes, set_notes)

    def _idle_set_notes(self, text):
        try:
            outfile = open(self.notes_filename, 'w')
            if not outfile:
                ERR("Could not open %s for writing" % (
                    self.notes_filename))
            else:
                outfile.write(text)
                outfile.close()
        except:
            ERR("Could not set notes to %s" % (
                self.notes_filename))
            raise
        self.refresh()
        return False

    ##############################
    ### Description
    ##############################
    def get_description(self):
        return  self.__description
    def set_description(self, text):
        if self.description.strip() == text.strip():
            # Task's description was not actually changed
            dbg("Description has not changed")
            return False

        # Delete any pending saves
        for job in self._description_idle_jobs:
            gobject.source_remove(job)

        # Create job to save the notes when there's a spare moment
        job = gobject.idle_add(self._idle_set_description, text)
        self._description_idle_jobs.append(job)
        return True
    description = property(get_description, set_description)

    def _idle_set_description(self, text):
        retval = self.taskwarrior.set_description(self.tid, text)
        if retval:
            self.refresh()
            return False
        return True

    def append(self, text):
        return self.taskwarrior.append(self.tid, text)

    def prepend(self, text):
        return self.taskwarrior.prepend(self.tid, text)

    ##############################
    ### Projects
    ##############################
    def get_project(self):
        return self.__project
    def set_project(self, project):
        return self.taskwarrior.set_project(self.tid, project)
    project = property(get_project, set_project)

    ##############################
    ### Priorities
    ##############################
    def get_priority(self):
        return self.__priority
    def set_priority(self, priority):
        return self.taskwarrior.set_priority(self.tid, priority)
    priority = property(get_priority, set_priority)

    ##############################
    ### Dates
    ##############################
    def get_due(self):
        return self.__due
    def set_due(self, due_date):
        if due_date is not None:
            self.taskwarrior.set_due(self.tid, due_date)
    due = property(get_due, set_due)

    def get_wait(self):
        return self.__wait
    def set_wait(self, wait_date):
        if wait_date is not None:
            return self.taskwarrior.set_wait(self.tid, wait_date)
    wait = property(get_wait, set_wait)

    @property
    def entry(self):
        '''Returns the date the task was created. [Not editable]'''
        return self.__entry

    ##############################
    ### Status
    ##############################
    @property
    def status(self):
        return self.__status

    def get_start(self):
        return self.__start
    def set_start(self, is_started=True):
        if not is_started:
            return self.set_stop()
        return self.taskwarrior.start(self.tid)
    start = property(get_start, set_start)

    @property
    def end(self):
        return self.__end

    def set_stop(self):
        return self.taskwarrior.stop(self.__uuid)

    def set_done(self):
        return self.taskwarrior.done(self.__uuid)

    ##############################
    ### Annotations
    ##############################
    def annotate(self, text):
        return self.taskwarrior.annotate(self.tid, text)

    def denotate(self, text):
        return self.taskwarrior.denotate(self.tid, text)

    @property
    def annotations(self):
        return self.__annotations


if __name__ == "__main__":
    import random
    taskwarrior = TaskWarrior()

    def display(fmt="%s", data=None):
        if data is None:
            return ''
        return fmt % (data)

    if len(taskwarrior.tasks_dict)>0:
        i = random.choice(range(0, len(taskwarrior.tasks_dict)))
        task_dict = taskwarrior.tasks_dict[i]
        task = Task()
        task.from_dict(task_dict)
        print ' '.join( [
            display("%s", task.tid),
            display("@%s", task.project),
            display("(%s)", task.priority) ] )
        print ' ', ' '.join( [
            display("%s", task.description),
            display("[%s]", task.status) ] )
        print ' ', ' '.join( [
            display("%s", task.due),
            display("%s", task.wait) ] )
