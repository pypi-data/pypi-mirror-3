#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

__all__ = ['Objective', 'simple_objective_rule', '_ObjectiveData', 'minimize', 'maximize']

import sys
import logging
import weakref

import pyutilib.math
import pyutilib.misc
from pyutilib.component.core import alias

from numvalue import NumericValue, as_numeric
from expr import Expression
from indexed_component import IndexedComponent
from misc import create_name, apply_indexed_rule
from sets import _BaseSet
from var import _VarData
from set_types import Reals

#import time
#from coopr.pyomo.base.expr import generate_expression, generate_relational_expression
#from coopr.pyomo.base.intrinsic_functions import generate_intrinsic_function_expression

logger = logging.getLogger('coopr.pyomo')

minimize=1
maximize=-1


def simple_objective_rule( fn ):
    """
    This is a decorator that translates None into Constraint.Skip.
    This supports a simpler syntax in objective rules, though these
    can be more difficult to debug when errors occur.

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


class ObjectiveRepresentation(object):
    """
    A dummy class that contains the different representations that
    are used to process objectives.
    """


class _ObjectiveData(NumericValue):
    """
    This class defines the data for a single objective.

    Note that this is a subclass of NumericValue to allow
    objectives to be used as part of expressions.

    Constructor arguments:
        expr        The expression for this objective.
        name        The name of this objective.
        obj         The corresponding objective component.

    Public class attributes:
        active          A boolean that is true if this objective is active in the model.
        component       The objective component.
        domain          A domain object that restricts possible values for this objective.
        expr            The Pyomo expression for this objective
        id              An integer value that defines 
        index           The index value for this objective
        name            The name of this objective
        value           The numeric value of this objective

    Private class attributes:
        _repn           TBD
    """

    __slots__ = ['component', 'expr', 'id', 'active', 'repn', 'ampl_repn', 'index']

    def __init__(self, expr, name, obj):
        """
        Class constructor.
        """
        # Initialize values defined in NumericValue base class
        self.name = name
        self.domain = Reals
        self.value = None
        #
        self.active = True
        self.ampl_repn = None
        self.component = weakref.ref(obj)
        self.expr = expr
        self.id = -1
        self.index = None
        self.repn = None

    def __getstate__(self):
        """
        This method is required because this class uses slots.
        """
        result = NumericValue.__getstate__(self)
        for i in _ObjectiveData.__slots__:
            result[i] = getattr(self, i)
        if type(result['component']) is weakref.ref:
            result['component'] = result['component']()
        return result

    def __setstate__(self, state):
        """
        This method is required because this class uses slots.
        """
        for (slot_name, value) in state.iteritems():
            setattr(self, slot_name, value)
        self.component = weakref.ref(self.component)

    def __call__(self, exception=True):
        """
        Compute the value of this objective.

        This method does not simply return self.value because that data value may be out of date
        w.r.t. the value of decision variables.
        """
        if self.expr is None:
            return None
        return self.expr()

    def polynomial_degree(self):
        """
        Return the polynomial degree of the objective expression.
        """
        if self.expr is None:
            return None
        return self.expr.polynomial_degree()

    def activate(self):
        """
        Activate this objective.
        """
        self.active=True

    def deactivate(self):
        """
        Deactivate this objective.
        """
        self.active=False


class Objective(IndexedComponent, NumericValue):
    """
    This modeling component defines an objective expression.

    Note that this is a subclass of NumericValue to allow
    objectives to be used as part of expressions.

    Constructor arguments:
        expr            A Pyomo expression for this objective
        doc             A text string describing this component
        name            A name for this component
        noruleinit      Indicate that its OK that no initialization is
                            specified
        rule            A function that is used to construct objective
                            expressions
        sense           Indicate whether minimizing or maximizing
        
    Public class attributes:
        active          A boolean that is true if this component will be 
                            used to construct a model instance
        doc             A text string describing this component
        domain          A domain object that restricts possible values for this object.
        expr*           Not defined
        id*             Not defined
        index*          Not defined
        name            A name for this object.
        rule            The rule used to initialize the objective(s)
        sense           The objective sense
        trivial         A boolean if all objective indices have trivial expressions
        value           The numeric value of this object.

    Private class attributes:
        _constructed    A boolean that is true if this component has been
                            constructed
        _data           A dictionary from the index set to component data objects
        _index          The set of valid indices
        _index_set      A tuple of set objects that represents the index set
        _model          A weakref to the model that owns this component
        _ndim           The dimension of the index set
        _no_rule_init   A boolean that indicates if an initialization rule is needed
        _parent         A weakref to the parent block that owns this component
        _type           The class type for the derived subclass
    """

    alias('Objective', 'Expressions that are minimized or maximized in a model.')

    Skip        = (1000,)
    NoObjective = (1000,)

    def __init__(self, *args, **kwargs):
        """
        Constructor
        """
        # Initialize values defined in NumericValue base class
        self.domain = None
        self.value = None
        #
        self.sense = kwargs.pop('sense', minimize )
        tmprule  = kwargs.pop('rule', None )
        self.rule  = kwargs.pop('expr', tmprule )
        self._no_rule_init = kwargs.pop('noruleinit', None )
        self.trivial = False
        self._constructed = False
        #
        kwargs.setdefault('ctype', Objective)
        IndexedComponent.__init__(self, *args, **kwargs)
        #
        if args == ():
            self._data[None] = _ObjectiveData(None, self.name, self)

    def __getstate__(self):
        """
        This method is required because this class uses slots.  Call base class __getstate__
        methods since this class does not define additional slots.
        """
        numvalue_result = NumericValue.__getstate__(self)
        indexed_component_result = IndexedComponent.__getstate__(self)
        return dict(numvalue_result.items() + indexed_component_result.items())

    def __setstate__(self, state):
        """
        This method is required because this class uses slots.  Call base class __setstate__
        methods since this class does not define additional slots.
        """
        NumericValue.__setstate__(self, state)
        IndexedComponent.__setstate__(self, state)
 
    def __call__(self, exception=True):
        """
        Compute and return the value of this object.

        This method does not simply return self.value because that data value may be out of date
        w.r.t. the value of decision variables.
        """
        if len(self._data) == 0:
            return None
        if None in self._data:
            if self._data[None].expr is None:
                return None
            return self._data[None].expr()
        if exception:
            msg = 'Cannot compute the value of an array of objectives'
            raise ValueError, msg

    def is_minimizing ( self ):
        """Return true if this is a minimization objective"""
        return self.sense == minimize

    def construct(self, data=None):
        """Construct the expression(s) for this objective."""
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
        if isinstance(self.rule,Expression) or isinstance(self.rule,_VarData):
            if None in self._index or len(self._index) == 0 or self._index[None] is None:
                self._data[None].expr = self.rule
            else:
                msg = 'Cannot define multiple indices in an objective with a' \
                      'single expression'
                raise IndexError, msg
        #
        elif self.rule is not None:
            if self._ndim==0:
                tmp = self.rule(self._model())
                if tmp is None:
                    raise ValueError, "Objective rule returned None instead of Objective.Skip"
                if not (tmp.__class__ is tuple and tmp == Objective.Skip):
                    self._data[None].expr = as_numeric(tmp)
            else:
                _name=self.name
                for val in self._index:
                    tmp = apply_indexed_rule(self, self.rule, self._model(), val)
                    if tmp is None:
                        raise ValueError, "Objective rule returned None instead of Objective.Skip"
                    if not (tmp.__class__ is tuple and tmp == Objective.Skip):
                        self._data[val] = _ObjectiveData(as_numeric(tmp), create_name(_name,val), self)
                        self._data[val].index = val
        #
        if None in self._data:
            self._data[None].name = self.name
        #print "[%.1f] %s: %d,%d,%d" % \
        #      (time.time(), self.name,
        #       generate_expression.clone_counter,
        #       generate_relational_expression.clone_counter,
        #       generate_intrinsic_function_expression.clone_counter)


    def pprint(self, ostream=None, verbose=False):
        """Print the objective value(s)"""
        if ostream is None:
            ostream = sys.stdout
        print >>ostream, "  ",self.name,":",
        if not self.doc is None:
            print >>ostream, self.doc
            print >>ostream, "  ",
        print >>ostream, "\tSize="+str(len(self._data.keys())),
        if isinstance(self._index, _BaseSet):
            print >>ostream, "\tIndex=",self._index.name
        else:
            print >>ostream,""
        for key in self._data:
            if not self._data[key].expr is None:
                print >>ostream, "\t",
                self._data[key].expr.pprint(ostream, verbose=verbose)
                print >>ostream, ""

    def display(self, prefix="", ostream=None):
        """Provide a verbose display of this object"""
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

