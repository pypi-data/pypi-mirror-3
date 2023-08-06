#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________

import pyutilib.component.core
from coopr.pyomo.base import IModelTransformation
from coopr.pyomo.base import Var
from coopr.pyomo import BooleanSet, IntegerSet, RangeSet, Reals


class RelaxIntegrality(pyutilib.component.core.SingletonPlugin):
    """
    This plugin relaxes integrality in a Pyomo model.
    """

    pyutilib.component.core.implements(IModelTransformation)

    def __init__(self, **kwds):
        kwds['name'] = "relax_integrality"
        pyutilib.component.core.Plugin.__init__(self, **kwds)

    def apply(self, model, **kwds):
        #
        # Clone the model
        #
        M = model.clone()
        #
        # Iterate over all variables, replacing the domain with a real-valued domain
        # and setting appropriate bounds.
        #
        # Note: this technique is not extensible.  If a user creates a new integer variable
        # class then we'd need to add it here (unless it was a subset of one of the sets we
        # detect here.  Alternatively, we could make the variables responsible for managing
        # the generation of a relaxed variable.  But that would pollute the variable objects
        # with logic about generating a specific relaxation.  That's probably a worse alternative.
        #
        comp = M.components[Var]
        for var in comp.values():
            if isinstance(var.domain, BooleanSet):
                var.domain=Reals
                var._bounds = (0.0,1.0)
            elif isinstance(var.domain, IntegerSet):
                var.domain=Reals
                var._bounds = var.domain._bounds
            elif isinstance(var.domain, RangeSet):
                var.domain=Reals
                var._bounds = var.domain._bounds
        M.statistics.number_of_continuous_variables += \
            M.statistics.number_of_binary_variables + \
            M.statistics.number_of_integer_variables
        M.statistics.number_of_binary_variables = 0
        M.statistics.number_of_integer_variables = 0
        return M
