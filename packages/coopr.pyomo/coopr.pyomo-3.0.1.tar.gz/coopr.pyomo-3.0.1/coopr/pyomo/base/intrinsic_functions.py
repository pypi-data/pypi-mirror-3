#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

#
# TODO:  Do we need to have different Expression objects for different
#        intrinsic expressions?
# TODO:  If an expression has a fixed value, should we simply call the
#        intrinsic function with the value of that expression?
# TODO:  Do we need to register these expression objects?
#

__all__ = [ 'log', 'log10', 'sin', 'cos', 'tan', 'cosh', 'sinh', 'tanh',
            'asin', 'acos', 'atan', 'exp', 'sqrt', 'asinh', 'acosh', 
            'atanh', 'ceil', 'floor' ]

import math
import sys

from component import Component
from expr import _IntrinsicFunctionExpression
from numvalue import NumericValue, as_numeric


def generate_intrinsic_function_expression(args, nargs, name, fcn):
    def _clone_if_needed(obj):
        count = sys.getrefcount(obj) - \
                generate_intrinsic_function_expression.UNREFERENCED_EXPR_COUNT
        if generate_intrinsic_function_expression.clone_if_needed_callback:
            generate_intrinsic_function_expression.clone_if_needed_callback(count)
        if count == 0:
            return obj
        elif count > 0:
            generate_intrinsic_function_expression.clone_counter += 1
            return obj.clone()
        else:
            raise RuntimeError, "Expression entered " \
                "generate_intrinsic_function_expression() " \
                "with too few references (%s<0); this is indicative of a " \
                "SERIOUS ERROR in the expression reuse detection scheme." \
                % ( count, )

    # Special handling: if there are no Pyomo Modeling Objects in the
    # argument list, then evaluate the expression and return the result.
    pyomo_expression = False
    for arg in args:
        # FIXME: does anyone know why we also test for 'Component' here? [JDS]
        if isinstance(arg, NumericValue) or isinstance(arg, Component):
            # TODO: efficiency: we already know this is a NumericValue -
            # so we should be able to avoid the call to as_numeric()
            # below (expecially since most intrinsic functions are unary
            # operators.
            pyomo_expression = True
            break
    if not pyomo_expression:
        return fcn(*args)

    new_args = []
    for arg in args:
        new_arg = as_numeric(arg)
        if new_arg.is_expression():
            new_arg = _clone_if_needed(new_arg)
        elif new_arg.is_indexed():
            raise ValueError, "Argument for intrinsic function '%s' is an "\
                "n-ary numeric value: %s\n    Have you given variable or "\
                "parameter '%s' an index?" % (name, new_arg.name, new_arg.name)
        new_args.append(new_arg)
    return _IntrinsicFunctionExpression(name, nargs, tuple(new_args), fcn)

# [testing] clone_check_callback allows test functions to intercept the
# call to _clone_if_needed and see the returned value from
# sys.getrefcount.
generate_intrinsic_function_expression.clone_if_needed_callback = None

# [debugging] clone_counter is a count of the number of calls to
# expr.clone() made during expression generation.
generate_intrinsic_function_expression.clone_counter = 0

# [configuration] UNREFERENCED_EXPR_COUNT is a "magic number" that
# indicates the stack depth between "normal" modeling and
# _clone_if_needed().  If an expression enters _clone_if_needed() with
# UNREFERENCED_EXPR_COUNT references, then there are no other variables
# that hold a reference to the expression and cloning is not necessary.
# If there are more references than UNREFERENCED_EXPR_COUNT, then we
# must clone the expression before operating on it.  It should be an
# error to hit _clone_if_needed() with fewer than
# UNREFERENCED_EXPR_COUNT references.
generate_intrinsic_function_expression.UNREFERENCED_EXPR_COUNT = 7


def log(*args):
    return generate_intrinsic_function_expression(args, 1, 'log', math.log)

def log10(*args):
    return generate_intrinsic_function_expression(args, 1, 'log10', math.log10)

def sin(*args):
    return generate_intrinsic_function_expression(args, 1, 'sin', math.sin)

def cos(*args):
    return generate_intrinsic_function_expression(args, 1, 'cos', math.cos)

def tan(*args):
    return generate_intrinsic_function_expression(args, 1, 'tan', math.tan)

def sinh(*args):
    return generate_intrinsic_function_expression(args, 1, 'sinh', math.sinh)

def cosh(*args):
    return generate_intrinsic_function_expression(args, 1, 'cosh', math.cosh)

def tanh(*args):
    return generate_intrinsic_function_expression(args, 1, 'tanh', math.tanh)

def asin(*args):
    return generate_intrinsic_function_expression(args, 1, 'asin', math.asin)

def acos(*args):
    return generate_intrinsic_function_expression(args, 1, 'acos', math.acos)

def atan(*args):
    return generate_intrinsic_function_expression(args, 1, 'atan', math.atan)

def exp(*args):
    return generate_intrinsic_function_expression(args, 1, 'exp', math.exp)

def sqrt(*args):
    return generate_intrinsic_function_expression(args, 1, 'sqrt', math.sqrt)

def asinh(*args):
    return generate_intrinsic_function_expression(args, 1, 'asinh', math.asinh)

def acosh(*args):
    return generate_intrinsic_function_expression(args, 1, 'acosh', math.acosh)

def atanh(*args):
    return generate_intrinsic_function_expression(args, 1, 'atanh', math.atanh)

def ceil(*args):
    return generate_intrinsic_function_expression(args, 1, 'ceil', math.ceil)

def floor(*args):
    return generate_intrinsic_function_expression(args, 1, 'floor', math.floor)
