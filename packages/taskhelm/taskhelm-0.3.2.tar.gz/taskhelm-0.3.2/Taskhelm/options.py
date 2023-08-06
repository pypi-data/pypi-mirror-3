#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''Command line options'''

import info
from optparse import (
    make_option,
    OptionParser,
    )

OPTIONS = [
    (make_option('-d', '--debug',
                 help='Enable debug output',
                 action='store_true', default=False, dest='debug'),
     "Turns on verbose debugging output."),

    (make_option('-q', '--quick-entry',
                 help='Display concise entry dialog',
                 action='store_true', default=False, dest='quick_entry'),
                 """Instead of launching the full application, display a
                 quick entry dialog for adding a single task."""),
    ]

# TODO: Probably should sub-class OptionParser...  (then re-run pylint on this)

def make_parser():
    '''Creates an OptionParser instance for the options in this module'''

    option_list = []
    for item in OPTIONS:
        option_list.append(item[0])
    return OptionParser(
        option_list=option_list,
        version="%prog "+info.VERSION,
        epilog=info.DESCRIPTION)

def descriptions(parser=None):
    '''Returns a list of dict objects mapping option name to description'''
    if parser is None:
        parser = make_parser()

    data = []
    for opt in OPTIONS:
        opts = opt[0]._short_opts
        opts.extend(opt[0]._long_opts)
        item = {
            'opts': opts,
            'text': opt[1],
            }
        data.append(item)
    return data

def parse_commandline(parser=None):
    '''Creates a parser and parses the command line'''
    if parser is None:
        parser = make_parser()
    (opts, values) = parser.parse_args()
    return opts


if __name__ == "__main__":
    parser = make_parser()

    for d in descriptions(parser):
        print ','.join(d['opts'])
        print "  ", d['text']
        print

