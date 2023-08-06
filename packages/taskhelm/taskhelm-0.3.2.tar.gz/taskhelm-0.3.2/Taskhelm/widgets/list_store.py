#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk

class DictListStore(gtk.ListStore):
    '''A gtk ListStore that permits adding data as dicts'''

    def __init__(self, columns):
        '''Construct a dictionary list store

        columns is a list of dicts containing 'name' and 'type' fields.
        '''
        gtk.ListStore.__init__(self, int)
        self.column_keys  = []
        self.column_types = []
        for col in columns:
            self.column_keys.append(col.name)
            self.column_types.append(col.type)

        self.COL_FONT = len(columns)
        self.column_keys.append("__Font")
        self.column_types.append(str)

        self.set_column_types(*self.column_types)

        # Create a TreeModelFilter and a TreeModelSort around that
        self.model_filter = self.filter_new()
        self.model_filtersort = gtk.TreeModelSort(self.model_filter)

    def set_data(self, list_of_dicts):
        '''Erase all current data items in the store and replace them'''
        self.clear()
        for d in list_of_dicts:
            self.append_data(d)
        self.model_filter.refilter()

    def append_data(self, new_data):
        '''Add one or more items of data to the end of the store'''
        if type(new_data) is dict:
            new_data = [ new_data ]
        for d in new_data:
            data = []
            font_effects = []
            project = d.get(u'project', '-')
            # Project: Background/Foreground
            # Started: Bold
            if d.get(u'start', False):
                font_effects.append('bold')
            # Recurring: Italic
            if d.get(u'recur', False):
                font_effects.append('italic')
            # Notes: Underline(?)
            #if d.get(u'annotations', False):
            #    for a in d[u'annotations']:
            #        if a.get(u'description', u'') == 'Notes':
            #            break
            font = ' '.join(font_effects)
            for key in self.column_keys:
                if key == '__Font':
                    value = font
                else:
                    value = d.get(key, '-')
                if type(value) == str or type(value) == unicode:
                    value = value.replace("\\", '')
                data.append(value)
            self.append(data)


if __name__ == '__main__':
    from list_column import Column

    columns = [
        Column('foo', str, 'Foo'),
        Column('bar', int, 'Bar'),
        Column('baz', str, 'Baz'),
        ]

    store = DictListStore(columns)

    d = {
        'foo': 'FOO',
        'bar': 42,
        'baz': 'BAR',
        }
    store.set_data([d])

    d['bar'] += 1
    store.append_data(d)

    for row in store:
        for value in row:
            print value,
        print
