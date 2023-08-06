#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# TaskHelm - A frontend for the TaskWarrior task tracker
# Copyright (c) 2011 - Bryce W. Harrington

'''Package setup script'''

import glob

from distutils.core  import setup

from Taskhelm        import info

setup(
    name             = info.PROGNAME,
    version          = info.VERSION,
    url              = info.URL,
    author           = info.LEAD_DEVELOPER.name,
    author_email     = info.LEAD_DEVELOPER.email,
    description      = info.DESCRIPTION,
    long_description = open('README').read(),
    license          = 'LICENSE',
    platforms        = ['any'],
    requires         = ['gobject', 'json', 'pygtk'],
    packages         = [
        'Taskhelm',
        'Taskhelm.browser',
        'Taskhelm.dialogs',
        'Taskhelm.editor',
        'Taskhelm.utils',
        'Taskhelm.widgets',
        ],
    data_files = [
        ('share/taskhelm/icons',
         glob.glob('data/icons/*.*')),
        ('share/taskhelm/initial_tasks',
         glob.glob('data/initial_tasks/*.*')),
        ('share/taskhelm/initial_tasks/notes',
         glob.glob('data/initial_tasks/notes/*.*')),
         ],
    scripts = [
        'bin/taskhelm',
        'bin/tasknote'
        ],
    )
