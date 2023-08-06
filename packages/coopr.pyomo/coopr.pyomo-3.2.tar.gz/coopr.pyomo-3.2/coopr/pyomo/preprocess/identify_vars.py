#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the FAST README.txt file.
#  _________________________________________________________________________


import pyutilib.component.core
from coopr.pyomo.base import expr, Constraint, Objective, SOSConstraint
from coopr.pyomo.base.connector import _ConnectorBase, _ConnectorValue
from coopr.pyomo.base.numvalue import NumericConstant
from coopr.pyomo.base.var import  _VarData, VarStatus, _VarArray, _VarBase, Var, VarList
from coopr.pyomo.base import IPyomoPresolver, IPyomoPresolveAction
import logging


class IdentifyVariablesPresolver(pyutilib.component.core.SingletonPlugin):
    """
    This plugin processes a Pyomo Model instance to define
    the order of variables and to categorize constraints.
    """

    pyutilib.component.core.implements(IPyomoPresolveAction)

    def __init__(self, **kwds):
        kwds['name'] = "identify_variables"
        pyutilib.component.core.Plugin.__init__(self, **kwds)

    def rank(self):
        return 1

    #
    # Scan through a linearly encoded expression body to identify variables.
    #
    def _identify_variables_in_linear_encoding(self, encoding):

        # recall that "encoding" is a tuple: element 0 is the constant, element 1 is a list of (coefficient, _VarData) pairs.
        for coefficient, var in encoding[1]:

            if var.fixed: # we know this is a _VarData, by construction - do the direct query to save time.
                continue
            else:
                var.status = VarStatus.used

    #
    # Recursively work through an expression (tree) to identify variables.
    #
    def _identify_variables_in_expression(self, exp):

        try:
            # It is possible (likely) that the expression is not
            # completely valid.  Check if that is the case, and return a
            # useful message to the user.
            is_expr = exp.is_expression()
        except AttributeError, e:
            # Likely caused by a constraint or an objective failing
            # to return a value.
            if isinstance(exp, _VarArray):
                msg = "Have you properly indexed '%s'?" % str(exp)
            else:
                msg = "Do all constraints and objectives return a value?"
            logging.getLogger('coopr.pyomo').error(
                "identifying variables in expression failed: %s\n%s\ntype=%s",
                str(e), msg, str(type(exp)) )
            raise

        #
        # Expression
        #
        if is_expr:
            #
            # Product Expressions store stuff differently
            #

            # NOTE: Avoid the considerable cost of recursion if we can avoid it.
            if exp.__class__ is expr._ProductExpression:
                for arg in exp._numerator:
                    if arg.is_constant():
                        pass
                    elif isinstance(arg,_VarData):
                        arg.status = VarStatus.used
                    else:
                        self._identify_variables_in_expression(arg)
                for arg in exp._denominator:
                    if arg.is_constant():
                        pass
                    else:
                       self._identify_variables_in_expression(arg)
            else:
                for arg in exp._args:
                    if arg.is_constant():
                        pass
                    elif isinstance(arg,_VarData):
                        arg.status = VarStatus.used
                    else:
                        self._identify_variables_in_expression(arg)
        #
        # Fixed Values (params, constants, fixed variables)
        #
        elif exp.is_constant():
            pass
        #
        # Variable Value
        #
        elif isinstance(exp,_VarData):
            exp.status = VarStatus.used

        #
        # Connector Value
        #
        elif isinstance(exp, _ConnectorValue):
            for var in exp.vars.itervalues():
                # FIXME: HACK: this is needed because preprocess is
                # called before the instance transformation plugins --
                # so for connectors attached to VarLists, the connector
                # is still pointing to an empty var list.  When
                # preprocess is called again after the transofrmation,
                # the expanded constraints will reference individual
                # _VarData.
                if type(var) is not VarList:
                    self._identify_variables_in_expression(var)
        #
        # Variable Base
        #
        elif isinstance(exp,_VarBase):
            # FIXME: [JDS] I am pretty sure that the only way to get here
            # will always raise the ValueError exception; the rest of
            # this logic is superfluous
            tmp = exp.as_numeric()
            if tmp is exp:
                raise ValueError("Variable %s appears in an expression without "
                                 "an index, but this variable is an indexed "
                                 "value." % ( exp.name, ))
            exp.status = VarStatus.used

        #
        # Connector Base
        #
        elif isinstance(exp,_ConnectorBase):
            raise ValueError("Connector %s appears in an expression without "
                             "an index, but this variable is an indexed "
                             "value." % exp.name)
        #
        # If not a constant, then this is an error
        #
        else:
            raise ValueError, "Unexpected expression type in identify_variables: " + str(type(exp))+" "+str(exp)

    def _preprocess_block(self, block):
        active_variables = block.active_components(Var)
        active_constraints = block.active_components(Constraint)
        active_objectives = block.active_components(Objective)

        active_constraints.update(block.active_components(SOSConstraint))

        #
        # Call the appropriate identify_variables to find the variables that
        # are actively used in the objective and constraints.
        #
        for name, objective in active_objectives.iteritems():
            for index, objective_data in objective._data.iteritems():
                if not objective_data.active:
                    continue
                try:
                    self._identify_variables_in_expression(objective_data.expr)
                except ValueError, err:
                    logging.getLogger('coopr.pyomo').error(
                        "Problem processing objective %s (index %s): %s" %
                        (str(name), str(index), str(err)) )
                    raise

                objective_data.id = self.objective_count
                self.objective_count += 1

        for name, constraint in active_constraints.iteritems():
            for index, constraint_data in constraint._data.iteritems():
                if not constraint_data.active:
                    continue
                try:
                    if constraint_data.lin_body is not None:
                        self._identify_variables_in_linear_encoding(constraint_data.lin_body)
                    else:
                        self._identify_variables_in_expression(constraint_data.body)
                except ValueError, err:
                    logging.getLogger('coopr.pyomo').error(
                        "Problem processing constraint %s (index %s):\n%s" %
                        ( str(name), str(index), str(err) ) )
                    raise
                self.constraint_count += 1

        #
        # count the number of variables in each type category.  we don't
        # do this within the _identify_variables_in_expression function
        # because the variable type is owned by the "parent" variable,
        # and the interrogation cost for variable type is comparatively
        # expensive - we don't want to do it for each variable value.
        #
        for var in active_variables.itervalues():
            self.num_binary_var += len(var.binary_keys())
            self.num_integer_var += len(var.integer_keys())
            self.num_real_var += len(var.continuous_keys())

    #
    # this pre-processor computes a number of attributes of model
    # components, in addition to models themselves. for _VarData,
    # _ConstraintData, and _ObjectiveData, the routine assigns the "id"
    # attribute. in addition, for _VarData, the routine sets the
    # "status" attribute - to used or unused, depending on whether it
    # appears in an active constraint/objective. on the Model object,
    # the routine populates the "statistics" (variable / constraint /
    # objective counts) attribute, and builds the _var, _con, and _obj
    # dictionaries of a Model, which map the id attributes to the
    # respective _VarData, _ConstraintData, or _ObjectiveData object.
    #
    # NOTE: if variables are fixed, then this preprocessor will flag
    #       them as unused and consequently not create entries for them
    #       in the model _var map.
    #
    def preprocess(self,model):
        """
        The main routine to perform the preprocess
        """
        self.var_count=0
        self.constraint_count=0
        self.objective_count=0
        self.num_binary_var = 0
        self.num_integer_var = 0
        self.num_real_var = 0

        model.statistics.number_of_binary_variables = 0
        model.statistics.number_of_integer_variables = 0
        model.statistics.number_of_continuous_variables = 0

        all_blocks = model.all_blocks()

        #
        # Until proven otherwise, all variables are unused.
        #
        for block in all_blocks:
            for var in block.active_components(Var).itervalues():
                for var_value in var._varval.itervalues():
                    var_value.status = VarStatus.unused

        for block in all_blocks:
            self._preprocess_block(block)

        #
        # assign the model statistics
        #

        model.statistics.number_of_variables = self.var_count
        model.statistics.number_of_constraints = self.constraint_count
        model.statistics.number_of_objectives = self.objective_count
        model.statistics.number_of_binary_variables = self.num_binary_var
        model.statistics.number_of_integer_variables = self.num_integer_var
        model.statistics.number_of_continuous_variables = self.num_real_var
        return model
