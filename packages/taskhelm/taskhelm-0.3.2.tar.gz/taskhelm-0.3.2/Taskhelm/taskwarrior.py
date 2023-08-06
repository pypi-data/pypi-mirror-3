#!/usr/bin/env python

import re
import sys
import json
from datetime import (datetime, timedelta)
from subprocess import (Popen, PIPE)
from time import sleep
from utils.dates import (week_start, total_seconds)
from utils.debug import (dbg, ERR)

def sanitize(text):
    text = text.replace('"', "'")
    text = text.replace('\\', '')
    text = text.replace('$', '$ ')
    #text = re.escape(text) # This ends up escaping spaces, commas, and other stuff we don't want
    return text.strip()

def utc_date_to_local_datetime(dt):
    utc_offset = datetime.utcnow() - datetime.now()
    return datetime.strptime(dt, "%Y%m%dT%H%M%SZ") - utc_offset

class TaskWarrior(object):
    '''Interfaces with taskwarrior to retrieve/filter tasks'''

    SUPPORTED_VERSIONS = [
        '1.9.4',
        '1.9.5',
        '2.0.0.beta1',
        '2.0.0.beta2',
        '2.0.0.beta3',
        '2.0.0.beta4',
        '2.0.0.beta5',
        '2.0.0.RC1',
        '2.0.0.RC2',
        '2.0.0',
        ]

    def __init__(self, tw_exec='task'):
        self.tw_exec = tw_exec
        self._last_exec = None
        self._major_version = None
        if not self.refresh():
            sys.stderr.write("Could not initialize TaskWarrior\n")
            sys.exit(1)

    ###############################
    ### Helpers
    ###############################
    def execute(self, s, workaround_confirmation_bug=False):
        opts = "rc.confirmation=off rc.bulk=1000"
        self._last_exec = '%s %s %s | grep -v "^Configuration"' % (
            self.tw_exec, opts, s)
        # TODO: Switch away from using shell, if possible
        dbg("  execute: %s" %(self._last_exec))
        process = Popen(self._last_exec, stdin=PIPE, stdout=PIPE, shell=True)
        while workaround_confirmation_bug and process.poll() is None:
            if self.major_version == 1:
                process.stdin.write('no\n' * 10)
            elif self.major_version == 2:
                process.stdin.write('-- ' + 'no\n' * 10)
            sleep(0.01)
        return process.stdout.read()

    @staticmethod
    def VERSION(tw_exec='task'):
        # Workaround taskwarrior bug #902
        cmd = "%s rc:/dev/null version | grep 'task '" % (tw_exec)
        dbg("VERSION: %s" %(cmd))
        info = Popen(cmd, stdout=PIPE, shell=True).stdout.read()
        return info.split(None, 3)[1]

    @property
    def major_version(self):
        if self._major_version is None:
            self._major_version = int(self.VERSION()[:1])
            dbg("  Version %d.x detected" %(
                self._major_version))
        return self._major_version

    def touch(self):
        '''Invokes task warrior one time without changing any data.'''
        # Need to send a 'y' in case this is the first time taskwarrior has been
        # called and it needs to create a .taskrc
        # Workaround taskwarrior bug #903
        if self.major_version == 1:
            tw_input = 'y'
        else:
            # Task version 2.0 and greater
            tw_input = '-- y'
        cmd = "echo '%s' | task version" %(tw_input)
        dbg(cmd)
        proc = Popen(cmd, stdout=PIPE, stdin=PIPE, shell=True)
        stdout, stderr = proc.communicate(input=tw_input)
        if proc.returncode != 0:
            ERR("Failed to invoke `task` (%d):" %(proc.returncode))
            dbg(stdout)
            return False
        return True

    def reinitialize(self):
        dbg("Re-initializing taskwarrior")
        self._is_taskwarrior_virgin = None
        self._tasks_json = None
        self._tasks_dict = None
        self._tasks = None
        self.__projects = None
        self.__find_rate = None
        self.__fix_rate = None
        self.__pending_tasks = None
        self.__pending_projects = None
        self.__schedule = None
        self.__num_new_this_week = None
        self.__num_done_last_week = None
        self.__num_done_this_week = None
        self.__num_pending = None
        self.__num_waiting = None

    def refresh(self):
        # export doesn't do a refresh on its own
        if not self.touch():
            return False

        dbg("taskwarrior.refresh:  reinitialize()")
        self.reinitialize()
        dbg("taskwarrior.refresh:  export.json")
        text = self.execute('export.json')
        if text[:8] == 'No match':
            self._is_taskwarrior_virgin = True
            text = ''
        else:
            self._is_taskwarrior_virgin = False
        self._tasks_json = "[ %s ]" % (text)
        return True

    def uuid_to_id_map(self):
        # We don't want to cache this mapping since it's volatile In tw2
        # this should go away in preference to direct access of tasks by
        # uuid
        s = self.execute("rc.report.all.columns:uuid,id "
                         "rc.report.all.labels:UUID,id "
                         "rc.report.all.sort:id- "
                         "all")

        ids = {}
        regex = re.compile("^(\w+-\w{4}-\w{4}-\w{4}-\w+) +([\d-]+)$")
        for line in s.split('\n'):
            m = regex.match(line.strip())
            if m:
                uuid = m.group(1)
                tid = m.group(2)
                if uuid in ids.keys() and tid == '-':
                    continue
                ids[uuid] = tid

        return ids

    def uuids_to_ids(self, uuids):
        dbg("Getting uuid_to_id_map()")
        m = self.uuid_to_id_map()
        if type(uuids) == list:
            ids = []
            for uuid in uuids:
                if uuid in m:
                    if m[uuid] == '-':
                        dbg("Warning:  %s has id '-'" %(uuid))
                    ids.append(m[uuid])
            return ids
        elif type(uuids) in (str, unicode):
            dbg("%s found %s" %(uuids, m.get(uuids)))
            return [ m.get(uuids, '-') ]
        else:
            return None

    def join_ids(self, uuids):
        assert(uuids is not None)
        if self.major_version < 2:
            ids = self.uuids_to_ids(uuids)
            assert('-' not in ids)
            return ','.join(ids)
        elif type(uuids) == list:
            # TODO: tw 2.0 doesn't permit comma-separated uuids (bug: #901)
            #return ','.join(uuids)
            if len(uuids) == 1:
                return uuids[0]
            ids = self.uuids_to_ids(uuids)
            assert('-' not in ids)
            return ','.join(ids)
        else:
            return uuids

    ###############################
    ### Debugging
    ###############################
    def diagnostics(self):
        return self.execute('diagnostics')

    def config(self):
        return self.execute('show')

    @property
    def last_command(self):
        return self._last_exec

    @property
    def is_taskwarrior_virgin(self):
        return self._is_taskwarrior_virgin

    ###############################
    ### Task Data
    ###############################
    @property
    def tasks_json(self):
        if self._tasks_json is None:
            dbg("taskwarrior.tasks_json: Refreshing")
            self.refresh()
        return self._tasks_json

    # TODO: Rename to all_tasks
    @property
    def tasks_dict(self):
        if self._tasks_dict is None:
            try:
                self._tasks_dict = json.loads(self.tasks_json)
            except:
                ERR("invoking task for taskwarrior.tasks_dict\n%s")
                dbg(self.tasks_json)
                return {}
        return self._tasks_dict

    def _digest_tasks(self):
        projects_dict = {}
        self._tasks = {}
        self.__pending_tasks = []
        self.__pending_projects = {}
        self.__schedule = {}
        self.__num_new_this_week = 0
        self.__num_done_last_week = 0
        self.__num_done_this_week = 0
        self.__num_pending = 0
        self.__num_waiting = 0

        t = datetime.today()
        today = long(t.strftime("%Y%m%d"))

        for task_dict in self.tasks_dict:
            # Tasks
            self._tasks[task_dict[u'uuid']] = task_dict

            # Pending Tasks
            if task_dict[u'status'] == u'pending':
                self.__pending_tasks.append(task_dict)

            # Projects
            if u'project' in task_dict.keys():
                p = task_dict[u'project']
            else:
                p = u'-'
            projects_dict[p] = 1

            # Waiting Tasks
            if u'wait' in task_dict.keys():
                d = task_dict[u'wait']
                # TODO: Exclude tasks with wait date before today
                wait_date = d[:8]
                if long(wait_date) < today:
                    continue
                if wait_date not in self.__schedule.keys():
                    self.__schedule[wait_date] = []
                self.__schedule[wait_date].append(task_dict)

            # Statistics
            if task_dict[u'status'] == u'completed':
                end_date_utc = task_dict[u'end']
                end_datetime = utc_date_to_local_datetime(end_date_utc)
                timediff = week_start(t) - end_datetime
                if total_seconds(timediff) < 0:
                    self.__num_done_this_week += 1
                elif timediff.days < 7:
                    self.__num_done_last_week += 1
            elif task_dict[u'status'] == u'pending':
                self.__num_pending += 1
                if p in self.__pending_projects.keys():
                    self.__pending_projects[p] += 1
                else:
                    self.__pending_projects[p] = 1
            elif task_dict[u'status'] == u'waiting':
                self.__num_waiting += 1
            if task_dict[u'status'] not in [u'deleted']:
                entry_date = task_dict[u'entry']
                entry_datetime = utc_date_to_local_datetime(entry_date)
                timediff = week_start(t) - entry_datetime
                if total_seconds(timediff) < 0:
                    self.__num_new_this_week += 1

        self.__projects = projects_dict.keys()
        self.__projects.sort()

    def _filter_uuids_due_before(self, uuids, wait_date):
        filtered_uuids = []
        for uuid in uuids:
            t = self.get(uuid)
            due_date_utc = t.get(u'due', None)

            if due_date_utc is None:
                filtered_uuids.append(uuid)
            else:
                due_datetime = utc_date_to_local_datetime(due_date_utc)
                if wait_date < due_datetime:
                    filtered_uuids.append(uuid)

        return filtered_uuids

    @property
    def pending_tasks(self):
        if self.__pending_tasks is None:
            self._digest_tasks()
        return self.__pending_tasks

    @property
    def pending_projects(self):
        if self.__pending_projects is None:
            self._digest_tasks()
        return self.__pending_projects

    @property
    def waiting_tasks_schedule(self):
        '''Returns a dict of open tasks waiting for each coming day'''
        if self.__schedule is None:
            self._digest_tasks()
        return self.__schedule

    def get(self, uuid):
        if self._tasks is None:
            dbg("Digesting tasks")
            self._digest_tasks()
        return self._tasks.get(uuid, None)

    ###############################
    ### Adding/Deleting Tasks
    ###############################
    def add(self, desc, project=None, status='New', wait=None, due=None):
        # Scan desc for quote characters
        desc = sanitize(desc)

        if status == 'Done':
            cmd = 'log "%s"' % (sanitize(desc))
        else:
            cmd = 'add "%s"' % (sanitize(desc))
        if project:
            cmd += ' pro:%s' % (sanitize(project))
        if wait:
            cmd += ' wait:%s' %(sanitize(wait))
        if due:
            cmd += ' due:%s' %(sanitize(wait))
        self._is_taskwarrior_virgin = False
        return self.execute(cmd)

    def delete(self, uuids):
        if self.major_version == 1:
            return self.execute('%s delete' %(self.join_ids(uuids)), workaround_confirmation_bug=True)
        else:
            return self.execute('%s delete' %(self.join_ids(uuids)))

    ###############################
    ### Undo
    ###############################
    def undo(self):
        return self.execute('undo')

    ###############################
    ### Description
    ###############################
    def set_description(self, tid, desc):
        if self.major_version == 1:
            cmd = '%s "%s"' % (tid, sanitize(desc))
        else:
            cmd = '%s modify "%s"' % (tid, sanitize(desc))
        retval = self.execute(cmd)
        dbg("%s %s" % (cmd, retval))
        return retval

    def append(self, uuids, text):
        return self.execute('%s append "%s"' %(self.join_ids(uuids), sanitize(text)))

    def prepend(self, uuids, text):
        return self.execute('%s prepend "%s"' %(self.join_ids(uuids), sanitize(text)))

    ###############################
    ### Status
    ###############################
    def start(self, uuids):
        return self.execute('%s start' %(self.join_ids(uuids)))

    def stop(self, uuids):
        return self.execute('%s stop' %(self.join_ids(uuids)))

    def end(self, uuids):
        return self.execute('%s end' %(self.join_ids(uuids)))

    def done(self, uuids):
        return self.execute('%s done' %(self.join_ids(uuids)))

    ###############################
    ### Projects
    ###############################
    @property
    def projects(self):
        '''Returns the current registered projects'''
        if self.__projects is None:
            self._digest_tasks()
        return self.__projects

    def set_project(self, uuids, project):
        '''Sets the project for the tasks matching uuids'''
        if self.major_version < 2:
            return self.execute('%s pro:%s' % (self.join_ids(uuids), sanitize(project)))
        else:
            return self.execute('%s modify pro:%s' % (self.join_ids(uuids), sanitize(project)))

    ###############################
    ### Priorities
    ###############################
    @property
    def priorities(self):
        '''Returns the valid set of task priorities'''
        return ['H', 'M', 'L', '-']

    def set_priority(self, uuids, priority='H'):
        '''Sets the priority for the tasks matching uuids'''
        assert priority in self.priorities
        if priority == '-':
            priority = 'N'
        if self.major_version == 1:
            return self.execute('%s pri:%s' % (self.join_ids(uuids), sanitize(priority)))
        else:
            return self.execute('%s modify pri:%s' % (self.join_ids(uuids), sanitize(priority)))

    ###############################
    ### Dates
    ###############################
    def set_due(self, uuids, due_date):
        '''Sets the due date for the tasks matching uuids'''
        if self.major_version == 1:
            return self.execute('%s due:%s' % (self.join_ids(uuids), sanitize(due_date)))
        else:
            return self.execute('%s modify due:%s' % (self.join_ids(uuids), sanitize(due_date)))

    def set_wait(self, uuids, wait_time_qty, wait_time_period):
        '''Postpones task until the given wait date'''
        assert(uuids is not None)

        # TODO: Move this into utils/dates
        if wait_time_period[:1].lower() == 'd':
            due_delta = timedelta(days = int(wait_time_qty))
        if wait_time_period[:1].lower() == 'm':
            due_delta = timedelta(days = int(wait_time_qty)*30)
        if wait_time_period[:1].lower() == 'y':
            due_delta = timedelta(days = int(wait_time_qty)*365)
        else:
            due_delta = timedelta(days = 0)

        filtered_uuids = self._filter_uuids_due_before(uuids, datetime.utcnow() + due_delta)
        if len(filtered_uuids) > 0:
            wait_time = "%s%s" %(wait_time_qty, str(wait_time_period))
            if self.major_version == 1:
                return self.execute('%s wait:%s' % (self.join_ids(filtered_uuids), sanitize(wait_time)))
            else:
                return self.execute('%s modify wait:%s' % (self.join_ids(filtered_uuids), sanitize(wait_time)),
                                    workaround_confirmation_bug=True)

    ###############################
    ### Tags
    ###############################
    @property
    def tags(self):
        '''Shows a list of all tags used'''
        return self.execute('tags')

    def add_tag(self, uuids, tag_name):
        '''Adds the given tag name to the specified task uuids'''
        if self.major_version == 1:
            return self.execute('%s +%s' % (self.join_ids(uuids), sanitize(tag_name)))
        else:
            return self.execute('%s modify +%s' % (self.join_ids(uuids), sanitize(tag_name)))

    def remove_tag(self, uuids, tag_name):
        '''Removes the given tag name from the specified task uuids'''
        if self.major_version == 1:
            return self.execute('%s -%s' % (self.join_ids(uuids), sanitize(tag_name)))
        else:
            return self.execute('%s modify -%s' % (self.join_ids(uuids), sanitize(tag_name)))

    ###############################
    ### Annotations
    ###############################
    def annotate(self, uuids, annotation):
        '''Adds annotation to the given tasks'''
        return self.execute('%s annotate "%s"' %(self.join_ids(uuids), sanitize(annotation)))

    def denotate(self, uuids, annotation):
        '''Removes annotation from the given tasks'''
        return self.execute('%s denotate "%s"' %(self.join_ids(uuids), sanitize(annotation)))


    ###############################
    ### Statistics
    ###############################
    def _get_find_and_fix_rates(self):
        re_rate = re.compile("(Find|Fix) rate:\s*([\d\.]+).d")
        burndown = self.execute('burndown')
        find_rate = 0
        fix_rate = 0
        for line in burndown.split("\n"):
            m = re_rate.search(line)
            if m:
                if m.group(1) == 'Find':
                    find_rate = m.group(2)
                elif m.group(1) == 'Fix':
                    fix_rate = m.group(2)
        return (find_rate, fix_rate)

    @property
    def num_done_last_week(self):
        if self.__num_done_last_week is None:
            self._digest_tasks()
        return self.__num_done_last_week

    @property
    def num_done_last_last_week(self):
        if self.__num_done_last_last_week is None:
            self._digest_tasks()
        return self.__num_done_last_last_week

    @property
    def num_done_last_last_last_week(self):
        if self.__num_done_last_last_last_week is None:
            self._digest_tasks()
        return self.__num_done_last_last_last_week

    @property
    def num_done_this_week(self):
        if self.__num_done_this_week is None:
            self._digest_tasks()
        return self.__num_done_this_week

    @property
    def num_new_this_week(self):
        if self.__num_new_this_week is None:
            self._digest_tasks()
        return self.__num_new_this_week

    @property
    def num_pending(self):
        if self.__num_pending is None:
            self._digest_tasks()
        return self.__num_pending

    @property
    def num_waiting(self):
        if self.__num_waiting is None:
            self._digest_tasks()
        return self.__num_waiting

    def num_waiting_in_period(self, start_date, period_length):
        count = 0
        for offset in range(0, period_length):
            t = start_date + timedelta(days=offset)
            day = t.strftime("%Y%m%d")
            count += len(self.waiting_tasks_schedule.get(day, []))
        return count

    @property
    def find_rate_per_day(self):
        if self.__find_rate is None:
            self.__find_rate, self.__fix_rate = self._get_find_and_fix_rates()
        return float(self.__find_rate)

    @property
    def fix_rate_per_day(self):
        if self.__fix_rate is None:
            self.__find_rate, self.__fix_rate = self._get_find_and_fix_rates()
        return float(self.__fix_rate)

    def get_statistic(self, name):
        if name == 'Total':
            return self.num_pending + self.num_waiting
        if name == 'Waiting':
            return self.num_waiting
        if name == 'Pending':
            return self.num_pending
        if name == 'New this week':
            return self.num_new_this_week
        if name == 'Done this week':
            return self.num_done_this_week
        if name == 'Done last week':
            return self.num_done_last_week


if __name__ == "__main__":
    tw = TaskWarrior()
    uuids = tw.uuid_to_id_map()
    print "New tasks this week:"
    for task_dict in tw.tasks_dict:
        uuid = task_dict.get(u'uuid', None)
        tid = uuids.get(uuid, '-')
#        if task_dict[u'status'] == u'pending':
#            print "%s %-20s %-2s %s" % (
#                tid,
#                task_dict.get(u'project', ''),
#                task_dict.get(u'priority', ''),
#                task_dict.get(u'description', '')
#                )

        if task_dict[u'status'] not in [u'deleted', u'recurring']:
            t = datetime.today()
            utc_offset = datetime.utcnow() - datetime.now()
            entry_date = task_dict[u'entry']
            entry_datetime = utc_date_to_local_datetime(entry_date)
            timediff = week_start(t) - entry_datetime
            if total_seconds(timediff) < 0:
                print "%5s %-25s %-2s %s" % (
                    tid,
                    task_dict.get(u'project', ''),
                    task_dict.get(u'priority', ''),
                    task_dict.get(u'description', '')
                    )

    if not tw.is_taskwarrior_virgin:
        print
        print "New this week:    %d" % (tw.num_new_this_week)
        print "Open today:       %d" % (tw.num_pending)
        print "Open total:       %d" % (tw.num_pending + tw.num_waiting)
        print "Done this week:   %d" % (tw.num_done_this_week)
        print "Done last week:   %d" % (tw.num_done_last_week)
        print "Find Rate:        %3.1f" % (tw.find_rate_per_day)
        print "Fix Rate:         %3.1f" % (tw.fix_rate_per_day)

        print
        print "Number of tasks for coming 2 weeks"
        schedule = tw.waiting_tasks_schedule
        days = schedule.keys()
        days.sort()
        for day in days[:14]:
            tasks = schedule[day]
            print day, len(tasks)

    print "Waiting this month: %d" % (tw.num_waiting_in_period(datetime.today(), 2))
