#!/usr/bin/env python

import os
import json

from dictable import (
    convert_to_dict,
    convert_from_dict,
    )
from debug import (dbg, ERR)

class JsonIO(object):
    def __init__(self, filename):
        self.filename = filename

    def read(self):
        if not os.path.exists(self.filename):
            return None
        json_file = open(self.filename, 'r')
        json_data = json.load(json_file, object_hook=convert_from_dict)
        json_file.close()
        return json_data

    def write(self, data):
        ftmp = self.filename+'.tmp'
        pathname = os.path.dirname(self.filename)
        if not os.path.exists(pathname):
            os.makedirs(pathname)

        try:
            if os.path.exists(ftmp):
                os.unlink(ftmp)
            file = open(ftmp, 'w')
            text = json.dumps(data, indent=4, default=convert_to_dict)
            file.write(text + "\n")
            file.close()
        except IOError:
            ERR("Failed to save %s to file %s" %(type(data), ftmp))
            raise
            return

        try:
            os.rename(ftmp, self.filename)
        except IOError:
            os.unlink(self.filename)
            os.rename(ftmp, self.filename)

if __name__ == "__main__":
    import debug
    debug.ENABLED = True

    dbg("Hello")
    ERR("World")

