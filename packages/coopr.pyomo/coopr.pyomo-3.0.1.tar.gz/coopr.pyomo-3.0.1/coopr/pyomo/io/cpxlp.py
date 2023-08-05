
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
# Problem Writer for CPLEX LP Format Files
#

import itertools
import math
import weakref

from coopr.opt import ProblemFormat
from coopr.opt.base import AbstractProblemWriter, SymbolMap
from coopr.pyomo.base import BooleanSet, Constraint, ConstraintList, expr, IntegerSet
from coopr.pyomo.base.constraint import Objective, NumericConstant, SOSConstraint, Var, ConstraintData
from coopr.pyomo.base import VarStatus, value, label_from_name
from coopr.pyomo.base.numtypes import minimize, maximize
from coopr.pyomo.expr import is_constant, is_nonlinear, is_quadratic

from pyutilib.component.core import alias
from pyutilib.misc import deprecated, tostr

class CPXLP_numeric_labeler(object):
    def __init__(self, prefix):
        self.id = 0
        self.prefix = prefix
    def __call__(self, obj):
        self.id += 1
        return self.prefix + str(self.id)

class CPXLP_text_labeler(object):
    def __call__(self, obj):
        label = str(obj.name)

        try:
            block = obj.component
        except:
            block = None

        if block is None:
            return label_from_name(label)
        block = block().parent
        if block is None:
            return label_from_name(label)

        block = block()
        while block.parent is not None and block.parent() is not None:
            label = block.name + "." + label
            block = block.parent()
        return label_from_name(label)

class CPXLP_prefix_labeler(object):
    def __init__(self, prefix):
        self.prefix = prefix
        
    def __call__(self, obj):
        label = str(obj.name)

        # We *really* need to move to a unified "parent" notion...
        try:
            block = obj.component
        except:
            block = None

        if block is None:
            return label_from_name(prefix+label)
        block = block().parent
        if block is None:
            return label_from_name(prefix+label)

        block = block()
        while block is not None:
            label = block.name + "." + label
            block = block.parent()
        return label_from_name(prefix+label)

class ProblemWriter_cpxlp(AbstractProblemWriter):

    alias('cpxlp')
    alias('lp')

    def __init__(self):

        AbstractProblemWriter.__init__(self,ProblemFormat.cpxlp)

        # temporarily placing attributes used in extensive-form writing
        # here, for eventual migration to the base class.
        self._output_objectives = True
        self._output_constraints = True
        self._output_variables = True
            # means we're outputting *some* variables - types determined by
            # following flags.

        # building on the above, partition out the variables that should
        # be written if the _output_variables attribute is set to True.
        # this is useful when writing components of multiple models to a
        # single LP file. unfortunately, the CPLEX LP format requires all
        # integer and binary (and continuous) variables to appear in a
        # single continuous block.
        #
        # SOS constraints must come after Bounds, General, Binary, and
        # Semi-Continuous sections
        #
        self._output_continuous_variables = True
        self._output_integer_variables = True
        self._output_binary_variables = True

        # do I pre-pend the model name to all identifiers I output?
        # useful in cases where you are writing components of multiple
        # models to a single output LP file.
        self._output_prefixes = False


    def __call__(self, model, filename, solver_capability):
        if filename is None:
            filename = model.name + ".lp"
        OUTPUT=open(filename,"w")
        symbol_map = self._print_model_LP(model,OUTPUT, solver_capability)
        OUTPUT.close()
        return filename, symbol_map


    def _get_bound(self, exp):

        if isinstance(exp,expr._IdentityExpression):
            return self._get_bound(exp._args[0])
        elif exp.is_constant():
            return exp()
        else:
            raise ValueError, "ERROR: nonconstant bound: " + str(exp)
            return None

    @staticmethod
    def _collect_key ( a ):

        return a[0]


    @staticmethod
    def _no_label_error ( var ):

        msg  = "Unable to find label for variable '%s'.\n"                    \
        'Possibly uninstantiated model.  Do any constraint or objective  '     \
        'rules reference the original model object, as opposed to the  '     \
        'passed model object? Alternatively, if you are developing code, '     \
        'has the model instance been pre-processed?'

        raise ValueError, msg % str(var)


    def _print_expr_linear(self, x, OUTPUT, symbol_map, labeler, is_objective):

        """
        Return a expression as a string in LP format.

        Note that this function does not handle any differences in LP format
        interpretation by the solvers (e.g. CPlex vs GLPK).  That decision is
        left up to the caller.

        required arguments:
          x: A Pyomo linear encoding of an expression to write in LP format

        optional keyword arguments:
          is_objective: set True if printing a quadratic objective.  Required
             for CPlex LP quadratic handling differences between objectives
             and constraints. (boolean)

          print_offset: print expression offset [deprecated] (boolean)
        """

        #is_objective = kwargs.pop('is_objective', False)
        #print_offset = kwargs.pop('print_offset', False)

        # Currently, it appears that we only need to print the constant
        # offset term for objectives.
        print_offset = is_objective

        constant_term = x[0]
        linear_terms = x[1]

        name_to_coefficient_map = {}

        for coefficient, var_value in linear_terms:

            if var_value.fixed is True:

                constant_term += (coefficient * var_value.value)

            else:
                name = symbol_map.getSymbol( var_value, labeler )

                # due to potential disabling of expression simplification,
                # variables might appear more than once - condense coefficients.
                name_to_coefficient_map[name] = coefficient + name_to_coefficient_map.get(name,0.0)

        sorted_names = sorted(name_to_coefficient_map.keys())

        for name in sorted_names:

            coefficient = name_to_coefficient_map[name]

            sign = '+'
            if coefficient < 0: sign = '-'
            #print >>OUTPUT, '%s%s %s' % (sign, repr(math.fabs(coefficient)), name)      #REPR_TAG
            print >>OUTPUT, '%s%f %s' % (sign, math.fabs(coefficient), name)

        if print_offset and (constant_term != 0.0):
            sign = '+'
            if constant_term < 0: sign = '-'
            #print >>OUTPUT, '%s%s %s' % (sign, repr(math.fabs(constant_term)), 'ONE_VAR_CONSTANT')    #REPR_TAG
            print >>OUTPUT, '%s%f %s' % (sign, math.fabs(constant_term), 'ONE_VAR_CONSTANT')

        return constant_term


    def _print_expr_canonical(self, x, OUTPUT, symbol_map, labeler, is_objective):

        """
        Return a expression as a string in LP format.

        Note that this function does not handle any differences in LP format
        interpretation by the solvers (e.g. CPlex vs GLPK).  That decision is
        left up to the caller.

        required arguments:
          x: A Pyomo canonical expression to write in LP format

        optional keyword arguments:
          is_objective: set True if printing a quadratic objective.  Required
             for CPlex LP quadratic handling differences between objectives
             and constraints. (boolean)

          print_offset: print expression offset [deprecated] (boolean)
        """

        #is_objective = kwargs.pop('is_objective', False)
        #print_offset = kwargs.pop('print_offset', False)

        # Currently, it appears that we only need to print the constant
        # offset term for objectives.
        print_offset = is_objective

        #
        # Linear
        #
        if 1 in x:
            sorted_names = []
            for var_hash, var_coefficient in x[1].iteritems():
                var_value = x[-1][var_hash]
                name = symbol_map.getSymbol( var_value, labeler )
                sorted_names.append((name,var_coefficient))

            sorted_names.sort()

            for name, coef in sorted_names:
                # there are various situations in which the coefficients may be equal to 0.0,
                # in which case there is no real reason to output the corresponding terms.
                if coef: # != 0.0: 
                    #print >>OUTPUT, '%s%s %s' % (sign, repr(math.fabs(coef)), name) #REPR_TAG
                    #print >>OUTPUT, '%s%f %s' % (coef < 0 and '-' or '+', math.fabs(coef), name)
                    print >>OUTPUT, '%+f' % coef, name

        #
        # Quadratic
        #
        if 2 in x:

            print >>OUTPUT, "+ ["

            num_output = 0

            for id in sorted(x[2].keys()):

                coefficient = x[2][id]
                sign = '+'
                if coefficient < 0:
                    sign = '-'
                    coefficient = math.fabs(coefficient)

                if is_objective:
                    coefficient *= 2
                # times 2 because LP format requires /2 for all the quadratic
                # terms /of the objective only/.  Discovered the last bit thru
                # trial and error.  Obnoxious.
                # Ref: ILog CPlex 8.0 User's Manual, p197.

                #print >>OUTPUT, sign, repr(coefficient)   #REPR_TAG
                print >>OUTPUT, sign, coefficient,

                term_variables = []

                for var in id:
                    var_value = x[-1][var]
                    name = symbol_map.getSymbol( var_value, labeler )
                    term_variables.append(name)

                if len(term_variables) == 2:
                    print >>OUTPUT, term_variables[0],"*",term_variables[1],
                else:
                    print >>OUTPUT, term_variables[0],"^ 2",
                print >>OUTPUT, ""

            print >>OUTPUT, ""

            print >>OUTPUT, "]",
            if is_objective:
                print >>OUTPUT, ' / 2'
                # divide by 2 because LP format requires /2 for all the quadratic
                # terms.  Weird.  Ref: ILog CPlex 8.0 User's Manual, p197
            else:
                print >>OUTPUT, ""


        #
        # Constant offset
        #
        if 0 in x:
            offset = x[0][None]
        else:
            offset=0.0
        if print_offset and offset != 0.0:
            #print >>OUTPUT, '%s%s %s' % (sign, repr(math.fabs(offset)), 'ONE_VAR_CONSTANT') #REPR_TAG
            print >>OUTPUT, '%s%f %s' % (offset < 0 and '-' or '+', math.fabs(offset), 'ONE_VAR_CONSTANT')

        #
        # Return constant offset
        #
        return offset

    @staticmethod
    def printSOS(con, name, OUTPUT, index=None):

        """
        Returns the SOS constraint (as a string) associated with con.
        If specified, index is passed to con.sos_set().

        Arguments:
        con    The SOS constraint object
        name   The name of the variable
        OUTPUT The output stream
        index  [Optional] the index to pass to the sets indexing the variables.
        """

        # The name of the variable being indexed
        varName = str(con.sos_vars())

        # The list of variable names to be printed, including indices
        varNames = []

        # Get all the variables
        if index is None:
            tmpSet = con.sos_set()
        else:
            tmpSet = con.sos_set()[index]
        for x in tmpSet:
            strX = str(x)
            if strX[0] == "(":
                # its a tuple, remove whitespace
                # handle stringed indices by replacing strings ' with _
                varNames.append(varName + strX.replace(" ","").replace('\'','_'))
            else:
                # its a single number, add parenthesis
                # handle stringed indices by replacing strings ' with _
                varNames.append(varName + "(" + strX.replace('\'','_') + ")")

        conNameIndex = ""
        if index is not None:
            if type(index) is tuple:
                conNameIndex = tostr(index).replace(' ','').replace('\t','_')
            else:
                conNameIndex = str(index).replace('\t','_')

        print >>OUTPUT, '%s_%s: S%s::' % (name, conNameIndex, con.sos_level())

        # We need to 'weight' each variable
        # For now we just increment a counter
        for i in range(0, len(varNames)):
            print >>OUTPUT, '%s:%f' % (varNames[i], i+1)

    def _print_model_LP(self, model, OUTPUT, solver_capability):

        symbol_map = SymbolMap(model)
        if self._output_prefixes:
            labeler = CPXLP_prefix_labeler(model.name + "_")
        else:
            labeler = CPXLP_text_labeler()
        #labeler = CPXLP_numeric_labeler('x')
        _obj = model.active_components(Objective)

        supports_quadratic = solver_capability('quadratic')

        #
        # Objective
        #
        if self._output_objectives is True:

            if len(_obj) == 0:
                msg = "ERROR: No objectives defined for input model '%s'; "    \
                      ' cannot write legal LP file'
                raise ValueError, msg % str( model.name )
            if len(_obj) > 1:
                msg = "More than one objective defined for input model '%s'; " \
                      'Cannot write legal LP file\n'                           \
                      'Objectives: %s'
                raise ValueError(
                    msg % ( model.name,','.join("'"+str(x.name)+"'" for x in _obj) ))

            obj = _obj[ _obj.keys()[0] ]
            if obj.sense == maximize:
                print >>OUTPUT, "max "
            else:
                print >>OUTPUT, "min "

            obj_keys = obj.keys()
            if len(obj_keys) > 1:
                keys = obj.name + ' (indexed by: %s)' % ', '.join(map(str, obj_keys))

                msg = "More than one objective defined for input model '%s'; " \
                      'Cannot write legal LP file\n'                           \
                      'Objectives: %s'
                raise ValueError, msg % ( str(model.name), keys )

            obj_data = obj[obj_keys[0]]

            if obj_data.repn is None:
                raise RuntimeError, "No canonical representation identified for objective="+obj_data.name
            if None in obj_data.repn:
                degree = None
            else:
                degree = max(obj_data.repn.iterkeys())

            if degree == 0:
                print ("Warning: Constant objective detected, replacing " +
                       "with a placeholder to prevent solver failure.")

                print >>OUTPUT, symbol_map.getSymbol( obj_data, labeler ) \
                      + ": +0.0 ONE_VAR_CONSTANT"
                symbol_map.alias(obj_data, '__default_objective__')

                # Skip the remaining logic of the section
            else:
                if degree == 2:

                    if not supports_quadratic:
                        raise RuntimeError(
                            'Selected solver is unable to handle objective functions with quadratic terms. ' \
                            'Objective at issue: %s.' % obj.name)
                        
                elif degree != 1:
                    msg  = "Cannot write legal LP file.  Objective '%s%s' "  \
                           'has nonlinear terms that are not quadratic.'
                    if key is None: msg %= (obj.name, '')
                    else:           msg %= (obj.name, '[%s]' % key )
                    raise RuntimeError, msg

                print >>OUTPUT, symbol_map.getSymbol( obj_data, labeler )+':'
                symbol_map.alias(obj_data, '__default_objective__')

                offset = self._print_expr_canonical( obj_data.repn,
                                                     OUTPUT,
                                                     symbol_map, labeler,
                                                     True )

                print >>OUTPUT, ""

        # Constraints
        #
        # If there are no non-trivial constraints, you'll end up with an empty
        # constraint block. CPLEX is OK with this, but GLPK isn't. And
        # eliminating the constraint block (i.e., the "s.t." line) causes GLPK
        # to whine elsewhere. output a warning if the constraint block is empty,
        # so users can quickly determine the cause of the solve failure.

        if self._output_constraints is True:

            # for now, if this routine isn't writing everything, then assume a
            # meta-level handler is dealing with the writing of the transitional
            # elements - these should probably be done in the form of
            # "end_objective()" and "end_constraint()" helper methods.
            #
            if self._output_objectives == self._output_variables == True:
                print >>OUTPUT, "s.t."
                print >>OUTPUT, ""

            have_nontrivial = False

            # FIXME: This is a hack to get nested blocks working...
            for block in model.all_blocks():
                active_constraints = block.active_components(Constraint)
                active_constraintlists = block.active_components(ConstraintList)
                for constraint in itertools.chain(active_constraints.itervalues(), active_constraintlists.itervalues()):
                    if constraint.trivial:
                        continue

                    have_nontrivial=True

                    for index in sorted(constraint.keys()):

                        constraint_data = constraint[index]
                        if not constraint_data.active:
                            continue

                        # if expression trees have been linearized, then the canonical
                        # representation attribute on the constraint data object will
                        # be equal to None.
                        if (constraint_data.repn is not None):
                            
                            if None in constraint_data.repn:
                                degree = None
                            else:
                                degree = max(constraint_data.repn.iterkeys())
                                
                            # There are conditions, e.g., when fixing variables, under which
                            # a constraint block might be empty.  Ignore these, for both
                            # practical reasons and the fact that the CPLEX LP format
                            # requires a variable in the constraint body.  It is also
                            # possible that the body of the constraint consists of only a
                            # constant, in which case the "variable" of
                            if degree == 0:
                                # this happens *all* the time in many applications,
                                # including PH - so suppress the warning.
                                #
                                #msg = 'WARNING: ignoring constraint %s[%s] which is ' \
                                #      'constant'
                                #print msg % (str(C),str(index))
                                continue

                            if degree == 2:
                                if not supports_quadratic:
                                    msg  = 'Solver unable to handle quadratic expressions.'\
                                           "  Constraint at issue: '%s%%s'"
                                    msg %= constraint.name
                                    if index is None: msg %= ''
                                    else: msg %= '[%s]' % index
                                    
                                    raise ValueError, msg

                            elif degree != 1:
                                msg = "Cannot write legal LP file.  Constraint '%s%s' "   \
                                      'has a body with nonlinear terms.'
                                if index is None:
                                    msg %= ( constraint.name, '')
                                else:
                                    msg %= ( constraint.name, '[%s]' % index )
                                raise ValueError, msg

                        con_symbol = symbol_map.getSymbol( constraint_data, labeler )
                        if constraint_data._equality:
                            label = 'c_e_' + con_symbol + '_'
                            symbol_map.alias(constraint_data, label)
                            print >>OUTPUT, label+':'
                            if constraint_data.lin_body is not None:
                                offset = self._print_expr_linear(constraint_data.lin_body, OUTPUT, symbol_map, labeler, False)
                            else:
                                offset = self._print_expr_canonical(constraint_data.repn, OUTPUT, symbol_map, labeler, False)
                            bound = constraint_data.lower
                            bound = str(self._get_bound(bound) - offset)
                            print >>OUTPUT, "=", bound
                            print >>OUTPUT, ""
                        else:
                            # TBD: ENCAPSULATE THE IF-ELSE INTO A SINGLE UTILITY METHOD
                            # TBD: MAKE THE _data and C[ndx] calls consistent - everything should just reference the data directly
                            if constraint_data.lower is not None:
                                label = 'c_l_' + con_symbol + '_'
                                symbol_map.alias(constraint_data, label)
                                print >>OUTPUT, label+':'
                                if constraint_data.lin_body is not None:
                                    offset = self._print_expr_linear(constraint_data.lin_body, OUTPUT, symbol_map, labeler, False)
                                else:
                                    offset = self._print_expr_canonical(constraint_data.repn, OUTPUT, symbol_map, labeler, False)
                                bound = constraint_data.lower
                                bound = str(self._get_bound(bound) - offset)
                                print >>OUTPUT, ">=", bound
                                print >>OUTPUT, ""
                            if constraint_data.upper is not None:
                                label = 'c_u_' + con_symbol + '_'
                                symbol_map.alias(constraint_data, label)
                                print >>OUTPUT, label+':'
                                if constraint_data.lin_body is not None:
                                    offset = self._print_expr_linear(constraint_data.lin_body, OUTPUT, symbol_map, labeler, False)
                                else:
                                    offset = self._print_expr_canonical(constraint_data.repn, OUTPUT, symbol_map, labeler, False)
                                bound = constraint_data.upper
                                bound = str(self._get_bound(bound) - offset)
                                print >>OUTPUT, "<=", bound
                                print >>OUTPUT, ""

            if not have_nontrivial:
                print 'WARNING: Empty constraint block written in LP format '  \
                      '- solver may error'

            # the CPLEX LP format doesn't allow constants in the objective (or
            # constraint body), which is a bit silly.  To avoid painful
            # book-keeping, we introduce the following "variable", constrained
            # to the value 1.  This is used when quadratic terms are present.
            # worst-case, if not used, is that CPLEX easily pre-processes it out.
            prefix = ""
            if self._output_prefixes is True:
                prefix = model.name + "_"
            print >>OUTPUT, '%sc_e_ONE_VAR_CONSTANT: ' % prefix
            print >>OUTPUT, '%sONE_VAR_CONSTANT = 1.0' % prefix
            print >>OUTPUT, ""

        #
        # Bounds
        #

        if self._output_variables is True:

            # For now, if this routine isn't writing everything, then assume a
            # meta-level handler is dealing with the writing of the transitional
            # elements - these should probably be done in the form of
            # "end_objective()" and "end_constraint()" helper methods.
            if True == self._output_objectives == self._output_constraints:
                print >>OUTPUT, "bounds "

            # Scan all variables even if we're only writing a subset of them.
            # required because we don't store maps by variable type currently.

            # Track the number of integer and binary variables, so you can
            # output their status later.
            niv = nbv = 0

            # FIXME: This is a hack to get nested blocks working...
            for block in model.all_blocks():
                active_variables = block.active_components(Var)

                for variable_name in sorted(active_variables.keys()):

                    var = active_variables[variable_name]

                    for index, var_value in var.iteritems():
                        if isinstance(var_value.domain, IntegerSet):   niv += 1
                        elif isinstance(var_value.domain, BooleanSet): nbv += 1

                    if self._output_continuous_variables is True:

                        for index in sorted(var._varval.keys()):

                            this_varval = var[index]

                            if (not this_varval.active) or (this_varval.status is not VarStatus.used):
                                continue

                            # if the variable isn't referenced in the model, don't
                            # output bounds...
                            if this_varval.id != -1:
                                # in the CPLEX LP file format, the default variable
                                # bounds are 0 and +inf.  These bounds are in
                                # conflict with Pyomo, which assumes -inf and +inf
                                # (which we would argue is more rational).
                                print >>OUTPUT,"   ",
                                if this_varval.lb is not None:
                                    #print >>OUTPUT, repr(value(this_varval.lb())), "<= ",   #REPR_TAG
                                    print >>OUTPUT, str(value(this_varval.lb())), "<= ",
                                else:
                                    print >>OUTPUT, " -inf <= ",
                                name_to_output = symbol_map.getSymbol( this_varval, labeler )
                                if name_to_output == "e":
                                    msg = 'Attempting to write variable with name' \
                                          "'e' in a CPLEX LP formatted file - "    \
                                          'will cause a parse failure due to '     \
                                          'confusion with numeric values '         \
                                          'expressed in scientific notation'
                                    raise ValueError, msg
                                print >>OUTPUT, name_to_output,
                                if this_varval.ub is not None:
                                    #print >>OUTPUT, " <=", repr(value(this_varval.ub()))       #REPR_TAG
                                    print >>OUTPUT, " <=", str(value(this_varval.ub()))
                                else:
                                    print >>OUTPUT, " <= +inf"

            if (niv > 0) and (self._output_integer_variables is True):

                # If we're outputting the whole model, then assume we can output
                # the "general" header. If not, then assume a meta-level process
                # is taking care of it.
                if True == self._output_objectives == self._output_constraints:
                    print >>OUTPUT, "general"

                for block in model.all_blocks():

                    active_variables = block.active_components(Var)

                    for variable_name in sorted(active_variables.keys()):

                        var = active_variables[variable_name]

                        for index in sorted(var.integer_keys()):

                            this_varvalue = var[index]

                            if (not this_varvalue.active) or (this_varvalue.status is not VarStatus.used):
                                continue
                            if this_varvalue.id != -1: # skip if variable not referenced
                                var_name = symbol_map.getSymbol( this_varvalue, labeler )
                                print >>OUTPUT, ' ', var_name

            if (nbv > 0) and (self._output_binary_variables is True):

                # If we're outputting the whole model, then assume we can output
                # the "binary" header. if not, then assume a meta-level process
                # is taking care of it.
                if True == self._output_objectives == self._output_constraints:
                    print >>OUTPUT, "binary"

                #prefix = ""
                #if self._output_prefixes is True:
                #    prefix = convert_name(var.model().name)+"_"

                for block in model.all_blocks():

                    active_variables = block.active_components(Var)

                    for variable_name in sorted(active_variables.keys()):

                        var = active_variables[variable_name]

                        for index in sorted(var.binary_keys()):

                            this_varvalue = var[index]

                            if (not this_varvalue.active) or (this_varvalue.status is not VarStatus.used):
                                continue
                            if this_varvalue.id != -1: # skip if variable not referenced
                                var_name = symbol_map.getSymbol( this_varvalue, labeler )
                                print >>OUTPUT, ' ', var_name


        # SOS constraints
        #
        # For now, we write out SOS1 and SOS2 constraints in the cplex format
        #
        # All Component objects are stored in model._component, which is a
        # dictionary of {class: {objName: object}}.
        #
        # Consider the variable X,
        #
        #   model.X = Var(...)
        #
        # We print X to CPLEX format as X(i,j,k,...) where i, j, k, ... are the
        # indices of X.
        #
        # TODO: Allow users to specify the variables coefficients for custom
        # branching/set orders - also update ampl.py, CPLEXDirect.py, gurobi_direct.py
        sosn = solver_capability("sosn")
        sos1 = solver_capability("sos1")
        sos2 = solver_capability("sos2")
        writtenSOS = False
        for block in model.all_blocks():
            sos_con_list = block.active_components(SOSConstraint)
        
            if len(sos_con_list) > 0:
                if not(sos1 or sos2 or sosn):
                    raise Exception(
                        "Solver does not support SOSConstraint declarations")

            for con in sos_con_list.itervalues():
                level = con.sos_level()
                if (level == 1 and not sos1) or (level == 2 and not sos2) or \
                        (level > 2 and not sosn):
                    raise Exception(
                        "Solver does not support SOS level %s constraints" 
                        % (level,) )
                if writtenSOS == False:
                    print >>OUTPUT, "SOS"
                    writtenSOS = True
                name = symbol_map.getSymbol( con, labeler ) 
                masterIndex = con.sos_set_set()
                if None in masterIndex:
                    # A single constraint
                    self.printSOS(con, name, OUTPUT)
                else:
                    # A series of indexed constraints
                    for index in masterIndex:
                        self.printSOS(con, name, OUTPUT, index)
                    

        #
        # wrap-up
        #
        if self._output_objectives == self._output_constraints == True:
            #
            # End
            #
            print >>OUTPUT, "end "
        #
        return symbol_map
