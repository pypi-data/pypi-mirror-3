#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the FAST README.txt file.
#  _________________________________________________________________________

from __future__ import division

__all__ = [ 'generate_canonical_repn', 'as_expr', 'canonical_is_constant', 
            'canonical_is_linear', 'canonical_is_quadratic', 'canonical_is_nonlinear' ]

import logging
from coopr.pyomo.base import IPyomoPresolver, IPyomoPresolveAction, Model, \
                             Constraint, Objective
from coopr.pyomo.base import expr
from coopr.pyomo.base.connector import _ConnectorValue
from coopr.pyomo.base.var import _VarData, Var
import copy


logger = logging.getLogger('coopr.pyomo')
#
# A frozen dictionary that can be hashed.  This dictionary isn't _really_
# frozen, but it acts hashable.
#
class frozendict(dict):

    __slots__ = ['_hash']

    def __hash__(self):
        rval = getattr(self, '_hash', None)
        if rval is None:
            rval = self._hash = hash(frozenset(self.iteritems()))
        return rval

    # getstate and setstate are currently not defined in a generic manner, i.e.,
    # we assume the underlying dictionary is the only thing

    def __getstate__(self):
        return self.items()

    def __setstate__(self, dictionary):
        self.clear()
        self.update(dictionary)
        self._hash = None

#
# Generate a canonical representation of an expression.
#
# The canonical representation is a dictionary.  Each element is a mapping
# from a term degree to terms in the expression.  If the term degree is
# None, then the map value is simply an expression of terms without a
# specific degree.  Otherwise, the map value is a dictionary of terms to
# their coefficients.  A term is represented as a frozen dictionary that
# maps variable id to variable power.  A constant term is represented
# with None.
#
# Examples:
#  Let x[1] ... x[4] be the first 4 variables, and
#      y[1] ... y[4] be the next 4 variables
#
# 1.3                           {0:{ None :1.3}}
# 3.2*x[1]                      {1:{ {0:1} :3.2}}
# 2*x[1]*y[2] + 3*x[2] + 4      {0:{None:4.0}, 1:{{1:1}:3.0}, 2:{{0:1, 5:1}:2.0}}
# 2*x[1]**4*y[2]    + 4         {0:{None:4.0}, 1:{{1:1}:3.0}, 5:{{0:4, 5:1 }:2.0}}
# log(y[1]) + x[1]*x[1]         {2:{{0:2}:1.0}, None:log(y[1])}
#

def generate_canonical_repn(exp, idMap=None):
    degree = exp.polynomial_degree()
    if degree == 1:
        # varmap is a map from the variable hash to a _VarData.
        # coef is a map from the variable hash to it's coefficient.
        coef, varmap = collect_linear_canonical_repn(exp, idMap)
        ans = {}
        if None in coef:
            val = coef.pop(None)
            if val != 0:
                ans[0] = { None: val }
        ans[1] = coef
        ans[-1] = varmap
        return ans
    elif degree > 1:
        ans = collect_general_canonical_repn(exp, idMap)
        if 1 in ans:
            linear_terms = {}
            for key, coef in ans[1].iteritems():
                linear_terms[key.keys()[0]] = coef
            ans[1] = linear_terms
        return ans
    elif degree == 0:
        return { 0: { None:exp() } }
    else:
        return { None: exp, -1 : collect_variables(exp, idMap) }


def as_expr(rep, vars=None, model=None, ignore_other=False):
    """ Convert a canonical representation into an expression. """
    if isinstance(model, Model):
        vars = model._var
        id_offset=0
    elif not vars is None:
        id_offset=1
    exp = 0.0
    for d in rep:
        if d is None:
            if not ignore_other:
                exp += rep[d]
            continue
        if d is -1:
            continue
        for v in rep[d]:
            if v is None:
                exp += rep[d][v]
                continue
            e = rep[d][v]
            for id in v:
                for i in xrange(v[id]):
                    if vars is None:
                        e *= rep[-1][id]
                    else:
                        e *= vars[id[1]+id_offset]
            exp += e
    return exp

def repn_add(lhs, rhs, coef=1.0):
    """
    lhs and rhs are the expressions being added together.
    'lhs' and 'rhs' are left-hand and right-hand side operands
    See generate_canonical_repn for explanation of pyomo expressions
    """
    for order in rhs:
        # For each order term, first-order might be 3*x,
        # second order 4*x*y or 5*x**2
        if order is None:
            # i.e., (currently) order is a constant or logarithm
            if order in lhs:
                lhs[order] += rhs[order]
            else:
                lhs[order] = rhs[order]
            continue
        if order < 0:
            # ignore now, handled below
            continue
        if not order in lhs:
            lhs[order] = {}
        for var in rhs[order]:
            # Add coefficients of variables in this order (e.g., third power)
            lhs[order][var] = coef*rhs[order][var] + lhs[order].get(var,0.0)
    #
    # Merge the _VarData maps
    #
    if -1 in rhs:
        if -1 in lhs:
            lhs[-1].update(rhs[-1])
        else:
            lhs[-1] = rhs[-1]
    return lhs


def repn_mult(r1, r2, coef=1.0):
    rep = {}
    for d1 in r1:
        for d2 in r2:
            if d1 == None or d2 == None or d1 < 0 or d2 < 0:
                pass
            else:
                d=d1+d2
                if not d in rep:
                    rep[d] = {}
                if d == 0:
                    rep[d][None] = coef * r1[0][None] * r2[0][None]
                elif d1 == 0:
                    for v2 in r2[d2]:
                        rep[d][v2]  = coef * r1[0][None] * r2[d2][v2] + rep[d].get(v2,0.0)
                elif d2 == 0:
                    for v1 in r1[d1]:
                        rep[d][v1]  = coef * r1[d1][v1] * r2[0][None] + rep[d].get(v1,0.0)
                else:
                    for v1 in r1[d1]:
                        for v2 in r2[d2]:
                            v = frozendict(v1)
                            for id in v2:
                                if id in v:
                                    v[id] += v2[id]
                                else:
                                    v[id]  = v2[id]
                            rep[d][v] = coef * r1[d1][v1] * r2[d2][v2] + rep[d].get(v,0.0)
    #
    # Handle other nonlinear terms
    #
    if None in r1:
        rep[None] = as_expr(r2, ignore_other=True) * copy.deepcopy(r1[None])
        if None in r2:
            rep[None] += copy.deepcopy(r1[None])*copy.deepcopy(r2[None])
    if None in r2:
        if None in rep:
            rep[None] += as_expr(r1, ignore_other=True) * copy.deepcopy(r2[None])
        else:
            rep[None]  = as_expr(r1, ignore_other=True) * copy.deepcopy(r2[None])
    #
    # Merge the _VarData maps
    #
    if -1 in r1:
        rep[-1] = r1[-1]
    if -1 in r2:
        if -1 in rep:
            rep[-1].update(r2[-1])
        else:
            rep[-1] = r2[-1]
    #
    # Return the canonical repn
    #
    return rep


def collect_variables(exp, idMap):
    if exp.is_expression():
        ans = {}
        if exp.__class__ is expr._ProductExpression:
            for subexp in exp._numerator:
                ans.update(collect_variables(subexp, idMap))
            for subexp in exp._denominator:
                ans.update(collect_variables(subexp, idMap))
        else:
            # This is fragile: we assume that all other expression
            # objects "play nice" and just use the _args member.
            for subexp in exp._args:
                ans.update(collect_variables(subexp, idMap))
        return ans
    elif exp.is_constant():
        # NB: is_constant() returns True for variables with fixed values
        return {}
    elif exp.__class__ is _VarData or exp.type() is Var:
        key = idMap is None and id(exp) or idMap.setdefault(id(exp), len(idMap))
        return { key : exp }
    else:
        raise ValueError, "Unexpected expression type: "+str(exp)

def collect_linear_canonical_repn(exp, idMap):

    # we already know this is a linear expression. given the cost of recursion / function
    # calls in Python, do some local optimization. specifically, we know with very high
    # probability (minus some very weird expression trees) that the sub-arguments to 
    # a sum expression are either constants or variables.

    #
    # Ignore identity expressions
    #

    while exp.__class__ is expr._IdentityExpression:
        exp = exp._args[0]

    # constants and _VarData are more frequent than expressions - look for them first, for efficiency.
    if exp.is_constant():
        # NB: is_constant() returns True for variables with fixed values
        return { None: exp() }, {}
    elif exp.__class__ is _VarData:
        key = idMap is None and id(exp) or idMap.setdefault(id(exp), len(idMap))
        return { key : 1.0 }, { key : exp }
    elif exp.is_expression():
        if exp.__class__ is expr._ProductExpression:
            # OK - the following is safe ONLY because we verify the
            # expression order before entering here -- so we know that
            # there will be no more than 1 variable in the product
            # expression (and that that variable will appear in the
            # numerator!)
            coef = None
            varmap = None
            const = exp.coef
            for subexp in exp._denominator:
                x = subexp() # only have constants in the denominator.
                if x == 0:
                    import StringIO
                    buf = StringIO.StringIO()
                    subexp.pprint(buf)
                    logger.error("Divide-by-zero: offending sub-expression:\n   " + buf)
                    raise ZeroDivisionError
                const /= x
            for subexp in exp._numerator:

                if subexp.is_constant():
                     _coef, _varmap = { None: subexp() }, {}
                elif subexp.__class__ is _VarData:
                    key = idMap is None and id(subexp) or \
                        idMap.setdefault(id(subexp), len(idMap))
                    _coef, _varmap = { key : 1.0 }, { key : subexp }
                else:
                    _coef, _varmap = collect_linear_canonical_repn(subexp, idMap)

                if _varmap:
                    varmap = _varmap
                    coef = _coef
                else:
                    const *= _coef[None]

            if coef:
                if const != 1:
                    for var in coef.iterkeys():
                        coef[var] *= const
                return coef, varmap
            else:
                return { None: const }, {}
        elif exp.__class__ is expr._SumExpression:
            coef = { None : exp._const } # None is the constant term in the coefficient map.
            varmap = {}
            for i in xrange(len(exp._args)):

                arg_coef = exp._coef[i]
                arg = exp._args[i]


                if (arg.__class__ is _VarData) and (arg.fixed is False):
                    # save an expensive recursion - this is by far the most common case.
                    key = idMap is None and id(arg) or \
                        idMap.setdefault(id(arg), len(idMap))
                    varmap.setdefault(key, arg)
                    coef[key] = coef.get(key, 0.0) + arg_coef
                else:
                    if arg.is_constant():
                        _coef, _varmap = { None: arg() }, {}
                    else:
                        _coef, _varmap = collect_linear_canonical_repn(arg, idMap)
                    varmap.update(_varmap)
                    for var, val in _coef.iteritems():
                        coef[var] = coef.get(var,0.0) + val * arg_coef

            return coef, varmap
        else:
            raise ValueError( "Unsupported expression (type %s):\n%s" %
                              (type(exp).__name__, str(exp)) )
    elif exp.type() is Var:
        key = idMap is None and id(exp) or idMap.setdefault(id(exp), len(idMap))
        return { key : 1.0 }, { key : exp }
    elif isinstance(exp, _ConnectorValue):
        return {},{}
    else:
        raise ValueError( "Unexpected expression (type %s): %s" %
                          (type(exp).__name__, str(exp)) )


#
# Temporary canonical expressions
#
# temp_const = { 0: {None:0.0} }
# temp_var = { 1: {frozendict({None:1}):1.0} }
# temp_nonl = { None: None }

#
# Internal function for collecting canonical representation, which is
# called recursively.
#
def collect_general_canonical_repn(exp, idMap):
#     global temp_const
#     global temp_var
#     global temp_nonl
    temp_const = { 0: {None:0.0} }
    temp_var = { 1: {frozendict({None:1}):1.0} }
    temp_nonl = { None: None }
    #
    # Ignore identity expressions
    #
    while isinstance(exp, expr._IdentityExpression):
        exp = exp._args[0]
    #
    # Expression
    #
    if isinstance(exp,expr.Expression):
        #
        # Sum
        #
        if isinstance(exp,expr._SumExpression):
            if exp._const != 0.0:
                repn = { 0: {None:exp._const} }
            else:
                repn = {}
            for i in xrange(len(exp._args)):
                repn = repn_add(repn, collect_general_canonical_repn(exp._args[i], idMap), coef=exp._coef[i] )
            return repn
        #
        # Product
        #
        elif isinstance(exp,expr._ProductExpression):
            #
            # Iterate through the denominator.  If they aren't all constants, then
            # simply return this expresion.
            #
            denom=1.0
            for e in exp._denominator:
                if e.fixed_value():
                    #print 'Z',type(e),e.fixed
                    denom *= e.value
                elif e.is_constant():
                    denom *= e()
                else:
                    temp_nonl[None] = exp
                    return temp_nonl
                if denom == 0.0:
                    print "Divide-by-zero error - offending sub-expression:"
                    e.pprint()
                    raise ZeroDivisionError
            #
            # OK, the denominator is a constant.
            #
            repn = { 0: {None:exp.coef / denom} }
            #print "Y",exp.coef/denom
            for e in exp._numerator:
                repn = repn_mult(repn, collect_general_canonical_repn(e, idMap))
            return repn
        #
        # ERROR
        #
        else:
            raise ValueError, "Unsupported expression type: "+str(exp)
    #
    # Constant
    #
    elif exp.fixed_value():
        temp_const[0][None] = exp.value
        return temp_const
    #
    # Variable
    #
    elif type(exp) is _VarData or exp.type() is Var:
        key = idMap is None and id(exp) or idMap.setdefault(id(exp), len(idMap))
        temp_var = { -1: {key:exp}, 1: {frozendict({key:1}):1.0} }
        return temp_var
    #
    # Connector
    #
    elif type(exp) is _ConnectorValue or exp.type() is Connector:
        # Silently omit constraint...  The ConnectorExpander should
        # expand this constraint into indvidual constraints that
        # reference "real" variables.
        return {}
    #
    # ERROR
    #
    else:
        raise ValueError("Unexpected expression (type %s): " %
                         ( type(exp).__name__, str(exp) ))



def canonical_is_constant(repn):
    """Return True if the canonical representation is a constant expression"""
    return max(repn.iterkeys()) == 0 and None not in repn
    for key in repn:
        if key is None or key > 0:
            return False
    return True

def canonical_is_nonlinear(repn):
    """Return True if the canonical representation is a nonlinear expression"""
    return max(repn.iterkeys()) > 1 or None in repn
    for key in repn:
        if not key in [-1,0,1]:
            return True
    return False

def canonical_is_linear(repn):
    return max(repn.iterkeys()) == 1 and None not in repn
    """Return True if the canonical representation is a linear expression."""
    return (1 in repn) and not is_nonlinear(repn)

def canonical_is_quadratic(repn):
    """Return True if the canonical representation is a quadratic expression."""
    return max(repn.iterkeys()) == 2 and None not in repn
    if not 2 in repn:
        return False
    for key in repn:
        if key is None or key > 2:
            return False
    return True

