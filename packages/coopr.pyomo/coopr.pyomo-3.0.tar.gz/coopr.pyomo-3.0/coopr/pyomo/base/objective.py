#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

__all__ = ['Objective', 'simple_objective_rule', 'ObjectiveData']

import sys
import logging
import weakref

from expr import *
from indexed_component import IndexedComponent
from misc import create_name, apply_indexed_rule
from numtypes import *
from numvalue import *
from pyutilib.component.core import alias
from sets import _BaseSet, _SetContainer
from var import Var, _VarValue, _VarArray, _VarElement
import pyutilib.math
import pyutilib.misc

from component import Component
from set_types import *
from sets import _SetContainer

from coopr.pyomo.base.expr import generate_expression, generate_relational_expression
from coopr.pyomo.base.intrinsic_functions import generate_intrinsic_function_expression
import time

logger = logging.getLogger('coopr.pyomo')


def simple_objective_rule( fn ):
    """This is a decorator that translates None into Constraint.Skip.
    This supports a simpler syntax in objective rules, though these can be
    more difficult to debug when errors occur.

    Example use:

    @simple_objective_rule
    def O_rule(model, i, j):
        ...
    """

    def wrapper_function ( *args, **kwargs ):
        value = fn( *args, **kwargs )
        if value is None:
            return Objective.Skip
        return value
    return wrapper_function

class ObjectiveData(NumericValue):

    __slots__ = ['component', 'obj', 'expr', 'id', 'active', 'repn', 'ampl_repn', 'index']

    def __init__(self, expr=None, name=None, obj=None):
        NumericValue.__init__(self,name,Reals,None,True)

        self.expr = expr
        self.index = None
        self.obj = weakref.ref(obj)
        self.component = weakref.ref(obj)

        self.id = -1

        self.active = True

        self.repn = None
        self.ampl_repn = None

    def __getstate__(self):
        result = NumericValue.__getstate__(self)
        for i in ObjectiveData.__slots__:
            result[i] = getattr(self, i)
        if type(result['obj']) is weakref.ref:
            result['obj'] = result['obj']()
        if type(result['component']) is weakref.ref:
            result['component'] = result['component']()
        return result

    def __setstate__(self, state):
        for (slot_name, value) in state.iteritems():
            setattr(self, slot_name, value)
        self.obj = weakref.ref(self.obj)
        self.component = weakref.ref(self.component)

    def __call__(self, exception=True):
        if self.expr is None:
            return None
        return self.expr()

    def polynomial_degree(self):
        if self.expr is None:
            return None
        return self.expr.polynomial_degree()

    def activate(self):
        self.active=True

    def deactivate(self):
        self.active=False


class Objective(IndexedComponent, NumericValue):
    """An object that defines a objective expression"""

    alias('Objective', 'Expressions that are minimized or maximized in a '    \
          'model.')

    Skip        = (1000,)
    NoObjective = (1000,)

    def __init__(self, *args, **kwargs):
        """Construct an objective expression with rule to construct the
           expression
        """
        tkwargs = {'ctype':Objective, 'doc': kwargs.pop('doc', None)}
        IndexedComponent.__init__(self, *args, **tkwargs)

        self._data = {}
        if args == ():
            self._data[None] = ObjectiveData(obj=self)

        tmpname  = kwargs.pop('name', 'unknown')
        tmpsense = kwargs.pop('sense', minimize )
        tmprule  = kwargs.pop('rule', None )
        tmprule  = kwargs.pop('expr', tmprule )
        self._no_rule_init = kwargs.pop('noruleinit', None )

        # _no_rule_init is a flag specified by the user to indicate that no
        # construction rule will be specified, and that constraints will be
        # explicitly added by the user. set via the "noruleinit" keyword. value
        # doesn't matter, as long as it isn't "None".

        if ( kwargs ): # if dict not empty, there's an error.  Let user know.
            msg = "Creating constraint '%s': unknown option(s)\n\t%s"
            msg = msg % ( tmpname, ', '.join(kwargs.keys()) )
            raise ValueError, msg

        NumericValue.__init__(self,tmpname,None,None,True)

        if None in self._data:
            self._data[None].name = self.name

        self.sense   = tmpsense
        self.rule    = tmprule
        self.trivial = False # True if all objective indicies have trivial expressions.
        self._constructed = False

    def __getstate__(self):

        numvalue_result = NumericValue.__getstate__(self)
        indexed_component_result = IndexedComponent.__getstate__(self)
        return dict(numvalue_result.items() + indexed_component_result.items())

    def __setstate__(self, state):

        NumericValue.__setstate__(self, state)
        IndexedComponent.__setstate__(self, state)
 
    def component(self):
        return self

    def clear(self):
        self._data = {}

    def __call__(self, exception=True):
        if len(self._data) == 0:
            return None
        if None in self._data:
            if self._data[None].expr is None:
                return None
            return self._data[None].expr()
        if exception:
            msg = 'Cannot compute the value of an array of objectives'
            raise ValueError, msg

    def dim(self):
        return self._ndim

    def __len__(self):
        return len(self._data.keys())

    def keys(self):
        return self._data.keys()
        #return self._index

    def __contains__(self,ndx):
        return ndx in self._data
        #return ndx in self._index

    def __getitem__(self,ndx):
        """This method returns a ObjectiveData object.  This object can be
           coerced to a numeric value using the value() function, or using
           explicity coercion with float().
        """
        if ndx in self._data:
            return self._data[ndx]
        msg = "Unknown index in objective '%s': %s"
        raise KeyError, msg % ( self.name, str(ndx) )

    def __iter__(self):
        return self._data.keys().__iter__()
        #return self._index.__iter__()

    def iteritems(self):
        return self._data.iteritems()

    def itervalues(self):
        return self._data.itervalues()

    def is_minimizing ( self ):
        return minimize == self.sense

    def construct(self, data=None):
        if __debug__:
            logger.debug("Constructing objective %s", self.name)
        if (self._no_rule_init is not None) and (self.rule is not None):
            msg = 'WARNING: noruleinit keyword is being used in conjunction ' \
                  "with rule keyword for objective '%s'; defaulting to "      \
                  'rule-based construction'
            print msg % self.name
        if self.rule is None:
            if self._no_rule_init is None:
                msg = 'WARNING: No construction rule or expression specified ' \
                      "for objective '%s'"
                print msg % self.name
            return
        if self._constructed:
            return
        self._constructed=True
        #
        if isinstance(self.rule,Expression) or isinstance(self.rule,_VarValue):
            if None in self._index or len(self._index) == 0 or self._index[None] is None:
                self._data[None].expr = self.rule
            else:
                msg = 'Cannot define multiple indices in an objective with a' \
                      'single expression'
                raise IndexError, msg
        #
        elif self.rule is not None:
            if self._ndim==0:
                tmp = self.rule(self.model())
                if tmp is None:
                    #logger.warning("DEPRECATION WARNING: Objective rule returned None instead of Objective.Skip")
                    raise ValueError, "Objective rule returned None instead of Objective.Skip"
                elif type(tmp) in (bool,int,long,float):
                    tmp = NumericConstant(None,None,tmp)
                if not (tmp.__class__ is tuple and tmp == Objective.Skip):
                    self._data[None].expr = tmp
            else:
                _name=self.name
                for val in self._index:
                    tmp = apply_indexed_rule(self, self.rule, self.model(), val)
                    if tmp is None:
                        #logger.warning("DEPRECATION WARNING: Objective rule returned None instead of Objective.Skip")
                        raise ValueError, "Objective rule returned None instead of Objective.Skip"
                    elif type(tmp) in (bool,int,long,float):
                        tmp = NumericConstant(None,None,tmp)

                    if not (tmp.__class__ is tuple and tmp == Objective.Skip):
                        self._data[val] = ObjectiveData(expr=tmp, name=create_name(_name,val), obj=self)
                        self._data[val].index = val
            #self._index = self._data.keys()

        if None in self._data:
            self._data[None].name = self.name
        #print "[%.1f] %s: %d,%d,%d" % \
        #      (time.time(), self.name,
        #       generate_expression.clone_counter,
        #       generate_relational_expression.clone_counter,
        #       generate_intrinsic_function_expression.clone_counter)


    def pprint(self, ostream=None, verbose=False):
        if ostream is None:
            ostream = sys.stdout
        print >>ostream, "  ",self.name,":",
        if not self.doc is None:
            print >>ostream, self.doc
            print >>ostream, "  ",
        print >>ostream, "\tSize="+str(len(self._data.keys())),
        if isinstance(self._index,_BaseSet):
            print >>ostream, "\tIndex=",self._index.name
        else:
            print >>ostream,""
        for key in self._data:
            if not self._data[key].expr is None:
                print >>ostream, "\t",
                self._data[key].expr.pprint(ostream, verbose=verbose)
                print >>ostream, ""

    def display(self, prefix="", ostream=None):
        if ostream is None:
            ostream = sys.stdout
        print >>ostream, prefix+"Objective "+self.name,":",
        print >>ostream, "  Size="+str(len(self))
        if None in self._data:
            if self._data[None].expr is None:
                val = 'none'
            else:
                val = pyutilib.misc.format_io(self._data[None].expr(exception=False))
            print >>ostream, '%s  Value=%s' % (prefix, val)
        else:
            for key in self._data:
                if not self._data[key].active:
                    continue
                val = self._data[key].expr(exception=False)
                print >>ostream, prefix+"  "+str(key)+" : "+str(val)
