#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

import os.path
import re
from TableData import TableData
import csv
from pyutilib.component.core import alias


class CSVTable(TableData):

    alias("csv", "Manage IO with tables in CSV files.")

    def __init__(self):
        TableData.__init__(self)

    def open(self):
        if self.filename is None:
            raise IOError, "No filename specified"
        if not os.path.exists(self.filename):
            raise IOError, "Cannot find file '%s'" % self.filename
        self.INPUT = open(self.filename, 'r')

    def close(self):
        self.INPUT.close()

    def read(self):
        tmp=[]
        for tokens in csv.reader(self.INPUT):
            if tokens != ['']:
                tmp.append(tokens)
        if len(tmp) == 0:
            raise IOError, "Empty *.csv file"
        elif len(tmp) == 1:
            if not self.options.param is None:
                self._info = ["param",self.options.param,":=",tmp[0][0]]
            elif len(self.options.symbol_map) == 1:
                self._info = ["param",self.options.symbol_map[self.options.symbol_map.keys()[0]],":=",tmp[0][0]]
            else:
                raise IOError, "Data looks like a parameter, but multiple parameter names have been specified: %s" % str(self.options.symbol_map)
        else:
            self._set_data(tmp[0], tmp[1:])
        return True
