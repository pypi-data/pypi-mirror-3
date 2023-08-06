#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2010 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the FAST README.txt file.
#  _________________________________________________________________________

__all__ = ['linearize_model_expressions', 'is_linear_expression_constant']

# a prototype utility to translate from a "normal" model instance containing
# constraints and objectives with expresssions for their bodies, into a
# more compact linearized verson of the problem. eliminates the need for
# canonical expressions and the associated overhead (memory and speed).

# NOTE: Currently only works for constraints - leaving the expressions alone,
#       mainly because PH doesn't modify those and I don't want to deal with
#       that aspect for the moment. In particular, this only works for
#       immutable parameters due to the reliance on the canonical expression
#       generator to extract the linear and constant terms.

from coopr.pyomo import *
from coopr.pyomo.expr import generate_canonical_repn, canonical_is_linear, canonical_is_constant

def linearize_model_expressions(instance):
    var_id_map = {}

    # TBD: Should we really be doing this for all components, and not just active ones?
    for constraint_name, constraint in instance.active_components()[Constraint].iteritems():

        for index, constraint_data in constraint._data.iteritems():

            if constraint_data.repn != None:
                canonical_encoding = constraint_data.repn
            else:
                canonical_encoding = generate_canonical_repn(constraint_data.body, var_id_map)

            variable_map = canonical_encoding[-1]

            # we obviously can't linearize an expression if it has higher-order terms!
            if canonical_is_linear(canonical_encoding) or canonical_is_constant(canonical_encoding):

                constant_term = 0.0
                linear_terms = [] # a list of coefficient, _VarData pairs.

                if canonical_encoding.has_key(0):
                    constant_term = canonical_encoding[0][None]

                for var_hash, var_coefficient in canonical_encoding[1].iteritems():
                    var_value = variable_map[var_hash]
                    linear_terms.append((var_coefficient, var_value))

                # eliminate the expression tree - we don't need it any longer.
                # ditto the canonical representation.
                constraint_data.body = None
                constraint_data.lin_body = [constant_term, linear_terms]
                if constraint_data.repn is not None:
                    constraint_data.repn = None

def is_linear_expression_constant(lin_body):
    """Return True if the linear expression is a constant expression, due either to a lack of variables or fixed variables"""
    return (len(lin_body[1]) == 0)
