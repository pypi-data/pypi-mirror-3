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
# AMPL Problem Writer Plugin
#

from coopr.opt import ProblemFormat, WriterFactory
from coopr.opt.base import *
from coopr.pyomo.base.objective import minimize, maximize
from coopr.pyomo.base import *
from coopr.pyomo.base import expr
from coopr.pyomo.base import intrinsic_functions
from coopr.pyomo.base.var import _VarData, Var, _VarElement, _VarBase
from coopr.pyomo.base import numvalue
from coopr.pyomo.base.param import _ParamData
from coopr.pyomo.base import var
from coopr.pyomo.base import param
from pyutilib.component.core import alias
from pyutilib.misc import PauseGC

from coopr.opt.base import SymbolMap
import itertools

import time
import gc

import logging
logger = logging.getLogger('coopr.pyomo')

ampl_var_id = {}

intrinsic_function_expressions = {'log':'o43', 'log10':'o42', 'sin':'o41', 'cos':'o46', 'tan':'o38', 'sinh':'o40', 'cosh':'o45', 'tanh':'o37', 'asin':'o51', 'acos':'o53', 'atan':'o49', 'exp':'o44', 'sqrt':'o39', 'asinh':'o50', 'acosh':'o52', 'atanh':'o47', 'pow':'o5'}

__all__ = ['ampl_var_id', 'intrinsic_function_expressions', 'ProblemWriter_nl', 'ampl_representation', 'generate_ampl_repn', 'generate_ef_ampl_repn', "_trivial_labeler"]


class _trivial_labeler(object):
    def __call__(self, obj, *args):
        label = str(obj.name)

        try:
            block = obj.component
        except:
            block = None

        if block is None:
            return nl_label_from_name(label)
        block = block()._parent
        if block is None:
            return nl_label_from_name(label)

#        block = block()
        while block is not None:
            block = block()
            label = block.name + "." + label
            block = block._parent
        return nl_label_from_name(label)

class ModelSOS(object):
    def __init__(self):
        self.sosno_list = []
        self.ref_list = []
        self.block_cntr = 0

    def count_constraint(self,con,symbol_map, labeler,level,index=None):

        # Identifies the the current set from others in the NL file
        self.block_cntr += 1

        # If SOS1, the identifier must be positive
        # if SOS2, the identifier must be negative
        sign_tag = 1
        if level == 2:
            sign_tag = -1

        # The name of the variable being indexed
        prefix = symbol_map.getSymbol(con.sos_vars()._model(), labeler)
        varName = prefix + "_" + str(con.sos_vars())

        if index is None:
            tmpSet = con.sos_set()
        else:
            tmpSet = con.sos_set()[index]

        # Get all the variables
        cntr = 0
        for x in tmpSet:
            ID = ampl_var_id[symbol_map.getSymbol( con.sos_vars()[x], labeler )]
            self.sosno_list.append((ID,self.block_cntr*sign_tag))
            # We need to weight each variable
            # For now we just increment a counter
            if cntr > 0:
                # We only need to report variables with weight greater than zero
                # Zero weight is assumed for variables with no weight reported.
                self.ref_list.append((ID,cntr))
            cntr += 1


class ProblemWriter_nl(AbstractProblemWriter):

    alias(str(ProblemFormat.nl))

    def __init__(self):
        AbstractProblemWriter.__init__(self,ProblemFormat.nl)

    def __call__(self, model, filename, solver_capability):
        # Pause the GC for the duration of this method
        suspend_gc = PauseGC()
        if filename is None:
            filename = model.name + ".nl"
        OUTPUT=open(filename,"w")
        ampl_var_id.clear()
        symbol_map = self._print_model_NL(model, OUTPUT, solver_capability, verbose=False, gen_obj_ampl_repn=True, gen_con_ampl_repn=True)
        OUTPUT.close()
        return filename, symbol_map

    def _get_bound(self, exp):
        if exp.is_constant():
            return exp()
        else:
            raise ValueError, "ERROR: nonconstant bound: " + str(exp)
            return None

        exp_type = type(exp)
        if exp_type is NumericConstant:
            return exp.value
        elif exp_type is _ParamData:
            return exp.value
        elif exp_type is expr._SumExpression:
            sum_expr_value=0.0
            for i in xrange(len(exp._args)):
                sum_expr_value += self._get_bound(exp._args[i])*exp._coef[i]
            return sum_expr_value
        elif exp_type is expr._ProductExpression:
            prod_expr_value=1.0
            for i in xrange(len(exp._numerator)):
                prod_expr_value *= float(self._get_bound(exp._numerator[i]))
            for i in xrange(len(exp._denominator)):
                prod_expr_value /= float(self._get_bound(exp._denominator[i]))
            return prod_expr_value
        else:
            raise ValueError, "ERROR: nonconstant bound: " + str(exp)
            return None

    def _print_nonlinear_terms_NL(self, OUTPUT, exp, symbol_map, labeler):

        if isinstance(exp, expr._IntrinsicFunctionExpression):
            if exp.name in intrinsic_function_expressions:
                print >>OUTPUT, intrinsic_function_expressions[exp.name]
            else:
                logger.error("Unsupported intrinsic function ({0})", exp.name)
                raise TypeError("ASL writer does not support '{0}' expressions"
                               .format(exp.name))
                
            for child_exp in exp._args:
                self._print_nonlinear_terms_NL(OUTPUT, child_exp, symbol_map, labeler)

        elif isinstance(exp, expr._SumExpression):
            n = len(exp._args)

            if n > 2:
#                print >>OUTPUT, "o54  #sum"
                print >>OUTPUT, "o54"
                print >>OUTPUT, n

                if exp._const != 0.0:
#                    print >>OUTPUT, "o0  #+"
                    print >>OUTPUT, "o0"
                    print >>OUTPUT, "n{0}".format(exp._const)

                for i in xrange(0,n):
                    if exp._coef[i] != 1:
#                        print >>OUTPUT, "o2  #*"
                        print >>OUTPUT, "o2"
                        print >>OUTPUT, "n{0}".format(exp._coef[i])
                    self._print_nonlinear_terms_NL(OUTPUT, exp._args[i], symbol_map, labeler)
            else:
                if exp._const != 0.0:
#                    print >>OUTPUT, "o0  #+"
                    print >>OUTPUT, "o0"
                    print >>OUTPUT, "n{0}".format(exp._const)

                for i in xrange(0,n-1):
#                    print >>OUTPUT, "o0  #+"
                    print >>OUTPUT, "o0"
                    if exp._coef[i] != 1:
#                        print >>OUTPUT, "o2  #*"
                        print >>OUTPUT, "o2"
                        print >>OUTPUT, "n{0}".format(exp._coef[i])
                    self._print_nonlinear_terms_NL(OUTPUT, exp._args[i], symbol_map, labeler)

                if exp._coef[n-1] != 1:
#                    print >>OUTPUT, "o2  #*"
                    print >>OUTPUT, "o2"
                    print >>OUTPUT, "n{0}".format(exp._coef[n-1])
                self._print_nonlinear_terms_NL(OUTPUT, exp._args[n-1], symbol_map, labeler)

        elif isinstance(exp, list):
            # this is an implied summation of expressions (we did not create a new sum expression for efficiency)
            # this should be a list of tuples where [0] is the coeff and [1] is the expr to write
            n = len(exp)
            if n > 2:
#                print >>OUTPUT, "o54  #sum"
                print >>OUTPUT, "o54"
                print >>OUTPUT, n

                for i in xrange(0,n):
                    assert(isinstance(exp[i],tuple))
                    coef = exp[i][0]
                    child_exp = exp[i][1]

                    if coef != 1.0:
#                        print >>OUTPUT, "o2  #*"
                        print >>OUTPUT, "o2"
                        print >>OUTPUT, "n{0}".format(coef)
                    self._print_nonlinear_terms_NL(OUTPUT, child_exp, symbol_map, labeler)
            else:
                for i in xrange(0,n):
                    assert(isinstance(exp[i],tuple))
                    coef = exp[i][0]
                    child_exp = exp[i][1]

                    if i != n-1:
                        # need the + op if it is not the last entry in the list
#                        print >>OUTPUT, "o0  #+"
                        print >>OUTPUT, "o0"

                    if coef != 1.0:
#                        print >>OUTPUT, "o2  #*"
                        print >>OUTPUT, "o2"
                        print >>OUTPUT, "n{0}".format(coef)
                    self._print_nonlinear_terms_NL(OUTPUT, child_exp, symbol_map, labeler)

        elif isinstance(exp, expr._ProductExpression):
            denom_exists = False
            if len(exp._denominator) == 0:
                pass
            else:
#                print >>OUTPUT, "o3 # /"
                print >>OUTPUT, "o3"
                denom_exists = True

            if exp.coef != 1:
#                print >>OUTPUT, "o2 # *"
                print >>OUTPUT, "o2"
                print >>OUTPUT, "n{0}".format(exp.coef)

            if len(exp._numerator) == 0:
                print >>OUTPUT, "n1"

            # print out the numerator
            child_counter = 0
            max_count = len(exp._numerator)-1
            for child_exp in exp._numerator:
                if child_counter < max_count:
#                    print >>OUTPUT, "o2  #*"
                    print >>OUTPUT, "o2"
                self._print_nonlinear_terms_NL(OUTPUT, child_exp, symbol_map, labeler)
                child_counter += 1

            if denom_exists:
            # print out the denominator
                child_counter = 0
                max_count = len(exp._denominator)-1
                for child_exp in exp._denominator:
                    if child_counter < max_count:
#                        print >>OUTPUT, "o2  #*"
                        print >>OUTPUT, "o2"
                    self._print_nonlinear_terms_NL(OUTPUT, child_exp, symbol_map, labeler)
                    child_counter += 1

        elif isinstance(exp, expr._PowExpression):
#            print >>OUTPUT, "o5  #^"
            print >>OUTPUT, "o5"
            for child_exp in exp._args:
                self._print_nonlinear_terms_NL(OUTPUT, child_exp, symbol_map, labeler)

        elif (isinstance(exp,var._VarData) or isinstance(exp,var.Var)) and not exp.fixed_value():
#            print >>OUTPUT, "v{0} #{1}".format(ampl_var_id[exp.name], exp.name)
#            print >>OUTPUT, "v{0} #{1}".format(ampl_var_id[exp.name], exp.name)
            variable_label = symbol_map.getSymbol(exp, labeler)
            print >>OUTPUT, "v{0}".format(ampl_var_id[variable_label])

        elif isinstance(exp,param._ParamData):
#            print >>OUTPUT, "n{0} #{1}".format(exp.value, exp.name)
            print >>OUTPUT, "n{0}".format(exp.value)

        elif (isinstance(exp,numvalue.NumericConstant) or exp.fixed_value):
#            print >>OUTPUT, "n{0} # numeric constant".format(exp.value)
            print >>OUTPUT, "n{0}".format(exp.value)

        else:
            raise ValueError, "Unsupported expression type in _print_nonlinear_terms_NL"
        
    
    def _print_model_NL(self, model, OUTPUT, solver_capability, verbose=False, gen_obj_ampl_repn=True, gen_con_ampl_repn=True):

        # maps NL variables to the "real" variable names in the problem.
        # it's really NL variable ordering, as there are no variable names
        # in the NL format. however, we by convention make them go from
        # x0 upward.

#        start_overall_time = time.clock()

#        if type(model) is dict:
#            symbol_map = self._print_ef(model, OUTPUT)
#            return symbol_map

        # because NL preprocessing occurs during the write process, we don't have direct access to
        # this method through the solve() method of a solver plugin. and keyword propagation is too
        # complex to think that would be a good solution. so, we can optionally tag the input
        # instance with the preprocessing keywords.
        if hasattr(model, "gen_obj_ampl_repn"):
            gen_obj_ampl_repn = getattr(model, "gen_obj_ampl_repn")
            delattr(model, "gen_obj_ampl_repn")
        if hasattr(model, "gen_con_ampl_repn"):
            gen_con_ampl_repn = getattr(model, "gen_con_ampl_repn")
            delattr(model, "gen_con_ampl_repn")            
            
        symbol_map = SymbolMap(model)
        labeler = _trivial_labeler()

        #
        # Collect statistics
        #
        Obj = model.active_components(Objective)

        Vars = dict() # will be the entire list of all vars used in the problem
        # linear variables
        LinearVars = set()
        LinearVarsInt = set()
        LinearVarsBool = set()
        #
        # Count number of objectives and build the ampl_repns
        #

#        print "Generate objective representation:",
#        start_time = time.clock()

        n_objs = 0
        n_nonlinear_objs = 0
        ObjVars = set()
        ObjNonlinearVars = set()
        ObjNonlinearVarsInt = set()
        for obj in Obj:
            for i in Obj[obj]:
                tmp_obj = Obj[obj][i]

                if gen_obj_ampl_repn is True:
                    ampl_repn = generate_ampl_repn(tmp_obj.expr, symbol_map, labeler)
                    tmp_obj.ampl_repn = ampl_repn
                else:
                    ampl_repn = tmp_obj.ampl_repn
                Vars.update(ampl_repn._linear_terms_var)
                Vars.update(ampl_repn._nonlinear_vars)

                LinearVars.update(ampl_repn._linear_terms_var)
                ObjNonlinearVars.update(ampl_repn._nonlinear_vars)
                    
                ObjVars.update(ampl_repn._linear_terms_var)
                ObjVars.update(ampl_repn._nonlinear_vars)
                n_objs += 1
                if ampl_repn.is_nonlinear():
                    n_nonlinear_objs += 1

        if n_objs > 1:
            raise ValueError, "asl solver has detected multiple objective functions, but currently only handles a single objective."

#        end_time = time.clock()
#        print (end_time - start_time)

#        print "Generate constraint repns:",
#        start_time = time.clock()

        #
        # Count number of constraints and build the ampl_repns
        #

        n_ranges = 0
        n_single_sided_ineq = 0
        n_equals = 0
        n_nonlinear_constraints = 0
        ConNonlinearVars = set()
        ConNonlinearVarsInt = set()
        nnz_grad_constraints = 0
        constraint_bounds_dict = {}
        stack_lin = {}
        stack_nonlin = {}
        nonlin_con_order_list = []
        lin_con_order_list = []

#        Con = model.active_components(Constraint)
#        Con.update( model.active_components(ConstraintList) )
        
        for block in model.all_blocks():
            active_constraints = block.active_components(Constraint)
            active_constraintlists = block.active_components(ConstraintList)
            for constraint in itertools.chain(active_constraints.itervalues(), active_constraintlists.itervalues()):
                if constraint.trivial is True:
                    continue
                
                for index in sorted(constraint.keys()):
                    constraint_data = constraint[index]
                    if not constraint_data.active:
                        continue

                    con_name = symbol_map.getSymbol( constraint_data, labeler )
                    if gen_con_ampl_repn is True:
                        ampl_repn = generate_ampl_repn(constraint_data.body, symbol_map, labeler)
                        constraint_data.ampl_repn = ampl_repn
                    else:
                        ampl_repn = constraint_data.ampl_repn

                    linear_vars = ampl_repn._linear_terms_var
                    nonlinear_vars = ampl_repn._nonlinear_vars
                    if is_constant(ampl_repn):
                        continue
    
                    # Merge variables from this expression
                    all_vars = {}
                    all_vars.update(linear_vars)
                    all_vars.update(nonlinear_vars)
                    Vars.update(all_vars)
                    nnz_grad_constraints += len(all_vars)
    
                    LinearVars.update(linear_vars)
                    ConNonlinearVars.update(nonlinear_vars)
    
                    if ampl_repn.is_nonlinear():
                        stack_nonlin[con_name] = constraint_data
                        nonlin_con_order_list.append(con_name)
                        n_nonlinear_constraints += 1
                    else:
                        stack_lin[con_name] = constraint_data
                        lin_con_order_list.append(con_name)
    
                    L = None
                    U = None
                    if constraint_data.lower is not None: L = self._get_bound(constraint_data.lower)
                    if constraint_data.upper is not None: U = self._get_bound(constraint_data.upper)
                    offset = ampl_repn._constant
                    if L == U:
                        if (L is None):
#                            constraint_bounds_dict[con_name] = [3, '', '', con_name]
                            constraint_bounds_dict[con_name] = [3, '', '']
                            # constraint with NO bounds ???
                            raise ValueError, "Constraint " + str(con) +\
                                             "[" + str(i) + "]: lower bound = None and upper bound = None"
                        else:
#                            constraint_bounds_dict[con_name] = [4, L-offset, '', con_name]
                            constraint_bounds_dict[con_name] = [4, L-offset, '']
                            n_equals += 1
                    elif L is None:
#                        constraint_bounds_dict[con_name] = [1, '', U-offset, con_name]
                        constraint_bounds_dict[con_name] = [1, '', U-offset]
                        n_single_sided_ineq += 1
                    elif U is None:
#                        constraint_bounds_dict[con_name] = [2, L-offset, '', con_name]
                        constraint_bounds_dict[con_name] = [2, L-offset, '']
                        n_single_sided_ineq += 1
                    elif (L > U):
                        msg = 'Constraint {0}: lower bound greater than upper' \
                              ' bound ({1} > {2})'
                        raise ValueError, msg.format(con_name, str(L), str(U))
                    else:
#                        constraint_bounds_dict[con_name] = [0, L-offset, U-offset, con_name]
                        constraint_bounds_dict[con_name] = [0, L-offset, U-offset]
                        # double sided inequality
                        # both are not none and they are valid
                        n_ranges += 1


        LinearVars = LinearVars.difference(ObjNonlinearVars)
        LinearVars = LinearVars.difference(ConNonlinearVars)

        if model.statistics.number_of_binary_variables != 0 or model.statistics.number_of_integer_variables != 0:
            var_names = LinearVars.copy()
            for var_name in var_names:
                var = Vars[var_name]
                var_type = type(var.domain)
                if var_type is IntegerSet:
                    LinearVarsInt.add(var_name)
                    LinearVars.discard(var_name)
                elif var_type is BooleanSet:
                    L = var.lb
                    U = var.ub
                    if L is None or U is None:
                        raise ValueError, "Variable " + str(var.name) +\
                            "is binary, but does not have lb and ub set"
                    elif value(L) == 0 and value(U) == 1:
                        LinearVarsBool.add(var_name)
                        LinearVars.discard(var_name)
                    else:
                        LinearVarsInt.add(var_name)
                        LinearVars.discard(var_name)

            var_names = ObjNonlinearVars.copy()
            for var_name in var_names:
                var_type = type(Vars[var_name].domain)
                if var_type is IntegerSet or var_type is BooleanSet:
                    ObjNonlinearVarsInt.add(var_name)
                    ObjNonlinearVars.discard(var_name)
            var_names = ConNonlinearVars.copy()
            for var_name in var_names:
                var_type = type(Vars[var_name].domain)
                if var_type is IntegerSet or var_type is BooleanSet:
                    ConNonlinearVarsInt.add(var_name)
                    ConNonlinearVars.discard(var_name)

        Nonlinear_Vars_in_Objs_and_Constraints = ObjNonlinearVars.intersection(ConNonlinearVars)
        Discrete_Nonlinear_Vars_in_Objs_and_Constraints = ObjNonlinearVarsInt.intersection(ConNonlinearVarsInt)
        ObjNonlinearVars = ObjNonlinearVars.difference(Nonlinear_Vars_in_Objs_and_Constraints)
        ConNonlinearVars = ConNonlinearVars.difference(Nonlinear_Vars_in_Objs_and_Constraints)
        ObjNonlinearVarsInt = ObjNonlinearVarsInt.difference(Discrete_Nonlinear_Vars_in_Objs_and_Constraints)
        ConNonlinearVarsInt = ConNonlinearVarsInt.difference(Discrete_Nonlinear_Vars_in_Objs_and_Constraints)
        

        # put the ampl variable id into the variable
        var_id_ctr=0
        full_var_list = []
        full_var_list.extend(sorted(Nonlinear_Vars_in_Objs_and_Constraints))
        full_var_list.extend(sorted(Discrete_Nonlinear_Vars_in_Objs_and_Constraints))
        full_var_list.extend(sorted(ConNonlinearVars))
        full_var_list.extend(sorted(ConNonlinearVarsInt))
        full_var_list.extend(sorted(ObjNonlinearVars))
        full_var_list.extend(sorted(ObjNonlinearVarsInt))
        full_var_list.extend(sorted(LinearVars))
        full_var_list.extend(sorted(LinearVarsBool))
        full_var_list.extend(sorted(LinearVarsInt))

        for var_name in full_var_list:
            ampl_var_id[var_name] = var_id_ctr
            var_id_ctr += 1


#        end_time = time.clock()
#        print (end_time - start_time)

#        print "Printing NL file header:",
#        start_time = time.clock()
        #
        # Print Header
        #
        # LINE 1
        #
        print >>OUTPUT,"g3 1 1 0\t# problem {0}".format(model.name)
        #
        # LINE 2
        #
        print >>OUTPUT, " {0} {1} {2} {3} {4} \t# vars, constraints, objectives, general inequalities, equalities  " \
           .format(len(Vars), n_single_sided_ineq+n_ranges+n_equals, n_objs, n_ranges, n_equals)
        #
        # LINE 3
        #
        print >>OUTPUT, " {0} {1} \t# nonlinear constraints, objectives".format(n_nonlinear_constraints, n_nonlinear_objs)
        #
        # LINE 4
        #
        print >>OUTPUT, " 0 0\t# network constraints: nonlinear, linear"
        #
        # LINE 5
        #
        nlv_both = len(Discrete_Nonlinear_Vars_in_Objs_and_Constraints)+len(Nonlinear_Vars_in_Objs_and_Constraints)
        print >>OUTPUT, " {0} {1} {2} \t# nonlinear vars in constraints, objectives, both" \
       .format(len(ConNonlinearVarsInt)+len(ConNonlinearVars)+nlv_both, len(ObjNonlinearVarsInt)+len(ObjNonlinearVars)+nlv_both, nlv_both)
             
        #
        # LINE 6
        #
        print >>OUTPUT, " 0 0 0 1\t# linear network variables; functions; arith, flags"
        #
        # LINE 7
        #
        n_int_nonlinear_b = len(Discrete_Nonlinear_Vars_in_Objs_and_Constraints)
        n_int_nonlinear_c = len(ConNonlinearVarsInt)
        n_int_nonlinear_o = len(ObjNonlinearVarsInt) 
        print >>OUTPUT, " {0} {1} {2} {3} {4} \t# discrete variables: binary, integer, nonlinear (b,c,o)" \
           .format(len(LinearVarsBool), len(LinearVarsInt), n_int_nonlinear_b, n_int_nonlinear_c, n_int_nonlinear_o)
        #
        # LINE 8
        #
        # objective info computed above
        print >>OUTPUT, " {0} {1} \t# nonzeros in Jacobian, obj. gradient".format(nnz_grad_constraints, len(ObjVars))
        #
        # LINE 9
        #
        print >>OUTPUT, " 0 0\t# max name lengths: constraints, variables"
        #
        # LINE 10
        #
        print >>OUTPUT, " 0 0 0 0 0\t# common exprs: b,c,o,c1,o1"

#        end_time = time.clock()
#        print (end_time - start_time)

#        print "Printing constraints:",
#        start_time = time.clock()


        # SOS constraints - largely taken from cpxlp.py so updates there,
        # should be applied here
        # TODO: Allow users to specify the variables coefficients for custom
        # branching/set orders - refer to cpxlp.py
        sosn = solver_capability("sos1")
        sos1 = solver_capability("sos2")
        sos2 = solver_capability("sosn")

        if sosn or sos1 or sos2:
            modelSOS = ModelSOS()
            for block in model.all_blocks():
                constrs = block.active_components(SOSConstraint)
                for name, con in constrs.iteritems():
                    level = con.sos_level()
                    if (level == 1 and sos1) or (level == 2 and sos2) or (sosn):
                        masterIndex = con.sos_set_set()
                        if None in masterIndex:
                            modelSOS.count_constraint(con, symbol_map, labeler, level)
                        else:
                            for index in masterIndex:
                                modelSOS.count_constraint(con, symbol_map, labeler, level, index)
                                
            if len(modelSOS.sosno_list) > 0:
                print >>OUTPUT, 'S0', len(modelSOS.sosno_list), 'sosno'
                for sos_var_id, sos_var_block in modelSOS.sosno_list:
                    print >>OUTPUT, sos_var_id, sos_var_block
                print >>OUTPUT, 'S0', len(modelSOS.ref_list), 'ref'
                for sos_var_id, sos_var_weight in modelSOS.ref_list:
                    print >>OUTPUT, sos_var_id, sos_var_weight
            
        #
        # "C" lines
        #
        nc = 0

        cu = [0 for i in xrange(len(Vars))]
        
        constraint_bounds_list = []
        for con_name in nonlin_con_order_list:
            ampl_repn = stack_nonlin[con_name].ampl_repn
            if is_constant(ampl_repn):
                continue

            else:
                print >>OUTPUT, "C{0}\t#{1}".format(nc, con_name)
                cbd = constraint_bounds_dict[con_name]
#                bounds_string = "{0} {1} {2}  # c{3} {4}".format(cbd[0], cbd[1], cbd[2], nc, cbd[3])
                bounds_string = "{0} {1} {2}".format(cbd[0], cbd[1], cbd[2])
                constraint_bounds_list.append(bounds_string)
                #symbol_map["c" + str(nc)] = constraint_data.label
                symbol_map.alias(stack_nonlin[con_name], "c"+str(nc))
                nc += 1

                self._print_nonlinear_terms_NL(OUTPUT, ampl_repn._nonlinear_expr, symbol_map, labeler)

            con_vars = set(ampl_repn._linear_terms_var)
            con_vars.update(ampl_repn._nonlinear_vars)
            for d in con_vars:
                cu[ampl_var_id[d]] += 1

        for con_name in lin_con_order_list:
            ampl_repn = stack_lin[con_name].ampl_repn
            con_vars = set(ampl_repn._linear_terms_var)
            for d in con_vars:
                cu[ampl_var_id[d]] += 1
#            print >>OUTPUT, "C{0}\t#{1}[{2}]".format(nc,key,ndx)
            print >>OUTPUT, "C{0}".format(nc)
            cbd = constraint_bounds_dict[con_name]
#            bounds_string = "{0} {1} {2}  # c{3} {4}".format(cbd[0], cbd[1], cbd[2], nc, cbd[3])
            bounds_string = "{0} {1} {2}".format(cbd[0], cbd[1], cbd[2])
            constraint_bounds_list.append(bounds_string)
            #symbol_map["c" + str(nc)] = C[ndx].label
            symbol_map.alias(stack_lin[con_name], "c"+str(nc))
            nc += 1
            print >>OUTPUT, "n0"

#        end_time = time.clock()
#        print (end_time - start_time)

#        print "Printing objective:",
#        start_time = time.clock()
        #
        # "O" lines
        #
        no = 0
        for key in Obj:
            k = 0
            if Obj[key].sense == maximize:
                k = 1
            for ndx in Obj[key]:
                ampl_repn = Obj[key][ndx].ampl_repn
                if ampl_repn is None:
                    continue
#                print >>OUTPUT, "O{0} {1}\t#{2}[{3}]".format(no, k, key, ndx)
                print >>OUTPUT, "O{0} {1}".format(no, k)
                no += 1

                if ampl_repn.is_linear():
                    print >>OUTPUT, "n{0}".format(ampl_repn._constant)
                else:
                    if ampl_repn._constant != 0.0:
#                        print >>OUTPUT, "o0  #+"
                        print >>OUTPUT, "o0"  #+"
                        print >>OUTPUT, "n{0}".format(ampl_repn._constant)

                    self._print_nonlinear_terms_NL(OUTPUT, ampl_repn._nonlinear_expr, symbol_map, labeler)

#        end_time = time.clock()
#        print (end_time - start_time)

#        print "Printing intializations:",
#        start_time = time.clock()
        #
        # "x" lines
        #
        # variable initialization
        tmp_map = {}
        var_bound_list = []
        for var_name in full_var_list:
            var = Vars[var_name]
            if var.value is not None:
#                tmp_map[ampl_var_id[var_name]] = [var.name,var.value]
                tmp_map[ampl_var_id[var_name]] = var.value
            if isinstance(var.domain, BooleanSet):
#                tmp_string = "0 0 1  # v{0}  {1}".format(ampl_var_id[var_name], var_name)
                tmp_string = "0 0 1"
                var_bound_list.append(tmp_string)
                #symbol_map["v"+str(ampl_var_id[var_name])] = var.label
                symbol_map.getSymbol(var, labeler, "v"+str(ampl_var_id[var_name]))
                symbol_map.alias(var, "v"+str(ampl_var_id[var_name]))
                continue
            L = var.lb
            U = var.ub
            if L is not None:
                Lv = value(L)
                if U is not None:
                    Uv = value(U)
                    if Lv == Uv:
#                        tmp_string = "4 {0}  # v{1}  {2}".format(Lv, ampl_var_id[var_name], var.name)
                        tmp_string = "4 {0}".format(Lv)
                        var_bound_list.append(tmp_string)
                    else:
#                        tmp_string = "0 {0} {1}  # v{2}  {3}".format(Lv, Uv, ampl_var_id[var_name], var.name)
                        tmp_string = "0 {0} {1}".format(Lv, Uv)
                        var_bound_list.append(tmp_string)
                else:
#                    tmp_string = "2 {0}  # v{1}  {2}".format(Lv, ampl_var_id[var_name], var.name)
                    tmp_string = "2 {0}".format(Lv)
                    var_bound_list.append(tmp_string)
            elif U is not None:
#                tmp_string = "1 {0}  # v{1}  {2}".format(value(U), ampl_var_id[var_name], var.name)
                tmp_string = "1 {0}".format(value(U))
                var_bound_list.append(tmp_string)
            else:
#                tmp_string = "3  #v{0}  {1}".format(ampl_var_id[var_name], var.name)
                tmp_string = "3"
                var_bound_list.append(tmp_string)
            #symbol_map["v"+str(ampl_var_id[var_name])] = var.label
            symbol_map.getSymbol(var, labeler, "v"+str(ampl_var_id[var_name]))
            symbol_map.alias(var, "v"+str(ampl_var_id[var_name]))


        print >>OUTPUT, "x{0}".format(len(tmp_map))
        for i in sorted(tmp_map.keys()):
#            print >>OUTPUT, "{0} {1} # {2} initial".format(i,tmp_map[i][1], tmp_map[i][0])
            print >>OUTPUT, i, tmp_map[i]
        
#        end_time = time.clock()
#        print (end_time - start_time)

#        print "Printing constraint bounds:",
#        start_time = time.clock()
        #
        # "r" lines
        #
        print >>OUTPUT, "r"
        for statement in constraint_bounds_list:
            print >>OUTPUT, statement

#        end_time = time.clock()
#        print (end_time - start_time)

#        print "Printing variable bounds:",
#        start_time = time.clock()
        #
        # "b" lines
        #
        print >>OUTPUT, "b"
        for bound in var_bound_list:
            print >>OUTPUT, bound

#        end_time = time.clock()
#        print (end_time - start_time)

#        print "Printing k's:",
#        start_time = time.clock()        

        #
        # "k" lines
        #
        ktot = 0
        n1 = len(Vars) - 1
        print >>OUTPUT, "k{0}".format(n1)
        ktot = 0
        for i in xrange(n1):
            ktot += cu[i]
            print >>OUTPUT, ktot

#        end_time = time.clock()
#        print (end_time - start_time)

#        print "Printing Jacobian's:",
#        start_time= time.clock()

        #
        # "J" lines
        # 
        nc = 0
        stack_ = stack_nonlin
        stack_.update(stack_lin)
        con_order_list = nonlin_con_order_list
        con_order_list.extend(lin_con_order_list)
        for con_name in con_order_list:
            ampl_repn = stack_[con_name].ampl_repn
            con_vars = set(ampl_repn._linear_terms_var)
            con_vars.update(ampl_repn._nonlinear_vars)
            
#            print >>OUTPUT, "J{0} {1} # {2}".format(nc, len(con_vars), con_name)
            print >>OUTPUT, "J{0} {1}".format(nc, len(con_vars))
            nc += 1
            
            for con_var in sorted(con_vars):
                if con_var in ampl_repn._linear_terms_var:
                    print >>OUTPUT, ampl_var_id[con_var], ampl_repn._linear_terms_coef[con_var]
                else:
                    print >>OUTPUT, ampl_var_id[con_var], 0

#        end_time = time.clock()
#        print (end_time - start_time)

#        print "Printing objective gradient:",
#        start_time = time.clock()
        #
        # "G" lines
        #
        no = 0
        grad_entries = {}
        for key in Obj:
            if Obj[key].trivial:
                continue
            obj = Obj[key]
            for ndx in obj:
                ampl_repn = obj[ndx].ampl_repn
                obj_vars = set(ampl_repn._linear_terms_var)
                obj_vars.update(ampl_repn._nonlinear_vars)
                if len(obj_vars) == 0:
                    pass
                else:
                    print >>OUTPUT, "G{0} {1}".format(no, len(obj_vars))
                no += 1

                for obj_var in obj_vars:
                    if obj_var in ampl_repn._linear_terms_var:
                        grad_entries[ampl_var_id[obj_var]] = ampl_repn._linear_terms_coef[obj_var]
                    else:
                        grad_entries[ampl_var_id[obj_var]] = 0

        for var_id in sorted(grad_entries.keys()):
            print >>OUTPUT, var_id, grad_entries[var_id]

#        print (end_time - start_time)
#        end_overall_time = time.clock()
#        print "Total time:",end_overall_time-start_overall_time

        return symbol_map


class ampl_representation:
    __slots__ = ('_constant', '_linear_terms_var', '_linear_terms_coef', '_nonlinear_expr', '_nonlinear_vars', '_name_prefix')
    def __init__(self):
        self._constant = 0
        self._linear_terms_var = {}
        self._linear_terms_coef = {}
        self._nonlinear_expr = None
        self._nonlinear_vars = {}
        self._name_prefix = ""

    def clone(self):
        clone = ampl_representation()
        clone._constant = self._constant
        clone._linear_terms_var = self._linear_terms_var
        clone._linear_terms_coef = self._linear_terms_coef
        clone._nonlinear_expr = self._nonlinear_expr
        clone._nonlinear_vars = self._nonlinear_vars
        return clone

    def __eq__(self, other):
        # Can only be equal to other ampl_representation instances
        if not isinstance(other, ampl_representation):
            return False
        
        # Immediately check constants
        if self._constant != other._constant:
            return False

        # Optimization: check linear term lengths before iterating
        if len(self._linear_terms_var) != len(other._linear_terms_var):
            return False

        # Establish a mapping between self's linear terms and other's
        linear_var_indices = {}
        for i in self._linear_terms_var:
            for j in other._linear_terms_var:
                if self._linear_terms_var[i] is other._linear_terms_var[j]:
                    linear_var_indices[i] = j

        # We have to have found all our own vars
        if len(linear_var_indices) != len(self._linear_terms_var):
            return False

        # Check that linear term coefficients are equal
        for i in self._linear_terms_var:
            if self._linear_terms_coef[i] != other._linear_terms_coef[linear_var_indices[i]]:
                return False

        if self._nonlinear_expr is not None:
            if other._nonlinear_expr is None:
                return False

            if type(self._nonlinear_expr) is list:
                if type(other._nonlinear_expr) is not list:
                    return False

                # Check that nonlinear expressions are the same length
                if len(self._nonlinear_expr) != len(other._nonlinear_expr):
                    return False

                # Check that nonlinear expression have the same terms
                for i in xrange(len(self._nonlinear_expr)):
                    if self._nonlinear_expr[i][0] != other._nonlinear_expr[i][0]:
                        return False
                    if not self._nonlinear_expr[i][1] is other._nonlinear_expr[i][1]:
                        return False
            else:
                if not self._nonlinear_expr is other._nonlinear_expr:
                    return False

        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def is_constant(self):
        if len(self._linear_terms_var) == 0 and self._nonlinear_expr is None:
            return True
        return False

    def is_linear(self):
        if self._nonlinear_expr is None:
            return True

    def is_nonlinear(self):
        if self._nonlinear_expr is None:
            return False
        return True

    def needs_sum(self):
        num_components = 0
        if self._constant != 0:
            num_components += 1

        num_components += len(self._linear_terms_var)

        if not self._nonlinear_expr is None:
            num_components += 1

        if num_components > 1:
            return True
        return False

    def create_expr(self):
        if self.needs_sum() is True:
            ret_expr = expr._SumExpression()
            if self.is_constant():
                ret_expr._const = self._constant

            for (var_name, var) in self._linear_terms_var.iteritems():
                ret_expr.add(self._linear_terms_coef[var_name], var)

            if self.is_nonlinear():
                ret_expr.add(1.0, self._nonlinear_expr)

            return ret_expr
        else:
            # we know there is only one component present in ampl_repn
            if self.is_constant():
                return as_numeric(self._constant)
            elif self.is_nonlinear():
                return self._nonlinear_expr
            else:
                assert( len(self._linear_terms_var) == 1 )
                return self._linear_terms_var[self._linear_terms_var.keys()[0]]


def generate_ampl_repn(exp, symbol_map, labeler):
    ampl_repn = ampl_representation()
    #
    # Variable
    #
    if isinstance(exp, _VarData):
        if exp.fixed:
            ampl_repn._constant = exp.value
            return ampl_repn
        use_name = symbol_map.getSymbol( exp, labeler )
        ampl_repn._name_prefix = use_name[:len(use_name)-len(exp.name)]
        ampl_repn._linear_terms_coef[use_name] = 1.0
        ampl_repn._linear_terms_var[use_name] = exp
        return ampl_repn

    #
    # Expression
    #
    if isinstance(exp,expr.Expression):
        exp_type = type(exp)

        #
        # Sum
        #
        if exp_type is expr._SumExpression:
            ampl_repn._constant = exp._const #float(exp._const)
            ampl_repn._nonlinear_expr = None
            for i in xrange(len(exp._args)):
                exp_coef = exp._coef[i]
                child_repn = generate_ampl_repn(exp._args[i], symbol_map, labeler)
                if ampl_repn._name_prefix == "":
                    ampl_repn._name_prefix = child_repn._name_prefix
                # adjust the constant
                ampl_repn._constant += exp_coef*child_repn._constant

                # adjust the linear terms
                for (var_name,var) in child_repn._linear_terms_var.iteritems():
                    if var_name in ampl_repn._linear_terms_var:
                        ampl_repn._linear_terms_coef[var_name] += exp_coef*child_repn._linear_terms_coef[var_name]
                    else:
                        ampl_repn._linear_terms_var[var_name] = var
                        ampl_repn._linear_terms_coef[var_name] = exp_coef*child_repn._linear_terms_coef[var_name]

                # adjust the nonlinear terms
                if not child_repn._nonlinear_expr is None:
                    if ampl_repn._nonlinear_expr is None:
                        ampl_repn._nonlinear_expr = [(exp_coef, child_repn._nonlinear_expr)]
                    else:
                        ampl_repn._nonlinear_expr.append((exp_coef, child_repn._nonlinear_expr))

                # adjust the nonlinear vars
                ampl_repn._nonlinear_vars.update(child_repn._nonlinear_vars)
            return ampl_repn

        #
        # Product
        #
        elif exp_type is expr._ProductExpression:
            #
            # Iterate through the denominator.  If they aren't all constants, then
            # simply return this expresion.
            #
            denom=1.0
            for e in exp._denominator:
                if e.fixed_value():
                    denom *= e.value
                elif e.is_constant():
                    denom *= e()
                else:
                    ampl_repn._nonlinear_expr = exp
                    break
                if denom == 0.0:
                    print "Divide-by-zero error - offending sub-expression:"
                    e.pprint()
                    raise ZeroDivisionError

            if not ampl_repn._nonlinear_expr is None:
                # we have a nonlinear expression ... build up all the vars
                for e in exp._denominator:
                    arg_repn = generate_ampl_repn(e, symbol_map, labeler)
                    ampl_repn._nonlinear_vars.update(arg_repn._linear_terms_var)
                    ampl_repn._nonlinear_vars.update(arg_repn._nonlinear_vars)

                for e in exp._numerator:
                    arg_repn = generate_ampl_repn(e, symbol_map, labeler)
                    ampl_repn._nonlinear_vars.update(arg_repn._linear_terms_var)
                    ampl_repn._nonlinear_vars.update(arg_repn._nonlinear_vars)
                if ampl_repn._name_prefix == "":
                    ampl_repn._name_prefix = arg_repn._name_prefix
                return ampl_repn

            #
            # OK, the denominator is a constant.
            #
            # build up the ampl_repns for the numerator
            n_linear_args = 0
            n_nonlinear_args = 0
            arg_repns = list()
            for i in xrange(len(exp._numerator)):
                e = exp._numerator[i]
                e_repn = generate_ampl_repn(e, symbol_map, labeler)
                arg_repns.append(e_repn)
                # check if the expression is not nonlinear else it is nonlinear
                if not e_repn._nonlinear_expr is None:
                    n_nonlinear_args += 1
                # Check whether the expression is constant or else it is linear
                elif not ((len(e_repn._linear_terms_var) == 0) and (e_repn._nonlinear_expr is None)):
                    n_linear_args += 1

            is_nonlinear = False
            if n_linear_args > 1 or n_nonlinear_args > 0:
                is_nonlinear = True


            if is_nonlinear is True:
                # do like AMPL and simply return the expression
                # without extracting the potentially linear part
                ampl_repn = ampl_representation()
                ampl_repn._nonlinear_expr = exp
                for repn in arg_repns:
                    ampl_repn._nonlinear_vars.update(repn._linear_terms_var)
                    ampl_repn._nonlinear_vars.update(repn._nonlinear_vars)
                if ampl_repn._name_prefix == "":
                    ampl_repn._name_prefix = repn._name_prefix
                return ampl_repn

            else: # is linear or constant
                ampl_repn = current_repn = arg_repns[0]
                for i in xrange(1,len(arg_repns)):
                    e_repn = arg_repns[i]
                    ampl_repn = ampl_representation()

                    # const_c * const_e
                    ampl_repn._constant = current_repn._constant * e_repn._constant

                    # const_e * L_c
                    if e_repn._constant != 0.0:
                        for (var_name, var) in current_repn._linear_terms_var.iteritems():
                            ampl_repn._linear_terms_coef[var_name] = current_repn._linear_terms_coef[var_name] * e_repn._constant
                            ampl_repn._linear_terms_var[var_name] = var

                    # const_c * L_e
                    if current_repn._constant != 0.0:
                        for (e_var_name,e_var) in e_repn._linear_terms_var.iteritems():
                            if e_var_name in ampl_repn._linear_terms_var:
                                ampl_repn._linear_terms_coef[e_var_name] += current_repn._constant * e_repn._linear_terms_coef[e_var_name]
                            else:
                                ampl_repn._linear_terms_coef[e_var_name] = current_repn._constant * e_repn._linear_terms_coef[e_var_name]
                                ampl_repn._linear_terms_var[e_var_name] = e_var
                    if ampl_repn._name_prefix == "":
                        ampl_repn._name_prefix = e_repn._name_prefix
                    current_repn = ampl_repn

            # now deal with the product expression's coefficient that needs
            # to be applied to all parts of the ampl_repn
            ampl_repn._constant *= exp.coef/denom
            for var_name in ampl_repn._linear_terms_coef:
                ampl_repn._linear_terms_coef[var_name] *= exp.coef/denom

            return ampl_repn

        #
        # Power Expressions
        #
        elif exp_type is expr._PowExpression:
            assert(len(exp._args) == 2)
            base_repn = generate_ampl_repn(exp._args[0], symbol_map, labeler)
            exponent_repn = generate_ampl_repn(exp._args[1], symbol_map, labeler)

            if base_repn.is_constant() and exponent_repn.is_constant():
                ampl_repn._constant = base_repn._constant**exponent_repn._constant
            elif exponent_repn.is_constant() and exponent_repn._constant == 1.0:
                ampl_repn = base_repn
            elif exponent_repn.is_constant() and exponent_repn._constant == 0.0:
                ampl_repn._constant = 1.0
            else:
                # instead, let's just return the expression we are given and only
                # use the ampl_repn for the vars
                ampl_repn._nonlinear_expr = exp
                ampl_repn._nonlinear_vars = base_repn._nonlinear_vars
                ampl_repn._nonlinear_vars.update(exponent_repn._nonlinear_vars)
                ampl_repn._nonlinear_vars.update(base_repn._linear_terms_var)
                ampl_repn._nonlinear_vars.update(exponent_repn._linear_terms_var)
            if ampl_repn._name_prefix == "":
                if len(base_repn._name_prefix) > len(exponent_repn._name_prefix):
                    ampl_repn._name_prefix = base_repn._name_prefix
                else:
                    ampl_repn._name_prefix = exponent_repn._name_prefix
            return ampl_repn

        #
        # Intrinsic Functions
        #
        elif exp_type is expr._IntrinsicFunctionExpression:
            assert(len(exp._args) == 1)

            # this is inefficient since it is using much more than what we need
            child_repn = generate_ampl_repn(exp._args[0], symbol_map, labeler)

            ampl_repn._nonlinear_expr = exp
            ampl_repn._nonlinear_vars = child_repn._nonlinear_vars
            ampl_repn._nonlinear_vars.update(child_repn._linear_terms_var)
            if ampl_repn._name_prefix == "":
                ampl_repn._name_prefix = child_repn._name_prefix
            return ampl_repn
        #
        # ERROR
        #
        else:
            raise ValueError, "Unsupported expression type: "+str(exp)
    #
    # Constant
    #
    elif exp.fixed_value():
        if (type(exp.value) != float):
            if (type(exp.value) != int):
               if (type(exp.value) != bool):                
                   ampl_repn = generate_ampl_repn(exp.value, symbol_map, labeler)
                   return ampl_repn
        ampl_repn._constant = exp.value #float(exp.value)
        return ampl_repn

    #
    # ERROR
    #
    else:
        raise ValueError, "Unexpected expression type: "+str(exp)



# Switch from Python to C generate_ampl_repn function when possible
try:
    py_generate_ampl_repn = generate_ampl_repn
    from cAmpl import generate_ampl_repn
except ImportError:
    del py_generate_ampl_repn

generate_ef_ampl_repn = generate_ampl_repn # legacy nam

# Alternative: import C implementation under another name for testing
#from cAmpl import generate_ampl_repn as cgar
#__all__.append('cgar')
