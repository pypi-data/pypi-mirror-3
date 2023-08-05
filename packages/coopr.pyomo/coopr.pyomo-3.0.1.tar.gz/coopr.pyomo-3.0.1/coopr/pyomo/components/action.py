#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

__all__ = ['BuildAction']

import logging

from coopr.pyomo.base.numvalue import *
from coopr.pyomo.base.indexed_component import IndexedComponent
import types
from pyutilib.component.core import alias

logger = logging.getLogger('coopr.pyomo')


class BuildAction(IndexedComponent):
    """A build action, which executes a rule for all valid indices"""

    """ Constructor
        Arguments:
           name         The name of this action
           index        The index set that defines the distinct parameters.
                          By default, this is None, indicating that there
                          is a single action.
           rule         The rule that is executed for every indice.
    """

    alias("BuildAction", "This component is used to inject arbitrary actions into the model construction process.  The action rule is applied to every index value.")

    def __init__(self, *args, **kwd):
        tkwd = {'ctype':BuildAction}
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
                raise ValueError, "BuildAction constructor: unknown keyword - "+key
        if not type(self._rule) is types.FunctionType:
            raise ValueError, "BuildAction must have an 'rule' option specified whose value is a function"

    def pprint(self, ostream=None, verbose=False):
        if ostream is None:
            ostream = sys.stdout
        print >>ostream, "  ",self.name,":",

    def construct(self, data=None):
        """ Apply the rule to construct values in this set """
        if __debug__:
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug("Constructing Action, name="+self.name)
        if self._constructed:
            return
        self._constructed=True
        #
        # Update the index set dimension
        #
        self._compute_dim()
        for val in self._index:
            if val.__class__ is tuple:
                self._rule(self.model(), *val)
            elif val is None:
                self._rule(self.model())
            else:
                self._rule(self.model(), val)
