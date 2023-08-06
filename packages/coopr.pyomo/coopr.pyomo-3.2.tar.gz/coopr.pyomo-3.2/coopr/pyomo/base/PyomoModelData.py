#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

__all__ = ['ModelData']

import logging
from plugin import *

logger = logging.getLogger('coopr.pyomo')


class ModelData(object):
    """
    An object that manages data for a model.

    This object contains the interface routines for importing and
    exporting data from external data sources.
    """

    def __init__(self, **kwds):
        """
        Constructor
        """
        #
        # This is the data that is imported from various data sources
        #
        self._default={}
        # _data[scenario][symbol] -> data
        self._data={}
        #
        self._info=[]
        self._model = kwds.pop('model', None)

        if 'filename' in kwds:
            if not kwds['filename'] is None:
                filename = kwds['filename']
                del kwds['filename']
                self.add(filename, **kwds)
                self.read()
        elif len(kwds) > 0:
            raise ValueError, "Unknown options: %s" % str(kwds.keys())

    def initialize(self, component, data, namespace=None):
        self._data[namespace][component] = data

    def add(self, filename, **kwds):
        tmp = filename.split(".")[-1]
        data = DataManagerFactory(tmp)
        data.initialize(filename, **kwds)
        self._info.append(data)

    def read(self, model=None):
        """
        Read data
        """
        if model is not None:
            self._model=model
        if self._model is None:
            raise ValueError, "Cannot read model data without a model"
        #
        # Although we want to load data in a particular order, it
        # may make sense to open/close all data resources all at once.
        # Should we do this by default, or make this a configuration option
        # for this class?
        #
        for data in self._info:
            if __debug__:
                logger.debug("Importing data...")
            data.open()
            if not data.read():
                print "Warning: error occured while processing %s" % str(data)
            data.close()
            if __debug__:
                logger.debug("Processing data ...")
            #
            # Update the _data and _default dictionaries with data that
            # was read in.
            #
            status = data.process(self._model, self._data, self._default)
            data.clear()
            if __debug__:
                logger.debug("Done.")
