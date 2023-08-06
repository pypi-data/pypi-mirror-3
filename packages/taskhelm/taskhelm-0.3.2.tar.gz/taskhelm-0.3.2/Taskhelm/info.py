#!/usr/bin/env python
# -*- coding: utf-8 -*-

from info_utils import (
    _contributor,
    _get_version_from_debian_changelog
    )

'''High level package information'''
PROGNAME = 'taskhelm'
URL = 'http://taskwarrior.org'
EMAIL = 'support@taskwarrior.org'
VERSION = '0.3.2'
DATE_STARTED = '2011-07-22'
DATE_COPYRIGHT = '2011'
LICENSE_URL = 'http://www.gnu.org/copyleft/gpl.html'

SHORT_DESCRIPTION = "A task management tool built on the powerful TaskWarrior"

DESCRIPTION = """
taskhelm is a graphic shell that sits on Task Warrior.
"""

LEAD_DEVELOPER = _contributor(
    'Bryce Harrington', 'bryce@bryceharrington.org', started='2011-07-22',
    roles=['lead', 'developer'], translating=None,
    )

CONTRIBUTORS = [
    # Copyright 2011, Alan Bowen, bowen@tcnj.edu.
    _contributor('Alan Bowen', 'bowen@tcnj.edu', roles='tasknote'),

    # Copyright 2010, Johannes Schlatow.
    _contributor('Johannes Schlatow', '', roles=['taskopen']),
    ]


if __name__ == "__main__":
    print PROGNAME, VERSION, URL
    print "Copyright (C) %s %s <%s>" % (
        DATE_COPYRIGHT, LEAD_DEVELOPER.name, LEAD_DEVELOPER.email)
    print
    for contributor in CONTRIBUTORS:
        print "%s %s %s" % (
            contributor.name,
            contributor.display_email,
            contributor.display_roles)
