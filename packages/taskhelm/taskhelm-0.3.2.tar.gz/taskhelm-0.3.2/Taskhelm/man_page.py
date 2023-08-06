#!/usr/bin/env python

'''Generate a man page using an info module'''

import info
import options

data = {}
for key in dir(info):
    if key[0] == '_':
        continue
    value = getattr(info, key)
    if type(value) is str:
        data[key] = getattr(info, key)
    elif hasattr(value, 'to_dict'):
        value_dict = value.to_dict()
        for membername in value_dict.keys():
            membervalue = value_dict[membername]
            data[key+'_'+membername.upper()] = membervalue


manpage = """.TH %(PROGNAME)s 1 %(DATE_STARTED)s "%(PROGNAME)s"
.SH NAME
%(PROGNAME)s \\-  %(SHORT_DESCRIPTION)s
.SH SYNOPSIS
.B %(PROGNAME)s [options]
.SH DESCRIPTION
%(DESCRIPTION)s
""" %(d)

manpage += ".SH OPTIONS"

for item in options.descriptions():
    opts_markup = '\\fB,\\fB'.join(item['opts'])
    manpage += """
.TP
\\fB%s\\fB
%s""" %(opts_markup, item['text'])

manpage += """
.SH COPYRIGHT
This manual page is Copyright %(DATE_COPYRIGHT)s %(LEAD_DEVELOPER_NAME)s <%(LEAD_DEVELOPER_EMAIL)s>.
Permission is granted to copy, distribute and/or modify this document
under the terms of the GNU General Public License, Version 3 or any later
version published by the Free Software Foundation.""" %(d)

print manpage
