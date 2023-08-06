#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

__all__ = ['Constraint', '_ConstraintData', 'ConstraintList', 'simple_constraint_rule', 'simple_constraintlist_rule']

import sys
import logging
import weakref

import pyutilib.math
import pyutilib.misc
from pyutilib.component.core import alias

from expr import Expression, generate_relational_expression, \
     _EqualityExpression, generate_expression
from numvalue import NumericValue, NumericConstant, ZeroConstant, value, \
     as_numeric
#from set_types import *
from indexed_component import IndexedComponent
from misc import create_name, apply_indexed_rule
from sets import _BaseSet, Set
from objective import Objective
from component import Component

logger = logging.getLogger('coopr.pyomo')


def simple_constraint_rule( fn ):
    """This is a decorator that translates None/True/False return values
    into Constraint.Skip/Constraint.Feasible/Constraint.Infeasible.
    This supports a simpler syntax in constraint rules, though these can be
    more difficult to debug when errors occur.

    Example use:

    @simple_constraint_rule
    def C_rule(model, i, j):
        ...
    """
    def wrapper_function ( *args, **kwargs ):
        value = fn( *args, **kwargs )
        if value is None:
            return Constraint.Skip
        elif value is True:
            return Constraint.Feasible
        elif value is False:
            return Constraint.Infeasible
        return value
    return wrapper_function


def simple_constraintlist_rule( fn ):
    """This is a decorator that translates None/True/False return values
    into ConstraintList.End/Constraint.Feasible/Constraint.Infeasible.
    This supports a simpler syntax in constraint rules, though these can be
    more difficult to debug when errors occur.

    Example use:

    @simple_constraintlist_rule
    def C_rule(model, i, j):
        ...
    """
    def wrapper_function ( *args, **kwargs ):
        value = fn( *args, **kwargs )
        if value is None:
            return ConstraintList.End
        elif value is True:
            return Constraint.Feasible
        elif value is False:
            return Constraint.Infeasible
        return value
    return wrapper_function



class _ConstraintData(object):
    """
    This class defines the data for a single constraint.

    Constructor arguments:
        name        The name of this objective.
        con         The corresponding constraint component.

    Public class attributes:
        active          A boolean that is true if this constraint is active in the model.
        component       The constraint component.
        domain          A domain object that restricts possible values for this constraint.
        expr            The Pyomo expression for this constraint
        id              An integer value that defines 
        index           The index value for this constraint
        name            The name of this constraint
        value           The numeric value of the constraint body

    Private class attributes:
        _repn           TBD
    """

    __slots__ = ('active', 'ampl_repn', 'body', 'component', 'dual', 
                 'index', 'lin_body', 'lower', 'name', 'repn', 'slack', 'upper', 'value',
                 '_equality')

    def __init__(self, name, con):
        self.active = True
        self.ampl_repn = None
        self.body = None 
        # an expression tree encoding of the constraint body. if None, an alternative representation (e.g., lin_body) will be != None.
        self.component = weakref.ref(con)
        self.dual = None
        self.index = None
        self.lin_body = None # a linear compilation of the source expressions tree.
        self.lower = None
        self.name = name
        self.repn = None
        self.slack = None
        self.upper = None
        self.value = None
        self._equality = False

    def __getstate__(self):
        """
        This method is required because this class uses slots.
        """
        result = {}
        for i in _ConstraintData.__slots__:
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
        Compute the value of the body of this constraint.

        This method does not simply return self.value because that data value may be out of date
        w.r.t. the value of decision variables.
        """

        if self.body is None:
            return None
        return self.body()

    def activate(self):
        self.active=True

    def deactivate(self):
        self.active=False


class Constraint(IndexedComponent, NumericValue):
    """An object that defines a objective expression"""

    alias("Constraint", "Constraint expressions in a model.")

    NoConstraint    = (1000,)
    Skip            = (1000,)
    Infeasible      = (1001,)
    Violated        = (1001,)
    Feasible        = (1002,)
    Satisfied       = (1002,)

    def __init__(self, *args, **kwargs):
        """
        Construct an objective expression with rule to construct the
        expression

        keyword arguments:
        name: name of this object
        rule: function or rule definition of constraint
        expr: same as rule
        doc:  documentation string for constraint
        """
        tmprule = kwargs.pop('rule', None )
        tmprule = kwargs.pop('expr', tmprule )
        self.rule = tmprule
        self.trivial = False
        self._no_rule_init = kwargs.pop('noruleinit', None )
        self.domain = None
        self.value = None
        #
        kwargs.setdefault('ctype', Constraint)
        IndexedComponent.__init__(self, *args, **kwargs)
        #
        if None in self._data:
            self._data[None].name=self.name

    def __getstate__(self):
        """TODO"""
        numvalue_result = NumericValue.__getstate__(self)
        constraint_base_result = IndexedComponent.__getstate__(self)
        return dict(numvalue_result.items() + constraint_base_result.items())

    def __setstate__(self, state):
        """TODO"""
        NumericValue.__setstate__(self, state)
        IndexedComponent.__setstate__(self, state)

    def __call__(self, exception=True):
        """Compute the value of the constraint body"""
        if len(self._data) == 0:
            return None
        if None in self._data:
            if self._data[None].body is None:
                return None
            return value(self._data[None].body)
        if exception:
            msg = 'Cannot compute the value of an array of constraints'
            raise ValueError, msg

    def construct(self, data=None):
        """TODO"""
        #
        # cache the debug generation flag, to avoid the expense of
        # calling isEnabledFor() for each index - this is far too
        # expensive an operation to perform deep in a loop. the only
        # potential down-side is that the debug logging is either
        # disabled or enabled globally for the duration of this
        # method invocation - which doesn't seem like much of
        # (if any) limitation in practice.
        #
        generate_debug_messages = (__debug__ is True) and (logger.isEnabledFor(logging.DEBUG) is True)

        if generate_debug_messages is True:
            logger.debug("Constructing constraint %s",self.name)

        if (self._no_rule_init is not None) and (self.rule is not None):
            logger.warn("noruleinit keyword is being used in conjunction with "
                        "rule keyword for constraint '%s'; defaulting to "
                        "rule-based construction.", self.name)
        if self.rule is None:
            if self._no_rule_init is None:
                logger.warn("No construction rule or expression specified for "
                            "constraint '%s'", self.name)
            return
        if self._constructed:
            return
        self._constructed=True
        #
        # Local variables for code optimization
        #
        _self_rule = self.rule
        _self_model = self._model()
        #
        # a somewhat gory way to see if you have a singleton - the len()=1 check is 
        # needed to avoid "None" being passed illegally into set membership validation rules.
        #
        if (len(self._index) == 1) and (None in self._index): 
            if len(self._index) != 1:
                raise IndexError, "Internal error: constructing constraint "\
                    "with both None and Index set"
            if generate_debug_messages:
                logger.debug("  Constructing single constraint (index=None)")
            if isinstance(_self_rule,Expression):
                expr = _self_rule
            else:
                expr = _self_rule(_self_model)
            self.add(None, expr)
        else:
            if isinstance(_self_rule,Expression):
                raise IndexError, "Cannot define multiple indices in a " \
                    "constraint with a single expression"
            for index in self._index:
                if generate_debug_messages:
                    logger.debug("  Constructing constraint index "+str(index))
                self.add( index, apply_indexed_rule( self, _self_rule,
                                                     _self_model, index ) )

    def add(self, index, expr):
        # index: the constraint index (should probably be renamed)
        # expr: the constraint expression

        # Convert deprecated expression values
        if expr is None:
            raise ValueError, "Expression defined using None instead of Constraint.Skip - constraint=%s" % create_name(self.name, index)
        if expr is True:
            raise ValueError, "Expression defined using True instead of Constraint.Feasible - constraint=%s" % create_name(self.name, index)
        if expr is False:
            raise ValueError, "Expression defined using False instead of Constraint.Infeasible - constraint=%s" % create_name(self.name, index)
        #
        expr_type = type(expr)
        #
        # Ignore an 'empty' constraint
        #
        if expr_type is tuple and len(expr) == 1:
            if expr == Constraint.Skip or expr == Constraint.Feasible:
                return
            if expr == Constraint.Infeasible:
                raise ValueError, "Constraint '%s' is always infeasible" % create_name(self.name,index)
        #
        #
        # Local variables to optimize runtime performance
        #
        conData = _ConstraintData(create_name(self.name,index), self)
        conData.index = index
        #
        if expr_type is tuple: # or expr_type is list:
            #
            # Form equality expression
            #
            if len(expr) == 2:
                arg0 = expr[0]
                if arg0 is not None:
                    arg0 = as_numeric(arg0)
                arg1 = expr[1]
                if arg1 is not None:
                    arg1 = as_numeric(arg1)

                conData._equality = True
                if arg1 is None or arg1.is_constant():
                    conData.lower = conData.upper = arg1
                    conData.body = arg0
                elif arg0 is None or arg0.is_constant():
                    conData.lower = conData.upper = arg0
                    conData.body = arg1
                else:
                    conData.lower = conData.upper = ZeroConstant
                    conData.body = arg0 - arg1
            #
            # Form inequality expression
            #
            elif len(expr) == 3:
                arg0 = expr[0]
                if arg0 is not None:
                    arg0 = as_numeric(arg0)
                    if not arg0.is_constant():
                        msg = "Constraint '%s' found a 3-tuple (lower, " \
                              "expression, upper) but the lower value was "\
                              "non-constant"
                        raise ValueError, msg % (conData.name,)

                arg1 = expr[1]
                if arg1 is not None:
                    arg1 = as_numeric(arg1)

                arg2 = expr[2]
                if arg2 is not None:
                    arg2 = as_numeric(arg2)
                    if not arg2.is_constant():
                        msg = "Constraint '%s' found a 3-tuple (lower, " \
                              "expression, upper) but the upper value was "\
                              "non-constant"
                        raise ValueError, msg % (conData.name,)

                conData.lower = arg0
                conData.body  = arg1
                conData.upper = arg2
            else:
                msg = "Constructor rule for constraint '%s' returned a tuple" \
                      ' of length %d.  Expecting a tuple of length 2 or 3:\n' \
                      'Equality:   (left, right)\n' \
                      'Inequality: (lower, expression, upper)'
                raise ValueError, msg % ( self.name, len(expr) )

            relational_expr = False
        else:
            try:
                relational_expr = expr.is_relational()
                if not relational_expr:
                    msg = "Constraint '%s' does not have a proper value.  " \
                          "Found '%s'\nExpecting a tuple or equation.  " \
                          "Examples:\n" \
                          "    summation( model.costs ) == model.income\n" \
                          "    (0, model.price[ item ], 50)"
                    raise ValueError, msg % ( conData.name, str(expr) )
            except:
                msg = "Constraint '%s' does not have a proper value.  " \
                      "Found '%s'\nExpecting a tuple or equation.  " \
                      "Examples:\n" \
                      "    summation( model.costs ) == model.income\n" \
                      "    (0, model.price[ item ], 50)" \
                      % ( conData.name, str(expr) )
                if type(expr) is bool:
                    msg +="""
Note: constant Boolean expressions are not valid constraint expressions.
Some apparently non-constant compound inequalities (e.g. "expr >= 0 <= 1")
can return boolean values; the proper form for compound inequalities is
always "lb <= expr <= ub"."""
                raise ValueError, msg
        #
        # Special check for chainedInequality errors like "if var < 1:"
        # within rules.  Catching them here allows us to provide the
        # user with better (and more immediate) debugging information.
        # We don't want to check earlier because we want to provide a
        # specific debugging message if the construction rule returned
        # True/False; for example, if the user did ( var < 1 > 0 )
        # (which also results in a non-None chainedInequality value)
        #
        if generate_relational_expression.chainedInequality is not None:
            from expr import chainedInequalityErrorMessage
            raise TypeError, chainedInequalityErrorMessage()
        #
        # Process relational expressions (i.e. explicit '==', '<', and '<=')
        #
        if relational_expr:
            if expr_type is _EqualityExpression:
                # Equality expression: only 2 arguments!
                conData._equality = True
                if expr._args[1].is_constant():
                    conData.lower = conData.upper = expr._args[1]
                    conData.body = expr._args[0]
                elif expr._args[0].is_constant():
                    conData.lower = conData.upper = expr._args[0]
                    conData.body = expr._args[1]
                else:
                    conData.lower = conData.upper = ZeroConstant
                    conData.body = generate_expression('_','sub', expr._args[0], expr._args[1])
            else:
                # Inequality expression: 2 or 3 arguments
                if len(expr._args) == 3:
                    if not expr._args[0].is_constant():
                        msg = "Constraint '%s' found a double-sided "\
                              "inequality expression (lower <= expression "\
                              "<= upper) but the lower bound was non-constant"
                        raise ValueError, msg % (conData.name,)
                    if not expr._args[2].is_constant():
                        msg = "Constraint '%s' found a double-sided "\
                              "inequality expression (lower <= expression "\
                              "<= upper) but the upper bound was non-constant"
                        raise ValueError, msg % (conData.name,)
                    conData.lower = expr._args[0]
                    conData.body  = expr._args[1]
                    conData.upper = expr._args[2]
                else:
                    if expr._args[1].is_constant():
                        conData.lower = None
                        conData.body  = expr._args[0]
                        conData.upper = expr._args[1]
                    elif expr._args[0].is_constant():
                        conData.lower = expr._args[0]
                        conData.body  = expr._args[1]
                        conData.upper = None
                    else:
                        conData.lower = None
                        conData.body  = generate_expression('_','sub', expr._args[0], expr._args[1])
                        conData.upper = ZeroConstant
        #
        # Replace numeric bound values with a NumericConstant object,
        # and reset the values to 'None' if they are 'infinite'
        #
        if conData.lower is not None:
            val = conData.lower()
            if not pyutilib.math.is_finite(val):
                if val > 0:
                    msg = "Constraint '%s' created with a +Inf lower bound"
                    raise ValueError, msg % ( conData.name, )
                conData.lower = None
            elif bool(val > 0) == bool(val <= 0):
                msg = "Constraint '%s' created with a non-numeric lower bound"
                raise ValueError, msg % ( conData.name, )
        if conData.upper is not None:
            val = conData.upper()
            if not pyutilib.math.is_finite(val):
                if val < 0:
                    msg = "Constraint '%s' created with a -Inf upper bound"
                    raise ValueError, msg % ( conData.name, )
                conData.upper = None
            elif bool(val > 0) == bool(val <= 0):
                msg = "Constraint '%s' created with a non-numeric upper bound"
                raise ValueError, msg % ( conData.name, )
        #
        # Error check, to ensure that we don't have a constraint that
        # doesn't depend on any variables / parameters
        #
        # Error check, to ensure that we don't have an equality constraint with
        # 'infinite' RHS
        #
        if conData._equality:
            if conData.lower != conData.upper: #pragma:nocover
                msg = "Equality constraint '%s' has non-equal lower and "\
                      "upper bounds (this is indicitive of a SERIOUS "\
                      "internal error in Pyomo)."
                raise RuntimeError, msg % self.name
            if conData.lower is None:
                msg = "Equality constraint '%s' defined with non-finite term"
                raise ValueError, msg % self.name
        #
        # hook up the constraint data object to the parent constraint.
        #
        self._data[index] = conData

    def pprint(self, ostream=None, verbose=False):
        """TODO"""
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
        for val in self._data:
            if not val is None:
                print >>ostream, "\t"+`val`
            if self._data[val].lower is not None:
                print >>ostream, "\t\t",
                if self._data[val].lower.is_expression():
                    self._data[val].lower.pprint(ostream)
                else:
                    print >>ostream, str(self._data[val].lower)
            else:
                print >>ostream, "\t\t-Inf"
            print >>ostream, "\t\t<="
            if self._data[val].body is not None:
                print >>ostream, "\t\t",
                if self._data[val].body.is_expression():
                    self._data[val].body.pprint(ostream)
                else:
                    print >>ostream, str(self._data[val].body)
            print >>ostream, "\t\t<="
            if self._data[val].upper is not None:
                print >>ostream, "\t\t",
                if self._data[val].upper.is_expression():
                    self._data[val].upper.pprint(ostream)
                else:
                    print >>ostream, str(self._data[val].upper)
            elif self._data[val]._equality:
                print >>ostream, "\t\t",
                if self._data[val].lower.is_expression():
                    self._data[val].lower.pprint(ostream)
                else:
                    print >>ostream, str(self._data[val].lower)
            else:
                print >>ostream, "\t\tInf"

    def display(self, prefix="", ostream=None):
        """TODO"""
        if ostream is None:
            ostream = sys.stdout
        print >>ostream, prefix+"Constraint "+self.name,":",
        print >>ostream, "  Size="+str(len(self))
        if None in self._data:
            if self._data[None].body is None:
                val = 'none'
            else:
                val = pyutilib.misc.format_io(self._data[None].body())
            print >>ostream, '%s  Value=%s' % (prefix, val)
        else:
            flag=True
            for key in self._data:
                if not self._data[key].active:
                    continue
                if flag:
                    print >>ostream, prefix+"        \tLower\tBody\t\tUpper"
                    flag=False
                if self._data[key].lower is not None:
                    lval = str(self._data[key].lower())
                else:
                    lval = "-Infinity"
                val = str(self._data[key].body())
                if self._data[key].upper is not None:
                    uval = str(self._data[key].upper())
                else:
                    uval = "Infinity"
                print >>ostream, "%s  %s :\t%s\t%s\t%s" % (
                                 prefix, str(key), lval, val, uval )
            if flag:
                print >>ostream, prefix+"  None active"


class ConstraintList(Constraint):
    """
    A constraint component that represents a list of constraints.  Constraints can
    be indexed by their index, but when they are added an index value is not specified.
    """

    alias("ConstraintList", "A list of constraints in a model.")

    End             = (1003,)

    def __init__(self, *args, **kwargs):
        """Constructor"""
        if len(args) > 0:
            raise ValueError, "Cannot specify indices for a ConstraintList object"
        #
        self._hidden_index = Set()
        targs = [self._hidden_index]
        self._nconstraints = 0
        kwargs.setdefault('ctype', ConstraintList)
        Constraint.__init__(self, *targs, **kwargs)

    def construct(self, *args, **kwds):
        """TODO"""
        self._hidden_index.construct()
        Constraint.construct(self, *args, **kwds)

    def construct(self, data=None):
        """TODO"""
        #
        generate_debug_messages = (__debug__ is True) and \
                                  (logger.isEnabledFor(logging.DEBUG) is True)

        if generate_debug_messages is True:
            logger.debug("Constructing constraint list %s",self.name)

        if (self._no_rule_init is not None) and (self.rule is not None):
            msg = 'WARNING: noruleinit keyword is being used in conjunction ' \
                  "with rule keyword for constraint '%s'; defaulting to "     \
                  'rule-based construction.'
            print msg % self.name
        if self.rule is None:
            return
        if self._constructed:
            return
        self._constructed=True
        #
        # Local variables for code optimization
        #
        _self_rule = self.rule
        _self_model = self._model()
        #
        while True:
            val = self._nconstraints + 1
            if generate_debug_messages:
                logger.debug("   Constructing constraint index "+str(val))
            expr = apply_indexed_rule( self, _self_rule, _self_model, val )
            if expr is None:
                #logger.warning("DEPRECATION WARNING: Constraint rule returned None instead of ConstraintList.End")
                raise ValueError, "Constraint rule returned None instead of ConstraintList.End"
            if (expr.__class__ is tuple and expr == ConstraintList.End) or \
               (type(expr) in (int, long, float) and expr == 0):
                break
            self.add(expr)

    def add(self, *args):
        """TODO"""
        self._nconstraints += 1
        targs = [self._nconstraints] + list(args)
        Constraint.add(self, *targs)

