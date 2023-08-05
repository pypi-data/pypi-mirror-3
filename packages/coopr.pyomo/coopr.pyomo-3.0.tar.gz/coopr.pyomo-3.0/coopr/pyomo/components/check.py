#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

__all__ = ['BuildCheck']

import logging

from pyutilib.component.core import alias
from coopr.pyomo.base.numvalue import *
from coopr.pyomo.base.indexed_component import IndexedComponent
import types

logger = logging.getLogger('coopr.pyomo')


class BuildCheck(IndexedComponent):
    """A build check, which executes a rule for all valid indices"""

    """ Constructor
        Arguments:
           name         The name of this check
           index        The index set that defines the distinct parameters.
                          By default, this is None, indicating that there
                          is a single check.
           rule         The rule that is executed for every indice.
    """

    alias("BuildCheck", "This component is used to perform a test during the model construction process.  The action rule is applied to every index value, and if the function returns False an exception is raised.")

    def __init__(self, *args, **kwd):
        tkwd = {'ctype':BuildCheck}
        IndexedComponent.__init__(self, *args, **tkwd)
        tmpname="unknown"
        self.domain=None
        self._rule=None
        for key in kwd.keys():
            if key == "name":
                tmpname=kwd[key]
            elif key == "rule":
                self.__dict__["_"+key] = kwd[key]
            else:
                raise ValueError, "BuildCheck constructor: unknown keyword - "+key
        if not type(self._rule) is types.FunctionType:
            raise ValueError, "BuildCheck must have an 'rule' option specified whose value is a function"

    def pprint(self, ostream=None, verbose=False):
        if ostream is None:
            ostream = sys.stdout
        print >>ostream, "  ",self.name,":",

    def construct(self, data=None):
        """ Apply the rule to construct values in this set """
        if __debug__:
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug("Constructing Check, name="+self.name)
        if self._constructed:
            return
        self._constructed=True
        #
        # Update the index set dimension
        #
        self._compute_dim()
        for val in self._index:
            if val.__class__ is tuple:
                res = self._rule(self.model(), *val)
            elif val is None:
                res = self._rule(self.model())
            else:
                res = self._rule(self.model(), val)
            if not res:
                raise ValueError, "BuildCheck %r identified error with index %r" % (self.name, str(val))
