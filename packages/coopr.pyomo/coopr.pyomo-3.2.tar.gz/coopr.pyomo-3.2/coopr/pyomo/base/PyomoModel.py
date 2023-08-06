#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

__all__ = ['Model', 'ConcreteModel', 'AbstractModel']

import array
import copy
import logging
import re
import sys
import traceback
import weakref
try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

from plugin import *
from numvalue import *

import pyutilib.component.core
from pyutilib.math import *
from pyutilib.misc import quote_split, tuplize, Container, PauseGC

from coopr.opt import ProblemFormat, ResultsFormat, guess_format
from coopr.opt.base import SymbolMap
from coopr.opt.results import SolutionMap, SolverResults, Solution
from coopr.pyomo.base.var import _VarData, VarStatus, Var
from coopr.pyomo.base.constraint import _ConstraintData
from coopr.pyomo.base.set_types import *
import coopr.opt
from PyomoModelData import ModelData
from coopr.opt.results.container import MapContainer,UndefinedData

from block import Block
from sets import Set

try:
    from pympler.muppy import tracker
    pympler_available = True
except ImportError:
    pympler_available = False

logger = logging.getLogger('coopr.pyomo')

class Model(Block):
    """
    An optimization model.  By default, this defers construction of components
    until data is loaded.
    """

    pyutilib.component.core.alias("Model", 'Model objects can be used as a '  \
                                  'component of other models.')

    preprocessor_ep = pyutilib.component.core.ExtensionPoint(IPyomoPresolver)

    #
    # IMPT: The base Block __getstate__ and __setstate__ methods are fine - 
    #       this class owns no weakrefs or slots.
    #

    def __init__ ( self, name='unknown', _deprecate=True, **kwargs ):
        """Constructor"""
        if _deprecate:
            msg = "Using the 'Model' class is deprecated.  Please use the "    \
                  "'AbstractModel' class instead."
            logger.warning( msg )

        # NB: some folks (notably, the PySP EF generator will stick
        # sub-models (the scenario models) into a master model (the
        # binding instance), so life is infinitely easier if the Model
        # registers itself as a Block -- otherwise, we need to define
        # Block.all_blocks() to look for both Blocks and Models; which
        # creates a chicken & egg import problem (block.py needs the
        # definition of Model for all_blocks(), but PyomoModel.py needs
        # to import block.py so inheritance works!
        #
        #kwargs.setdefault('ctype',Model)
        Block.__init__(self, **kwargs)

        self.name=name
        self._preprocessors = ["simple_preprocessor"]
        #
        # Model statistics
        #
        self.statistics = Container()

    def nvariables(self):
        return self.statistics.number_of_variables

    #def variable(self, name):
    #    if isinstance(name,basestring):
    #        return self._label_var_map[name]
    #    else:
    #        return self._var[name-1]

    #def variables(self):
    #    return self._label_var_map

    def nconstraints(self):
        return self.statistics.number_of_constraints

    #def constraint(self, name):
    #    if isinstance(name,basestring):
    #        return self._label_constraint_map[name]
    #    else:
    #        return self._con[name-1]

    #def constraints(self):
    #    return self._label_constraint_map

    def nobjectives(self):
        return self.statistics.number_of_objectives

    #def objective(self, name):
    #    if isinstance(name,basestring):
    #        return self._label_objective_map[name]
    #    else:
    #        return self._obj[name-1]

    #def objectives(self):
    #    return self._label_objective_map

    #def num_used_variables(self):
    #    return len(self._var)

    def valid_problem_types(self):
        return [ProblemFormat.pyomo]

    def create(self, filename=None, name=None, namespace=None, namespaces=None, preprocess=True, simplify=None, profile_memory=0):
        """
        Create a concrete instance of this Model, possibly using data
        read in from a file.
        """

        if simplify is not None:
            print """
 WARNING: The 'simplify' argument to PyomoModel.create() has been deprecated.
      Please remove references from your code.
 """

        # if you have a concrete model, it's already constructed - passing in a
        # data file is a waste of time. the only reason one would call create()
        # on a concrete instance is to preprocess.
        if (self._defer_construction is False) and isinstance(filename,basestring) and filename is not None:
            name_to_print = self.name
            if name is not None:
                name_to_print = name
            msg = "The filename=%s will not be loaded - supplied as an argument to the create() method of a ConcreteModel instance with name=%s." % (filename, name)
            logger.warning(msg)
            
        if self._defer_construction:
            instance = self.clone()

            if namespaces is None:
                instance.load(filename, namespaces=[namespace], profile_memory=profile_memory)
            elif len(namespaces) == 0:
                instance.load(filename, namespaces=[None], profile_memory=profile_memory)
            else:
                instance.load(filename, namespaces=namespaces+[None], profile_memory=profile_memory)
        else:
            instance = self
            
        # FIXME: Logically, we should do the following, but if I do, it
        # breaks several set tests
        #
        #instance._defer_construction = False
        #instance._constructed = True

        if preprocess is True:

            if (pympler_available is True) and (profile_memory >= 2):
                memory_tracker = tracker.SummaryTracker()
                memory_tracker.create_summary()

            instance.preprocess()

            if (pympler_available is True) and (profile_memory >= 2):
                print "Objects created during instance preprocessing:"
                memory_tracker.print_diff()

        if not name is None:
            instance.name=name
        return instance

    def clone(self):
        """Create a copy of this model"""

        #for name in self.components:
        #    #print 'y',name
        #    #print 'z', type(self.components[name])
        #    self.components[name]._model = None
        self._model = None
        for block in self.all_blocks():
            for compMap in block.components.components().itervalues():
                for comp in compMap.itervalues():
                    comp._parent = None

        # Monkey-patch for deepcopying weakrefs
        # Only required on Python <= 2.6
        import sys
        if sys.version_info[0] == 2 and sys.version_info[1] <= 6:
            copy._copy_dispatch[weakref.ref] = copy._copy_immutable
            copy._deepcopy_dispatch[weakref.ref] = copy._deepcopy_atomic
            copy._deepcopy_dispatch[weakref.KeyedRef] = copy._deepcopy_atomic

            def dcwvd(self, memo):
                """Deepcopy implementation for WeakValueDictionary class"""
                from copy import deepcopy
                new = self.__class__()
                for key, wr in self.data.items():
                    o = wr()
                    if o is not None:
                        new[deepcopy(key, memo)] = o
                return new
            weakref.WeakValueDictionary.__copy__ = weakref.WeakValueDictionary.copy
            weakref.WeakValueDictionary.__deepcopy__ = dcwvd

            def dcwkd(self, memo):
                """Deepcopy implementation for WeakKeyDictionary class"""
                from copy import deepcopy
                new = self.__class__()
                for key, value in self.data.items():
                    o = key()
                    if o is not none:
                        new[o] = deepcopy(value, memo)
                return new
            weakref.WeakKeyDictionary.__copy__ = weakref.WeakKeyDictionary.copy
            weakref.WeakKeyDictionary.__deepcopy__ = dcwkd

        # Actually do the copy
        instance = copy.deepcopy(self)
        #for name in self.components:
        #    self._model = weakref.ref(self)
        #    self.components[name]._model = weakref.ref(self)
        #for name in instance.components:
        #    instance._model = weakref.ref(instance)
        #    instance.components[name]._model = weakref.ref(instance)
        self._model = weakref.ref(self)
        instance._model = weakref.ref(instance)
        for block in self.all_blocks():
            for compMap in block.components.components().itervalues():
                for comp in compMap.itervalues():
                    comp._parent = weakref.ref(block)
        for block in instance.all_blocks():
            for compMap in block.components.components().itervalues():
                for comp in compMap.itervalues():
                    comp._parent = weakref.ref(block)
        return instance

    def reset(self):
        for name in self.components:
            self.components[name].reset()

    def preprocess(self):
        """Apply the preprocess plugins defined by the user"""
        suspend_gc = PauseGC()
        for item in self._preprocessors:
            self = Model.preprocessor_ep.service(item).preprocess(self)

    def solution(selfNone):
        """Return the solution"""
        soln = []
        for i in range(len(self._var)):
            soln.append( self._var[i].value )
        return soln

    # this method is a hack, used strictly by the pyomo command-line utility to
    # allow for user-readable names to be present in solver results objects.
    # this should be removed in the very near future, when labels are isolated
    # completely to solver plugins. in that situation, only human-readable
    # names will be present in a SolverResults object, and this method can
    # be removed.
    #
    # WEH - I think we need this method, even if the labeling method changes.
    #
    # The var/con/obj data is ordered by variable name, sorted by index.
    # This may differ from the declaration order, as well as the
    # instance order.  I haven't figured out how to efficiently generate
    # the declaration order.
    #
    # JDS - I think I agree with JP that this is no longer necessary
    #
    def update_results(self, results):

        results_symbol_map = results._symbol_map
        same_instance = results_symbol_map is not None and \
            results_symbol_map.instance is self

        new_results = SolverResults()
        new_results.problem = results.problem
        new_results.solver = results.solver

        for i in xrange(len(results.solution)):

            input_soln = results.solution(i+1)
            input_soln_variable = input_soln.variable
            input_soln_constraint = input_soln.constraint

            new_soln = Solution()
            new_soln.gap = input_soln.gap
            new_soln.status = input_soln.status
            #
            # Variables
            #
            vars = OrderedDict()
            tmp = {}
            for label, entry in input_soln_variable.iteritems():
                # NOTE: the following is a hack, to handle the ONE_VAR_CONSTANT variable
                if label == "ONE_VAR_CONSTANT":
                    continue
                # translate the label first if there is a symbol map
                # associated with the input solution.
                if same_instance:
                    var_value = results_symbol_map.getObject(label)
                elif results_symbol_map is not None:
                    var_value = results_symbol_map.getEquivalentObject(label, self)
                else:
                    raise RuntimeError("Cannot update from results missing a symbol map")

                if var_value is SymbolMap.UnknownSymbol:
                    msg = "Variable with label '%s' is not in model '%s'."
                    raise KeyError, msg % ( label, self.name, )

                if var_value.index.__class__ is tuple:
                    tmp[(var_value.component().name,)+var_value.index] = (var_value.name, entry)
                else:
                    tmp[(var_value.component().name,var_value.index)] = (var_value.name, entry)
                #vars[var_value.name] = entry
            for key in sorted(tmp.keys()):
                value = tmp[key]
                vars[value[0]] = value[1]
            new_soln.variable = vars
            #
            # Constraints
            #
            tmp = {}
            for label, entry in input_soln_constraint.iteritems():
                # NOTE: the following is a hack, to handle the ONE_VAR_CONSTANT variable
                if label == "c_e_ONE_VAR_CONSTANT":
                    continue
                if same_instance:
                    con_value = results_symbol_map.getObject(label)
                elif results_symbol_map is not None:
                    con_value = results_symbol_map.getEquivalentObject(label, self)
                else:
                    raise RuntimeError("Cannot update from results missing a symbol map")

                if con_value is SymbolMap.UnknownSymbol:
                    msg = "Constraint with label '%s' is not in model '%s'."
                    raise KeyError, msg % ( label, self.name, )

                if con_value.index.__class__ is tuple:
                    tmp[(con_value.component().name,)+con_value.index] = (con_value.name, entry)
                else:
                    tmp[(con_value.component().name,con_value.index)] = (con_value.name, entry)
            for key in sorted(tmp.keys()):
                value = tmp[key]
                new_soln.constraint.declare(value[0])
                dict.__setitem__(new_soln.constraint, value[0], value[1])
            #
            # Objectives
            #
            tmp = {}
            for label in input_soln.objective.keys():
                if same_instance:
                    obj_value = results_symbol_map.getObject(label)
                elif results_symbol_map is not None:
                    obj_value = results_symbol_map.getEquivalentObject(label, self)
                else:
                    raise RuntimeError("Cannot update from results missing a symbol map")

                if obj_value is SymbolMap.UnknownSymbol:
                    msg = "Objective with label '%s' is not in model '%s'."
                    raise KeyError, msg % ( label, self.name, )

                entry = input_soln.objective[label]
                if obj_value.index.__class__ is tuple:
                    tmp[(obj_value.component().name,)+obj_value.index] = (obj_value.name, entry)
                else:
                    tmp[(obj_value.component().name,obj_value.index)] = (obj_value.name, entry)
            for key in sorted(tmp.keys()):
                value = tmp[key]
                new_soln.objective.declare(value[0])
                dict.__setitem__(new_soln.objective, value[0], value[1])
            #
            new_results.solution.insert(new_soln)

        return new_results

    def load(self, arg, namespaces=[None], symbol_map=None,
             allow_consistent_values_for_fixed_vars=False,
             simplify=None, profile_memory=0, ignore_invalid_labels=False):
        """ Load the model with data from a file or a Solution object """

        if simplify is not None:
            print """
 WARNING: The 'simplify' argument to PyomoModel.load() has been deprecated.
      Please remove references from your code.
 """

        if arg is None or type(arg) is str:
            self._load_model_data(ModelData(filename=arg,model=self), namespaces, profile_memory=profile_memory)
            return True
        elif type(arg) is ModelData:
            self._load_model_data(arg, namespaces, profile_memory=profile_memory)
            return True
        elif type(arg) is coopr.opt.SolverResults:
            # if the solver status not one of either OK or Warning, then error.
            if (arg.solver.status != coopr.opt.SolverStatus.ok) and \
               (arg.solver.status != coopr.opt.SolverStatus.warning):

                if (arg.solver.status == coopr.opt.SolverStatus.aborted) and (len(arg.solution) > 0):
                   print "WARNING - Loading a SolverResults object with an 'aborted' status, but containing a solution"
                else:
                   msg = 'Cannot load a SolverResults object with bad status: %s'
                   raise ValueError, msg % str( arg.solver.status )

            # but if there is a warning, print out a warning, as someone should
            # probably take a look!
            if (arg.solver.status == coopr.opt.SolverStatus.warning):
                print 'WARNING - Loading a SolverResults object with a '       \
                      'warning status'

            if len(arg.solution) > 0:
                self._load_solution(
                    arg.solution(0),
                    symbol_map=arg.__dict__.get('_symbol_map', None),
                    allow_consistent_values_for_fixed_vars
                    = allow_consistent_values_for_fixed_vars,
                    ignore_invalid_labels=ignore_invalid_labels )
                return True
            else:
                return False
        elif type(arg) is coopr.opt.Solution:
            self._load_solution(
                arg,
                symbol_map=symbol_map,
                allow_consistent_values_for_fixed_vars
                = allow_consistent_values_for_fixed_vars,
                ignore_invalid_labels=ignore_invalid_labels )
            return True
        #elif type(arg) in (tuple, list):
        #    self._load_solution(
        #        arg,
        #        allow_consistent_values_for_fixed_vars
        #        = allow_consistent_values_for_fixed_vars,
        #        ignore_invalid_labels=ignore_invalid_labels )
        #    return True
        else:
            msg = "Cannot load model with object of type '%s'"
            raise ValueError, msg % str( type(arg) )

    def store_info(self, results):
        """ Store model information into a SolverResults object """
        results.problem.name = self.name

        stat_keys = (
          'number_of_variables',
          'number_of_binary_variables',
          'number_of_integer_variables',
          'number_of_continuous_variables',
          'number_of_constraints',
          'number_of_objectives'
        )

        for key in stat_keys:
            results.problem.__dict__[key] = self.statistics.__dict__[key]

    def _tuplize(self, data, setobj):
        if data is None:            #pragma:nocover
            return None
        if setobj.dimen == 1:
            return data
        ans = {}
        for key in data:
            if type(data[key][0]) is tuple:
                return data
            ans[key] = tuplize(data[key], setobj.dimen, setobj.name)
        return ans

    def _load_model_data(self, modeldata, namespaces, **kwds):
        """
        Load declarations from a ModelData object.
        """

        # As we are primarily generating objects here (and acyclic ones
        # at that), there is no need to run the GC until the entire
        # model is created.  Simple reference-counting should be
        # sufficient to keep memory use under control.
        suspend_gc = PauseGC()

        profile_memory = kwds.get('profile_memory', 0)

        # for pretty-printing summaries - unlike the standard
        # method in the pympler summary module, the tracker
        # doesn't print 0-byte entries to pad out the limit.
        if (pympler_available is True) and (profile_memory >= 2):
            memory_tracker = tracker.SummaryTracker()

        # Do some error checking
        for namespace in namespaces:
            if not namespace is None and not namespace in modeldata._data:
                msg = "Cannot access undefined namespace: '%s'"
                raise IOError, msg % namespace

        # Initialize each component in order.
        components = [key for key in self.components]

        for component_name in components:

            if (pympler_available is True) and (profile_memory >= 2):
                memory_tracker.create_summary()

            if self.components[component_name].type() is Model:
                continue
            elif self.components[component_name].type() is Var:
                var = self.components[component_name]
                if var._defer_domain:
                    domain_name = var.domain.name
                    var.domain = list(var.domain)
                    var.domain.sort()
                    if var.domain == []:
                        raise ValueError,"Attempting to set a variable's domain to an empty Set"
                    else:
                        if len(var.domain) != var.domain[-1] - var.domain[0] + 1:
                            raise ValueError,"Attempting to set a variable's domain to an improperly formatted Set " \
                                           + "-- elements are missing or duplicates exist: {0}".format(var.domain)
                        elif not all(type(elt) is int for elt in var.domain):
                            raise ValueError,"Attempting to set a veriable's domain to a Set with noninteger elements: {0}".format(var.domain)
                        else:
                            var.bounds = (var.domain[0],var.domain[-1])
                            var.domain = IntegerSet()
                            var.domain.name = domain_name
                            self.active_components(Var)[key] = var

            declaration = self.components[component_name]
            if component_name in modeldata._default.keys():
                if declaration.type() is Set:
                    declaration.set_default(self._tuplize(modeldata._default[component_name], declaration))
                else:
                    declaration.set_default(modeldata._default[component_name])
            data = None

            for namespace in namespaces:
                if component_name in modeldata._data.get(namespace,{}).keys():
                    if declaration.type() is Set:
                        data = self._tuplize(modeldata._data[namespace][component_name],
                                             declaration)
                    else:
                        data = modeldata._data[namespace][component_name]
                if not data is None:
                    break

            if __debug__:
                if logger.isEnabledFor(logging.DEBUG):
                    msg = "About to generate '%s' with data: %s"
                    print msg % ( declaration.name, str(data) )
                    self.pprint()

            try:
                declaration.construct(data)
            except:
                logger.error("constructing declaration '%s' from data=%s failed",
                             str(declaration.name), str(data).strip() )
                raise

            #print component_name, data # XXX

            if (pympler_available is True) and (profile_memory >= 2):
                print "Objects created during construction of component "+component_name+":"
                memory_tracker.print_diff()




    def _load_solution( self, soln, symbol_map,
                        allow_consistent_values_for_fixed_vars=False,
                        ignore_invalid_labels=False ):
        """
        Load a solution. A solution can be either a tuple or list, or a coopr.opt.Solution instance.
        - The allow_consistent_values_for_fixed_vars flag indicates whether a solution can specify
          consistent values for variables in the model that are fixed.
        - The ignore_invalid_labels flag indicates whether labels in the solution that don't
          appear in the model yield an error. This allows for loading a results object 
          generated from one model into another related, but not identical, model.
        """
        ## Load list or tuple into the variables, based on their order
        # NB: This is no longer supportable with the new SymbolMap 
        #if type(soln) in (tuple, list):
        #    if len(soln) != len(self._var):
        #        msg = 'Attempting to load a list/tuple solution into a ' \
        #              'model, but its length is %d while the model has %d ' \
        #              'variables' % (len(soln), len(self._var))
        #        raise ValueError, msg % ( len(soln), len(self._var) )
        #    for i in range(len(soln)):
        #        self._var[i].value = soln[i]
        #    return

        #
        # FIXME: JDS: Why doesn't this load the objective data?
        #

        if symbol_map is None:
            same_instance = False
        else:
            same_instance = symbol_map.instance is self
        #
        # Load variable data
        #
        for label, entry in soln.variable.iteritems():

            if same_instance:
                var_value = symbol_map.getObject(label)
            elif symbol_map is None:
                # We are going to assume the Solution was labeled with
                # the SolverResults pickler
                if 'canonical_label' in entry:
                    var_value = self.find_component(entry['canonical_label'])
                else:
                    # A last-ditch effort to resolve the object by the
                    # old lp-style labeling scheme
                    tmp = label
                    if tmp[-1] == ')': tmp = tmp[:-1]
                    tmp = tmp.replace('(',':').replace(')','.')
                    var_value = self.find_component(tmp)
            else:
                var_value = symbol_map.getEquivalentObject(label, self)

            if var_value is SymbolMap.UnknownSymbol:
                # NOTE: the following is a hack, to handle the ONE_VAR_CONSTANT
                #    variable that is necessary for the objective constant-offset
                #    terms.  probably should create a dummy variable in the model
                #    map at the same time the objective expression is being
                #    constructed.
                if label == "ONE_VAR_CONSTANT":
                    continue
                elif ignore_invalid_labels is True:
                    continue
                else:
                    raise KeyError("Variable label '%s' is not in model '%s'."
                                   % ( label, self.name, ))

            if not isinstance(var_value,_VarData):
                msg = "Variable '%s' in model '%s' is type %s"
                raise TypeError, msg % (
                    label, self.name, str(type(var_value)) )

            if (allow_consistent_values_for_fixed_vars is False) and (var_value.fixed is True):
                msg = "Variable '%s' in model '%s' is currently fixed - new" \
                      ' value is not expected in solution'
                raise TypeError, msg % ( label, self.name )

            #if var_value.status is not VarStatus.used:
            #    msg = "Variable '%s' in model '%s' is not currently used - no" \
            #          ' value is expected in solution'
            #    raise TypeError, msg % ( label, self.name )

            for attr_key, attr_value in entry.iteritems():
                if attr_key == 'Value':
                    if (allow_consistent_values_for_fixed_vars is True) and (var_value.fixed is True) and (attr_value != var_value.value):
                        msg = "Variable '%s' in model '%s' is currently fixed - a value of '%s' in solution is not identical to the current value of '%s'"
                        raise TypeError, msg % ( label, self.name, str(attr_value), str(var_value.value) )
                    var_value.value = attr_value
                elif attr_key != 'Id' and attr_key != 'canonical_label':
                    var_value.setattrvalue(attr_key, attr_value, define=True)
        #
        # Load constraint data
        #
        for label,entry in soln.constraint.iteritems():

            if same_instance:
                con_value = symbol_map.getObject(label)
            elif symbol_map is None:
                # We are going to assume the Solution was labeled with
                # the SolverResults pickler
                con_value = self.find_component(label)
            else:
                con_value = symbol_map.getEquivalentObject(label, self)

            if con_value is SymbolMap.UnknownSymbol:
                #
                # This is a hack - see above.
                #
                if label.endswith('ONE_VAR_CONSTANT'):
                    continue
                elif ignore_invalid_labels is True:
                    continue
                else:
                    raise KeyError("Constraint with label '%s' is not in model '%s'."
                                   % ( label, self.name, ))

            if not isinstance(con_value, _ConstraintData):
                raise TypeError("Constraint '%s' in model '%s' is type %s"
                                % ( label, self.name, str(type(con_value)) ))

            for _key in entry.iterkeys():
                key = _key[0].lower() + _key[1:]
                if key == 'value':
                    con_value.value = entry.value
                elif key != 'id' and key != 'canonical label':
                    setattr(con_value, key, getattr(entry, _key))

    def write(self, filename=None, format=ProblemFormat.cpxlp, solver_capability=None):
        """
        Write the model to a file, with a given format.
        """
        if format is None and not filename is None:
            #
            # Guess the format
            #
            format = guess_format(filename)
        #print "X",str(format),coopr.opt.WriterFactory.services()
        problem_writer = coopr.opt.WriterFactory(format)
        if problem_writer is None:
            msg = "Cannot write model in format '%s': no model writer "      \
                  "registered for that format"
            raise ValueError, msg % str(format)

        if solver_capability is None:
            solver_capability = lambda x: True
        (fname, symbol_map) = problem_writer(self, filename, solver_capability)
        if __debug__:
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug("Writing model '%s' to file '%s' with format %s", self.name, str(fname), str(format))
        return fname, symbol_map

    def to_standard_form(self):
        """
        Produces a standard-form representation of the model. Returns
        the coefficient matrix (A), the cost vector (c), and the
        constraint vector (b), where the 'standard form' problem is

        min/max c'x
        s.t.    Ax = b
                x >= 0

        All three returned values are instances of the array.array
        class, and store Python floats (C doubles).
        """

        from coopr.pyomo.expr import generate_canonical_repn


        # We first need to create an map of all variables to their column
        # number
        colID = {}
        ID2name = {}
        id = 0
        tmp = self.variables().keys()
        tmp.sort()

        for v in tmp:
            colID[v] = id
            ID2name[id] = v
            id += 1

        # First we go through the constraints and introduce slack and excess
        # variables to eliminate inequality constraints
        #
        # N.B. Structure heirarchy:
        #
        # active_components: {class: {attr_name: object}}
        # object -> Constraint: ._data: {ndx: _ConstraintData}
        # _ConstraintData: .lower, .body, .upper
        #
        # So, altogether, we access a lower bound via
        #
        # model.active_components()[Constraint]['con_name']['index'].lower
        #
        # {le,ge,eq}Constraints are
        # {constraint_name: {index: {variable_or_none: coefficient}} objects
        # that represent each constraint. None in the innermost dictionary
        # represents the constant term.
        #
        # i.e.
        #
        # min  x1 + 2*x2 +          x4
        # s.t. x1                         = 1
        #           x2   + 3*x3          <= -1
        #      x1 +                 x4   >= 3
        #      x1 + 2*x2 +      +   3*x4 >= 0
        #
        #
        # would be represented as (modulo the names of the variables,
        # constraints, and indices)
        #
        # eqConstraints = {'c1': {None: {'x1':1, None:-1}}}
        # leConstraints = {'c2': {None: {'x2':1, 'x3':3, None:1}}}
        # geConstraints = {'c3': {None: {'x1':1, 'x4':1, None:-3}},
        #                  'c4': {None: {'x1':1, 'x2':2, 'x4':1, None:0}}}
        #
        # Note the we have the luxury of dealing only with linear terms.
        var_id_map = {}
        leConstraints = {}
        geConstraints = {}
        eqConstraints = {}
        objectives = {}
        # For each registered component
        for c in self.active_components():

            # Get all subclasses of Constraint
            if issubclass(c, Constraint):
                cons = self.active_components(c)

                # Get the name of the constraint, and the constraint set itself
                for con_set_name in cons:
                    con_set = cons[con_set_name]

                    # For each indexed constraint in the constraint set
                    for ndx in con_set._data:
                        con = con_set._data[ndx]

                        # Process the body
                        terms = self._process_canonical_repn(
                            generate_canonical_repn(con.body, var_id_map))

                        # Process the bounds of the constraint
                        if con._equality:
                            # Equality constraint, only check lower bound
                            lb = self._process_canonical_repn(
                                generate_canonical_repn(con.lower, var_id_map))

                            # Update terms
                            for k in lb:
                                v = lb[k]
                                if k in terms:
                                    terms[k] -= v
                                else:
                                    terms[k] = -v

                            # Add constraint to equality constraints
                            eqConstraints[(con_set_name, ndx)] = terms
                        else:

                            # Process upper bounds (<= constraints)
                            if con.upper is not None:
                                # Less than or equal to constraint
                                tmp = dict(terms)

                                ub = self._process_canonical_repn(
                                    generate_canonical_repn(con.upper, var_id_map))

                                # Update terms
                                for k in ub:
                                    if k in terms:
                                        tmp[k] -= ub[k]
                                    else:
                                        tmp[k] = -ub[k]

                                # Add constraint to less than or equal to
                                # constraints
                                leConstraints[(con_set_name, ndx)] = tmp

                            # Process lower bounds (>= constraints)
                            if con.lower is not None:
                                # Less than or equal to constraint
                                tmp = dict(terms)

                                lb = self._process_canonical_repn(
                                    generate_canonical_repn(con.lower, var_id_map))

                                # Update terms
                                for k in lb:
                                    if k in terms:
                                        tmp[k] -= lb[k]
                                    else:
                                        tmp[k] = -lb[k]

                                # Add constraint to less than or equal to
                                # constraints
                                geConstraints[(con_set_name, ndx)] = tmp
            elif issubclass(c, Objective):
                # Process objectives
                objs = self.active_components(c)

                # Get the name of the objective, and the objective set itself
                for obj_set_name in objs:
                    obj_set = objs[obj_set_name]

                    # For each indexed objective in the objective set
                    for ndx in obj_set._data:
                        obj = obj_set._data[ndx]
                        # Process the objective
                        terms = self._process_canonical_repn(
                            generate_canonical_repn(obj.expr, var_id_map))

                        objectives[(obj_set_name, ndx)] = terms


        # We now have all the constraints. Add a slack variable for every
        # <= constraint and an excess variable for every >= constraint.
        nSlack = len(leConstraints)
        nExcess = len(geConstraints)

        nConstraints = len(leConstraints) + len(geConstraints) + \
                       len(eqConstraints)
        nVariables = len(colID) + nSlack + nExcess
        nRegVariables = len(colID)

        # Make the arrays
        coefficients = array.array("d", [0]*nConstraints*nVariables)
        constraints = array.array("d", [0]*nConstraints)
        costs = array.array("d", [0]*nVariables)

        # Populate the coefficient matrix
        constraintID = 0

        # Add less than or equal to constraints
        for ndx in leConstraints:
            con = leConstraints[ndx]
            for termKey in con:
                coef = con[termKey]

                if termKey is None:
                    # Constraint coefficient
                    constraints[constraintID] = -coef
                else:
                    # Variable coefficient
                    col = colID[termKey]
                    coefficients[constraintID*nVariables + col] = coef

            # Add the slack
            coefficients[constraintID*nVariables + nRegVariables + \
                        constraintID] = 1
            constraintID += 1

        # Add greater than or equal to constraints
        for ndx in geConstraints:
            con = geConstraints[ndx]
            for termKey in con:
                coef = con[termKey]

                if termKey is None:
                    # Constraint coefficient
                    constraints[constraintID] = -coef
                else:
                    # Variable coefficient
                    col = colID[termKey]
                    coefficients[constraintID*nVariables + col] = coef

            # Add the slack
            coefficients[constraintID*nVariables + nRegVariables + \
                        constraintID] = -1
            constraintID += 1

        # Add equality constraints
        for ndx in eqConstraints:
            con = eqConstraints[ndx]
            for termKey in con:
                coef = con[termKey]

                if termKey is None:
                    # Constraint coefficient
                    constraints[constraintID] = -coef
                else:
                    # Variable coefficient
                    col = colID[termKey]
                    coefficients[constraintID*nVariables + col] = coef

            constraintID += 1

        # Determine cost coefficients
        for obj_name in objectives:
            obj = objectives[obj_name]()
            for var in obj:
                costs[colID[var]] = obj[var]

        # Print the model
        #
        # The goal is to print
        #
        #         var1   var2   var3   ...
        #       +--                     --+
        #       | cost1  cost2  cost3  ...|
        #       +--                     --+
        #       +--                     --+ +-- --+
        # con1  | coef11 coef12 coef13 ...| | eq1 |
        # con2  | coef21 coef22 coef23 ...| | eq2 |
        # con2  | coef31 coef32 coef33 ...| | eq3 |
        #  .    |   .      .      .   .   | |  .  |
        #  .    |   .      .      .    .  | |  .  |
        #  .    |   .      .      .     . | |  .  |

        constraintPadding = 2
        numFmt = "% 1.4f"
        altFmt = "% 1.1g"
        maxColWidth = max(len(numFmt % 0.0), len(altFmt % 0.0))
        maxConstraintColWidth = max(len(numFmt % 0.0), len(altFmt % 0.0))

        # Generate constraint names
        maxConNameLen = 0
        conNames = []
        for name in leConstraints:
            strName = str(name)
            if len(strName) > maxConNameLen:
                maxConNameLen = len(strName)
            conNames.append(strName)
        for name in geConstraints:
            strName = str(name)
            if len(strName) > maxConNameLen:
                maxConNameLen = len(strName)
            conNames.append(strName)
        for name in eqConstraints:
            strName = str(name)
            if len(strName) > maxConNameLen:
                maxConNameLen = len(strName)
            conNames.append(strName)

        # Generate the variable names
        varNames = [None]*len(colID)
        for name in colID:
            tmp_name = " " + name
            if len(tmp_name) > maxColWidth:
                maxColWidth = len(tmp_name)
            varNames[colID[name]] = tmp_name
        for i in xrange(0, nSlack):
            tmp_name = " _slack_%i" % i
            if len(tmp_name) > maxColWidth:
                maxColWidth = len(tmp_name)
            varNames.append(tmp_name)
        for i in xrange(0, nExcess):
            tmp_name = " _excess_%i" % i
            if len(tmp_name) > maxColWidth:
                maxColWidth = len(tmp_name)
            varNames.append(tmp_name)

        # Variable names
        line = " "*maxConNameLen + (" "*constraintPadding) + " "
        for col in xrange(0, nVariables):
            # Format entry
            token = varNames[col]

            # Pad with trailing whitespace
            token += " "*(maxColWidth - len(token))

            # Add to line
            line += " " + token + " "
        print line

        # Cost vector
        print " "*maxConNameLen + (" "*constraintPadding) + "+--" + \
              " "*((maxColWidth+2)*nVariables - 4) + "--+"
        line = " "*maxConNameLen + (" "*constraintPadding) + "|"
        for col in xrange(0, nVariables):
            # Format entry
            token = numFmt % costs[col]
            if len(token) > maxColWidth:
                token = altFmt % costs[col]

            # Pad with trailing whitespace
            token += " "*(maxColWidth - len(token))

            # Add to line
            line += " " + token + " "
        line += "|"
        print line
        print " "*maxConNameLen + (" "*constraintPadding) + "+--" + \
              " "*((maxColWidth+2)*nVariables - 4) + "--+"

        # Constraints
        print " "*maxConNameLen + (" "*constraintPadding) + "+--" + \
              " "*((maxColWidth+2)*nVariables - 4) + "--+" + \
              (" "*constraintPadding) + "+--" + \
              (" "*(maxConstraintColWidth-1)) + "--+"
        for row in xrange(0, nConstraints):
            # Print constraint name
            line = conNames[row] + (" "*constraintPadding) + (" "*(maxConNameLen - len(conNames[row]))) + "|"

            # Print each coefficient
            for col in xrange(0, nVariables):
                # Format entry
                token = numFmt % coefficients[nVariables*row + col]
                if len(token) > maxColWidth:
                    token = altFmt % coefficients[nVariables*row + col]

                # Pad with trailing whitespace
                token += " "*(maxColWidth - len(token))

                # Add to line
                line += " " + token + " "

            line += "|" + (" "*constraintPadding) + "|"

            # Add constraint vector
            token = numFmt % constraints[row]
            if len(token) > maxConstraintColWidth:
                token = altFmt % constraints[row]

            # Pad with trailing whitespace
            token += " "*(maxConstraintColWidth - len(token))

            line += " " + token + "  |"
            print line
        print " "*maxConNameLen + (" "*constraintPadding) + "+--" + \
              " "*((maxColWidth+2)*nVariables - 4) + "--+" + \
              (" "*constraintPadding) + "+--" + (" "*(maxConstraintColWidth-1))\
              + "--+"

        return (coefficients, costs, constraints)

    def _process_canonical_repn(self, expr):
        """
        Returns a dictionary of {var_name_or_None: coef} values
        """

        terms = {}

        # Get the variables from the canonical representation
        vars = expr.pop(-1, {})

        # Find the linear terms
        linear = expr.pop(1, {})
        for k in linear:
            # FrozeDicts don't support (k, v)-style iteration
            v = linear[k]

            # There's exactly 1 variable in each term
            terms[vars[k.keys()[0]].label] = v

        # Get the constant term, if present
        const = expr.pop(0, {})
        if None in const:
            terms[None] = const[None]

        if len(expr) != 0:
            raise TypeError, "Nonlinear terms in expression"

        return terms


def _tempTrue(x):
    """
    Defined to return True to all inquiries
    """
    return True


class ConcreteModel(Model):
    """
    A concrete optimization model that does not defer construction of
    components.
    """

    def __init__(self, *args, **kwds):
        kwds['_deprecate'] = False
        Model.__init__(self, *args, **kwds)
        self._defer_construction=False

    pyutilib.component.core.alias("ConcreteModel", 'A concrete optimization model that '\
              'does not defer construction of components.')

class AbstractModel(Model):
    """
    An abstract optimization model that defers construction of
    components.
    """

    def __init__(self, *args, **kwds):
        kwds['_deprecate'] = False
        Model.__init__(self, *args, **kwds)
        self._defer_construction=True

    pyutilib.component.core.alias("AbstractModel", 'An abstract optimization model that '\
              'defers construction of components.')
