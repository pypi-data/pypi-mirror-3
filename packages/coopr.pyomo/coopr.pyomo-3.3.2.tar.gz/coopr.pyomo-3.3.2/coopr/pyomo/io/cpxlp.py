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
from coopr.pyomo.base import BooleanSet, Constraint, ConstraintList, expr, IntegerSet, Component
from coopr.pyomo.base import active_components_generator, active_subcomponents_generator
from coopr.pyomo.base import Var, value, label_from_name, NumericConstant
from coopr.pyomo.base.sos import SOSConstraint
from coopr.pyomo.base.objective import Objective, minimize, maximize

from pyutilib.component.core import alias
from pyutilib.misc import tostr, PauseGC

class CPXLP_numeric_labeler(object):

    def __init__(self, prefix):

        self.id = 0
        self.prefix = prefix

    def __call__(self, obj):

        self.id += 1
        return self.prefix + str(self.id)

class CPXLP_text_labeler(object):

    def __call__(self, obj):

        try:
            # the most common input object is something that is an element
            # of an indexed component - in this case, we're looking for 
            # the parent component, to try to chase up the block chain.
            block = obj.component()
        except:
            # if we can't find a "component" attribute, then this might be 
            # an indexed or non-indexed component - rather than a part of such
            # a compoent.d in this case, we just assign the "block" (which is 
            # a terrible name in this context) to the current component. 
            # subsequent logic in this function will cause the parent-chasing
            # to occur.
            if isinstance(obj, Component):
                block = obj
            else:
                block = None

        if block is None:
            return label_from_name(str(obj.name))
        block = block._parent
        if block is None:
            return label_from_name(str(obj.name))

        label = str(obj.name)

        block = block()
        while block._parent is not None and block._parent() is not None:
            label = block.name + "." + label
            block = block._parent()
        return label_from_name(label)

class ProblemWriter_cpxlp(AbstractProblemWriter):

    alias('cpxlp')
    alias('lp')

    def __init__(self):

        AbstractProblemWriter.__init__(self, ProblemFormat.cpxlp)

        # the LP writer is responsible for tracking which variables are referenced in constraints,
        # so that one doesn't end up with a zillion "unreferenced variables" warning messages.
        # stored at the object level to avoid additional method arguments. collection of id(_VarData).
        self._referenced_variable_ids = set()

    def __call__(self, model, output_filename, solver_capability, generate_symbolic_labels):

        # when sorting, there are a non-trivial number of temporary objects
        # created. these all yield non-circular references, so disable GC -
        # the overhead is non-trivial, and because references are non-circular,
        # everything will be collected immediately anyway.
        suspend_gc = PauseGC()

        # clear the collection of referenced variables.
        self._referenced_variable_ids.clear()

        if output_filename is None:
            output_filename = model.name + ".lp"

        output_file=open(output_filename, "w")
        symbol_map = self._print_model_LP(model, output_file, solver_capability, generate_symbolic_labels)
        output_file.close()

        return output_filename, symbol_map

    def _get_bound(self, exp):

        if isinstance(exp,expr._IdentityExpression):
            return self._get_bound(exp._args[0])
        elif exp.is_fixed():
            return exp()
        else:
            raise ValueError, "ERROR: non-fixed bound: " + str(exp)
            return None

    def _print_expr_linear(self, x, output_file, object_symbol_dictionary, is_objective):

        """
        Return a expression as a string in LP format.

        Note that this function does not handle any differences in LP format
        interpretation by the solvers (e.g. CPlex vs GLPK).  That decision is
        left up to the caller.

        required arguments:
          x: A Pyomo linear encoding of an expression to write in LP format
        """

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

                var_id = id(var_value)
                if var_id not in self._referenced_variable_ids:
                    self._referenced_variable_ids.add(var_id)

                name = object_symbol_dictionary[id(var_value)]

                # due to potential disabling of expression simplification,
                # variables might appear more than once - condense coefficients.
                name_to_coefficient_map[name] = coefficient + name_to_coefficient_map.get(name,0.0)

        sorted_names = sorted(name_to_coefficient_map.keys())

        for name in sorted_names:

            coefficient = name_to_coefficient_map[name]

            sign = '+'
            if coefficient < 0: sign = '-'
            print >>output_file, '%s%f %s' % (sign, math.fabs(coefficient), name)

        if print_offset and (constant_term != 0.0):
            sign = '+'
            if constant_term < 0: sign = '-'
            print >>output_file, '%s%f %s' % (sign, math.fabs(constant_term), 'ONE_VAR_CONSTANT')

        return constant_term


    def _print_expr_canonical(self, x, output_file, object_symbol_dictionary, is_objective):

        """
        Return a expression as a string in LP format.

        Note that this function does not handle any differences in LP format
        interpretation by the solvers (e.g. CPlex vs GLPK).  That decision is
        left up to the caller.

        required arguments:
          x: A Pyomo canonical expression to write in LP format
        """

        # cache - this is referenced numerous times.
        var_hashes = x[-1]

        #
        # Linear
        #
        if 1 in x:

            for var_hash in x[1]:
                var_id = id(var_hashes[var_hash])
                if var_id not in self._referenced_variable_ids:
                    self._referenced_variable_ids.add(var_id)            

            sorted_names = [(object_symbol_dictionary[id(var_hashes[var_hash])], var_coefficient) for var_hash, var_coefficient in x[1].iteritems()]
            sorted_names.sort()

            for name, coef in sorted_names:
                # there are various situations in which the coefficients may be equal to 0.0,
                # in which case there is no real reason to output the corresponding terms.
                if coef: # != 0.0:
                    print >>output_file, '%+f' % coef, name

        #
        # Quadratic
        #
        if 2 in x:

            # first, make sure there is something to output - it is possible for all
            # terms to have coefficients equal to 0.0, in which case you don't want
            # to get into the bracket notation at all.
            # NOTE: if the coefficient is really 0.0, it should be preprocessed out by
            #       the canonial expression generator!
            found_nonzero_term = False # until proven otherwise
            for var_hash, var_coefficient in x[2].iteritems():
                for var in var_hash:
                    var_value = var_hashes[var]
                    var_id = id(var_value)
                    if var_id not in self._referenced_variable_ids:
                        self._referenced_variable_ids.add(var_id)
                    
                if math.fabs(var_coefficient) != 0.0:
                    found_nonzero_term = True
                    break

            if found_nonzero_term:

                print >>output_file, "+ ["

                num_output = 0

                for var_hash in sorted(x[2].keys()):

                    coefficient = x[2][var_hash]
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

                    print >>output_file, sign, coefficient,

                    term_variables = []

                    for var in var_hash:
                        var_value = var_hashes[var]
                        name = object_symbol_dictionary[id(var_value)]
                        term_variables.append(name)

                    if len(term_variables) == 2:
                        print >>output_file, term_variables[0],"*",term_variables[1],
                    else:
                        print >>output_file, term_variables[0],"^ 2",
                    print >>output_file, ""

                print >>output_file, ""

                print >>output_file, "]",

                if is_objective:
                    print >>output_file, ' / 2'
                    # divide by 2 because LP format requires /2 for all the quadratic
                    # terms.  Weird.  Ref: ILog CPlex 8.0 User's Manual, p197
                else:
                    print >>output_file, ""


        #
        # Constant offset
        #
        if 0 in x:
            offset = x[0][None]
        else:
            offset=0.0

        # Currently, it appears that we only need to print the constant
        # offset term for objectives.
        if is_objective and offset != 0.0:
            print >>output_file, '%s%f %s' % (offset < 0 and '-' or '+', math.fabs(offset), 'ONE_VAR_CONSTANT')

        #
        # Return constant offset
        #
        return offset

    @staticmethod
    def printSOS(symbol_map,labeler, con, name, output_file, index=None):

        """
        Returns the SOS constraint (as a string) associated with con.
        If specified, index is passed to con.sos_set().

        Arguments:
        con    The SOS constraint object
        name   The name of the variable
        output_file The output stream
        index  [Optional] the index to pass to the sets indexing the variables.
        """

        # The name of the variable being indexed
        var = con.sos_vars()

        # The list of variable names to be printed, including indices
        varNames = []

        # Get all the variables
        if index is None:
            tmpSet = con.sos_set()
        else:
            tmpSet = con.sos_set()[index]
        for idx in tmpSet:
            varNames.append(symbol_map.getSymbol(var[idx],labeler))

        
        conNameIndex = ""
        if index is not None:
            if type(index) is tuple:
                conNameIndex += label_from_name(tostr(index))
            else:
                conNameIndex += label_from_name(str(index))

        print >>output_file, '%s_%s: S%s::' % (symbol_map.getSymbol(con,labeler), conNameIndex, con.sos_level())

        # We need to 'weight' each variable
        # For now we just increment a counter
        for i in range(0, len(varNames)):
            print >>output_file, '%s:%f' % (varNames[i], i+1)

    #
    # a simple utility to pass through each variable and constraint
    # in the input model and populate the symbol map accordingly. once
    # we know all of the objects in the model, we can then "freeze"
    # the contents and use more efficient query mechanisms on simple
    # dictionaries - and avoid checking and function call overhead.
    #
    def _populate_symbol_map(self, model, symbol_map, labeler):

        # NOTE: we use createSymbol instead of getSymbol because we know
        # whether or not the symbol exists, and don't want to the overhead
        # of error/duplicate checking.

        # cache frequently called functions
        create_symbol_func = SymbolMap.createSymbol
        create_symbols_func = SymbolMap.createSymbols
        alias_symbol_func = SymbolMap.alias

        for block in model.all_blocks():

            active_objectives = model.active_components(Objective)
            # all blocks don't necessarily have an objective.
            if len(active_objectives) > 0:
               objective = active_objectives[active_objectives.keys()[0]]
               objective_data = objective[objective.keys()[0]]
               create_symbol_func(symbol_map, objective_data, labeler)
               alias_symbol_func(symbol_map, objective_data, '__default_objective__')

            for constraint_data in itertools.chain(active_subcomponents_generator(block, Constraint), 
                                                   active_subcomponents_generator(block, ConstraintList)):
                constraint_data_symbol = create_symbol_func(symbol_map, constraint_data, labeler)
                if constraint_data._equality:
                    label = 'c_e_' + constraint_data_symbol + '_'
                    alias_symbol_func(symbol_map, constraint_data, label)
                else:
                    if constraint_data.lower is not None:
                        label = 'c_l_' + constraint_data_symbol + '_'
                        alias_symbol_func(symbol_map, constraint_data, label)
                    if constraint_data.upper is not None:
                        label = 'c_u_' + constraint_data_symbol + '_'
                        alias_symbol_func(symbol_map, constraint_data, label)

            create_symbols_func(symbol_map, active_subcomponents_generator(block, Var), labeler)

            # TBD - MOVE TO ABOVE, WITH OTHER CONSTRAINTS - ASSUMING THEY HAVE SUB_COMPONENTS?
            sos_con_list = block.active_components(SOSConstraint)
            for con in sos_con_list.itervalues():
                create_symbol_func(symbol_map, con, labeler)

    def _print_model_LP(self, model, output_file, solver_capability, generate_symbolic_labels):

        symbol_map = SymbolMap(model)

        if generate_symbolic_labels is True:
            labeler = CPXLP_text_labeler()
        else:
            labeler = CPXLP_numeric_labeler('x')

        # populate the symbol map in a single pass.
        self._populate_symbol_map(model, symbol_map, labeler)

        # and extract the information we'll need for rapid labeling.
        object_symbol_dictionary = symbol_map.getByObjectDictionary()

        # cache - these are called all the time.
        print_expr_linear = self._print_expr_linear
        print_expr_canonical = self._print_expr_canonical

        #
        # Objective
        #
        _obj = model.active_components(Objective)

        supports_quadratic = solver_capability('quadratic')

        if len(_obj) == 0:
            msg = "ERROR: No objectives defined for input model '%s'; "    \
                  ' cannot write legal LP file'
            raise ValueError, msg % str( model.name )
        if len(_obj) > 1:
            msg = "More than one objective defined for input model '%s'; " \
                  'Cannot write legal LP file\n'                           \
                  'Objectives: %s'
            raise ValueError(
                msg % ( model.name,', '.join("'%s'" % x for x in _obj) ))

        obj = _obj[ _obj.keys()[0] ]
        if obj.sense == maximize:
            print >>output_file, "max "
        else:
            print >>output_file, "min "

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

            print >>output_file, object_symbol_dictionary[id(obj_data)] \
                 + ": +0.0 ONE_VAR_CONSTANT"

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
                if obj_keys[0] is None:
                    msg %= (obj.name, '')
                else:
                    msg %= (obj.name, '[%s]' % obj_keys[0] )
                raise RuntimeError, msg

            print >>output_file, object_symbol_dictionary[id(obj_data)]+':'

            offset = print_expr_canonical( obj_data.repn,
                                                 output_file,
                                                 object_symbol_dictionary,
                                                 True )

            print >>output_file, ""

        # Constraints
        #
        # If there are no non-trivial constraints, you'll end up with an empty
        # constraint block. CPLEX is OK with this, but GLPK isn't. And
        # eliminating the constraint block (i.e., the "s.t." line) causes GLPK
        # to whine elsewhere. output a warning if the constraint block is empty,
        # so users can quickly determine the cause of the solve failure.

        print >>output_file, "s.t."
        print >>output_file, ""

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

                    con_symbol = object_symbol_dictionary[id(constraint_data)]
                    if constraint_data._equality:
                        label = 'c_e_' + con_symbol + '_'
                        print >>output_file, label+':'
                        if constraint_data.lin_body is not None:
                            offset = print_expr_linear(constraint_data.lin_body, output_file, object_symbol_dictionary, False)
                        else:
                            offset = print_expr_canonical(constraint_data.repn, output_file, object_symbol_dictionary, False)
                        bound = constraint_data.lower
                        bound = self._get_bound(bound) - offset
                        print >>output_file, "=", bound
                        print >>output_file, ""
                    else:
                        if constraint_data.lower is not None:
                            label = 'c_l_' + con_symbol + '_'
                            print >>output_file, label+':'
                            if constraint_data.lin_body is not None:
                                offset = print_expr_linear(constraint_data.lin_body, output_file, object_symbol_dictionary, False)
                            else:
                                offset = print_expr_canonical(constraint_data.repn, output_file, object_symbol_dictionary, False)
                            bound = constraint_data.lower
                            bound = self._get_bound(bound) - offset
                            print >>output_file, ">=", bound
                            print >>output_file, ""
                        if constraint_data.upper is not None:
                            label = 'c_u_' + con_symbol + '_'
                            print >>output_file, label+':'
                            if constraint_data.lin_body is not None:
                                offset = print_expr_linear(constraint_data.lin_body, output_file, object_symbol_dictionary, False)
                            else:
                                offset = print_expr_canonical(constraint_data.repn, output_file, object_symbol_dictionary, False)
                            bound = constraint_data.upper
                            bound = self._get_bound(bound) - offset
                            print >>output_file, "<=", bound
                            print >>output_file, ""

        if not have_nontrivial:
            print 'WARNING: Empty constraint block written in LP format '  \
                  '- solver may error'

        # the CPLEX LP format doesn't allow constants in the objective (or
        # constraint body), which is a bit silly.  To avoid painful
        # book-keeping, we introduce the following "variable", constrained
        # to the value 1.  This is used when quadratic terms are present.
        # worst-case, if not used, is that CPLEX easily pre-processes it out.
        prefix = ""
        print >>output_file, '%sc_e_ONE_VAR_CONSTANT: ' % prefix
        print >>output_file, '%sONE_VAR_CONSTANT = 1.0' % prefix
        print >>output_file, ""

        #
        # Bounds
        #

        print >>output_file, "bounds "

        # Scan all variables even if we're only writing a subset of them.
        # required because we don't store maps by variable type currently.

        # Track the number of integer and binary variables, so you can
        # output their status later.
        niv = nbv = 0

        # FIXME: This is a hack to get nested blocks working...
        for block in model.all_blocks():
            for var_value in active_subcomponents_generator(block, Var, sort_by_keys=True):

                if (not var_value.active) or (var_value.fixed is True) or (id(var_value) not in self._referenced_variable_ids):
                    continue

                # track the number of integer and binary variables, so we know whether
                # to output the general / binary sections below.
                if isinstance(var_value.domain, IntegerSet):   niv += 1
                elif isinstance(var_value.domain, BooleanSet): nbv += 1

                # in the CPLEX LP file format, the default variable
                # bounds are 0 and +inf.  These bounds are in
                # conflict with Pyomo, which assumes -inf and +inf
                # (which we would argue is more rational).
                print >>output_file,"   ",
                if var_value.lb is not None:
                    print >>output_file, value(var_value.lb), "<= ",
                else:
                    print >>output_file, " -inf <= ",
                name_to_output = object_symbol_dictionary[id(var_value)]
                if name_to_output == "e":
                    msg = 'Attempting to write variable with name' \
                        "'e' in a CPLEX LP formatted file - "    \
                        'will cause a parse failure due to '     \
                        'confusion with numeric values '         \
                        'expressed in scientific notation'
                    raise ValueError, msg
                print >>output_file, name_to_output,
                if var_value.ub is not None:
                    print >>output_file, " <=", value(var_value.ub)
                else:
                    print >>output_file, " <= +inf"

        if niv > 0:

            print >>output_file, "general"

            for block in model.all_blocks():
                for variable in active_components_generator(block, Var, sort_by_keys=True):
                    for index in sorted(variable.integer_keys()):
                        var_value = variable[index]
                        if (not var_value.active) or (var_value.fixed is True) or (id(var_value) not in self._referenced_variable_ids):
                            continue
                        var_name = object_symbol_dictionary[id(var_value)]
                        print >>output_file, ' ', var_name

        if nbv > 0:

            print >>output_file, "binary"

            for block in model.all_blocks():
                for variable in active_components_generator(block, Var, sort_by_keys=True):
                    for index in sorted(variable.binary_keys()):
                        var_value = variable[index]
                        if (not var_value.active) or (var_value.fixed is True) or (id(var_value) not in self._referenced_variable_ids):
                            continue
                        var_name = object_symbol_dictionary[id(var_value)]
                        print >>output_file, ' ', var_name


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
                    print >>output_file, "SOS"
                    writtenSOS = True
                name = symbol_map.getSymbol( con, labeler )
                masterIndex = con.sos_set_set()
                if None in masterIndex:
                    # A single constraint
                    self.printSOS(symbol_map, labeler, con, name, output_file)
                else:
                    # A series of indexed constraints
                    for index in masterIndex:
                        self.printSOS(symbol_map, labeler, con, name, output_file, index)


        #
        # wrap-up
        #
        print >>output_file, "end "

        return symbol_map
