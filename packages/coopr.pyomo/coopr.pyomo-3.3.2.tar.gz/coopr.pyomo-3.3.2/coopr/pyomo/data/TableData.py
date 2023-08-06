#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

__all__ = ['TableData']

from coopr.pyomo.base.plugin import IDataManager
from process_data import _process_data
from pyutilib.component.core import Plugin, implements
from pyutilib.misc import Options


class TableData(Plugin):
    """
    An object that imports data from a table in an external data source.
    """

    implements(IDataManager)

    def __init__(self):
        """
        Constructor
        """
        self._info=None
        self._data=None

    def initialize(self, filename, **kwds):
        self.filename = filename
        self.options = Options(**kwds)

    def open(self):
        """
        Open the table
        """
        pass

    def read(self):
        """
        Read data from the table
        """
        pass

    def close(self):
        """
        Close the table
        """
        pass

    def process(self, model, data, default):
        """
        Return the data that was extracted from this table
        """
        if not None in data:
            data[None] = {}
        return _process_data(
          self._info,
          model,
          data[None],
          default,
          self.filename
        )

    def clear(self):
        """
        Clear the data that was extracted from this table
        """
        self._info = None

    def _set_data(self, headers, rows):
        #print "_SET_DATA",headers,rows # XXX
        if self.options.param_name is None:
            mapped_headers = map(str,list(headers))
        else:
            mapped_headers = list()
            for header in map(str, list(headers)):
                if header in self.options.param_name:
                    mapped_headers.append(self.options.param_name[header])
        #print "X", mapped_headers, self.options.param_name, \
        #           self.options.index, self.options.format

        if self.options.format == 'set':
            if self.options.set is None:
                msg = "Must specify set name for data with the 'set' format"
                raise IOError, msg

            if not (self.options.index is None or self.options.index == []):
                msg = "Cannot specify index for data with the 'set' format: %s"
                raise IOError, msg % str( self.options.index )

            self._info = ["set",self.options.set,":="]
            for row in rows:
                self._info.extend(row)

        elif self.options.format == 'set_array':
            if self.options.set is None:
                msg = "Must specify set name for data with the 'set_array' "  \
                      'format'
                raise IOError, msg

            if not (self.options.index is None or self.options.index == []):
                msg = "Cannot specify index for data with the 'set_array' "   \
                      'format: %s'
                raise IOError, msg % str( self.options.index )

            self._info = ["set",self.options.set, ":"]
            self._info = self._info + list(headers[1:])
            self._info = self._info + [":="]
            for row in rows:
                self._info = self._info + list(row)

        elif self.options.format == 'transposed_array':
            self._info = ["param",self.options.param,"(tr)",":"]              \
                       + headers[1:]
            self._info.append(":=")
            for row in rows:
                self._info.extend(row)

        elif self.options.format == 'array':
            self._info = ["param",self.options.param,":"] + headers[1:]
            self._info.append(":=")
            for row in rows:
                self._info.extend(row)

        elif self.options.format == 'param':
            self._info = ["param",":",self.options.param,':=']
            for row in rows:
                self._info.extend(row)

        elif self.options.format == 'table' or self.options.format is None:
            #print "TABLE FORMAT" # XXX
            #print "INDEX:", self.options.index # XXX
            #print "INDEX NAME:", self.options.index_name # XXX
            #print "MAPPED HEADERS:", mapped_headers # XXX
            if self.options.index is None or len(self.options.index) == 0:
                msg = "Cannot import a relational table without specifying "  \
                      "index values"
                raise IOError, msg

            if self.options.index_name is not None:
                self._info = ["param",":",self.options.index_name,":"]
            else:
                self._info = ["param",":"]
            for header in mapped_headers:
                if not header in self.options.index:
                    self._info.append(header)
            self._info.append(":=")
            for row in rows:
                self._info.extend(row)
        else:
            msg = "Unknown parameter format: '%s'"
            raise ValueError, msg % self.options.format
        #print "FINAL",self._info # XXX
