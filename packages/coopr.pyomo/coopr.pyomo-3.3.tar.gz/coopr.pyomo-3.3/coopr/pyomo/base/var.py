#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

__all__ = ['Var', 'VarList', '_VarData']

import logging
import types
import sys
import weakref

from pyutilib.component.core import alias
import pyutilib.math
import pyutilib.misc
from pyutilib.enum import Enum

from numvalue import NumericValue, value, as_numeric, is_fixed
from set_types import BooleanSet, IntegerSet, Reals
from component import Component
from indexed_component import IndexedComponent
from misc import apply_indexed_rule
from misc import create_name
from sets import Set, _SetContainer
from coopr.pyomo.base.util import isfunctor

logger = logging.getLogger('coopr.pyomo')

class _VarData(NumericValue):
    """
    This class defines the data for a single variable.

    Constructor Arguments:
        name        The name of this variable.  Use None for a default value.
        domain      The domain of this variable.  Use None for a default value.
        component   The Var object that owns this data.

    Public Class Attributes:
        active      If True, then this variable is active in the model.
        component   A weakref to the component object that owns this variable index.
        index       The index of this variable within the Var component.
        domain      The domain of this variable.
        fixed       If True, then this variable is treated as a fixed constant in the model.
        initial     The default initial value for this variable.
        lb          A lower bound for this variable.  The lower bound can be either 
                        numeric constants, parameter values, expressions or any object that 
                        can be called with no arguments.
        ub          A upper bound for this variable.  The upper bound can be either 
                        numeric constants, parameter values, expressions or any object that 
                        can be called with no arguments.
        name        A text string that provides an easy-to-read representation of the
                        variable/index pair (e.g. var[x,y,z])
        stale       A Boolean indicating whether the value of this variable is legitimiate -
                    or, in other words, if it should be considered legitimate for purposes 
                    of reporting or other interrogation. 
        value       The numeric value of this variable.
    """

    __slots__ = ['component','index','initial','active','lb','ub','fixed','stale']

    def __init__(self, name, domain, component):
        """
        Constructor
        """
        # The following three lines are equivalent to calling the
        # basic NumericValue constructor, i.e., as follows:
        # NumericValue.__init__(self, name, domain, None, False)
        self.name = name
        self.domain = domain
        self.value = None
        #
        self.active = True
        if component is None:
            self.component = None
        else:
            self.component = weakref.ref(component)
        self.fixed = False
        self.index = None
        self.initial = None
        # IMPT: The type of the lower and upper bound attributes can either be atomic numeric types
        #       in Python, expressions, etc. Basically, they can be anything that passes an "is_fixed" test.
        self.lb = None
        self.ub = None

        self.stale = True

    def __str__(self):
        """
        Return a string representation of the variable.  If the name attribute is None,
        then return ''
        """
        if self.name is None:
            return ""
        else:
            return self.name

    def __getstate__(self):
        """
        This method must be defined because this class uses slots.
        """
        result = NumericValue.__getstate__(self)
        for i in _VarData.__slots__:
            result[i] = getattr(self, i)
        if type(result['component']) is weakref.ref:
            result['component'] = result['component']()
        return result

    def __setstate__(self, state):
        """
        This method must be defined because this class uses slots.
        """
        result = NumericValue.__getstate__(self)
        for (slot_name, value) in state.iteritems():
            setattr(self, slot_name, value)
        if self.component is not None:
            self.component = weakref.ref(self.component)

    def get_suffix_value(self, suffix):
        return self.component().get_suffix_value(suffix, self.index)

    def set_suffix_value(self, suffix, value, define=False):
        self.component().set_suffix_value(suffix, value, self.index, define)

    def activate(self):
        self.active=True

    def deactivate(self):
        self.active=False

    def setlb(self, value):
        if value is None:
            self.lb = None
        else:
            if is_fixed(value):
                self.lb = value
            else:
                raise ValueError(
                    "Non-fixed input of type '%s' supplied as variable lower "
                    "bound - legal types must be fixed expressions or variables."
                    % (type(value),) )

    def setub(self, value):
        if value is None:
            self.ub = None
        else:
            if is_fixed(value):
                    self.ub = value
            else:
                raise ValueError(
                    "Non-fixed input of type '%s' supplied as variable upper "
                    "bound - legal types are fixed expressions or variables."
                    "parameters"
                    % (type(value),) )

    def is_fixed(self):
        if self.fixed:
            return True
        return False

    def is_constant(self):
        return False

    def polynomial_degree(self):
        if self.fixed:
            return 0
        return 1

    def is_binary(self):
        return self.component().is_binary(self.index)

    def is_integer(self):
        return self.component().is_integer(self.index)

    def is_continuous(self):
        return self.component().is_continuous(self.index)

    def pprint(self, ostream=None, verbose=False):
        if ostream is None:
            ostream = sys.stdout
        print >>ostream, str(self),

#
# Variable attributes:
#
# Single variable:
#
# x = Var()
# x.fixed = True
# x.domain = Reals
# x.name = "x"
# x.setlb(-1.0)
# x.setub(1.0)
# x.initial = 0.0
# x = -0.4
#
# Array of variables:
#
# y = Var(set1,set2,...,setn)
# y.fixed = True (fixes all variables)
# y.domain = Reals
# y.name = "y"
# y[i,j,...,k] (returns value of a given index)
#
# y[i,j,...,k].fixed
# y[i,j,...,k].lb()
# y[i,j,...,k].ub()
# y[i,j,...,k].initial
#

class Var(IndexedComponent):
    """A numeric variable, which may be defined over a index"""

    """
    Constructor Arguments:
        name        The name of this variable
        index       The index set that defines the distinct variables.
                        By default, this is None, indicating that there
                        is a single variable.
        domain      A set that defines the type of values that
                        each variable must be.
        default     A set that defines default values for this
                        variable.
        bounds      A rule for defining bounds values for this
                        variable.
        rule        A rule for setting up this variable with
                        existing model data
    """

    alias("Var", doc="Decision variables in a model.", subclass=True)

    def __new__(cls, *args, **kwds):
        if cls != Var:
            return super(Var, cls).__new__(cls)
        if args == ():
            return _VarElement.__new__(_VarElement)
        else:
            return _VarArray.__new__(_VarArray)

    def __init__(self, *args, **kwd):
        # Default keyword values
        self._initialize = kwd.pop('initialize', None )
        self.domain = kwd.pop('within', Reals )
        self.domain = kwd.pop('domain', self.domain )
        self.bounds = kwd.pop('bounds', None )

        self._defer_domain = False

        #Handle within=not_pyomo_object 
        if not getattr(self.domain, 'virtual', False):
            if self.domain == [] or self.domain == set([]):
                raise ValueError,"Attempting to set a variable's domain to an empty set"
            else: 
                from rangeset import RangeSet
                if type(self.domain) is RangeSet:
                    self.bounds = (self.domain._start,self.domain._end)
                    domain_name = self.domain.name
                    self.domain = IntegerSet()
                    self.domain.name = domain_name
                elif type(self.domain) is _SetContainer:
                    if self.domain.initialize is None:
                        self._defer_domain = True
                    elif self.domain.initialize == []:
                        raise ValueError,"Attempting to set a variable's domain to an empty Set"
                    else:
                        self._defer_domain = False
                        domain_name = self.domain.name
                        self.domain = self.domain.initialize
                        self.domain.sort()
                        if len(self.domain) != self.domain[-1] - self.domain[0] + 1:
                            raise ValueError,"Attempting to set a variable's domain to an improperly formatted Set " \
                                           + "-- elements are missing or duplicates exist: {0}".format(self.domain)
                        elif not all(type(elt) is int for elt in self.domain):
                            raise ValueError,"Attempting to set a veriable's domain to a Set with noninteger elements: {0}".format(self.domain)
                        else:
                            self.bounds = (self.domain[0],self.domain[-1])
                            self.domain = IntegerSet()
                            self.domain.name = domain_name
                elif type(self.domain) is list:
                    self.domain.sort()
                    if len(self.domain) != self.domain[-1] - self.domain[0] + 1:
                        raise ValueError,"Attempting to set a variable's domain to an improperly formatted set " \
                                       + "-- elements are missing or duplicates exist: {0}".format(self.domain)
                    elif not all(type(elt) is int for elt in self.domain):
                        raise ValueError,"Attempting to set a veriable's domain to a set with noninteger elements: {0}".format(self.domain)
                    else:
                        self.bounds = (self.domain[0],self.domain[-1])
                        domain_name = "[{0}..{1}]".format(self.domain[0],self.domain[-1])
                        self.domain = IntegerSet()
                        self.domain.name = domain_name
                elif type(self.domain) is set:
                    self.domain = list(self.domain) 
                    self.domain.sort()
                    if len(self.domain) != self.domain[-1] - self.domain[0] + 1:
                        raise ValueError,"Attempting to set a variable's domain to an improperly formatted set " \
                                       + "-- elements are missing or duplicates exist: {0}".format(self.domain)
                    elif not all(type(elt) is int for elt in self.domain):
                        raise ValueError,"Attempting to set a veriable's domain to a set with noninteger elements: {0}".format(self.domain)
                    else:
                        self.bounds = (self.domain[0],self.domain[-1])
                        domain_name = "[{0}..{1}]".format(self.domain[0],self.domain[-1])
                        self.domain = IntegerSet()
                        self.domain.name = domain_name
                elif type(self.domain) is xrange:
                    self.bounds = (self.domain[0],self.domain[-1])
                    domain_name = "[{0}..{1}]".format(self.bounds[0],self.bounds[-1])
                    self.domain = IntegerSet()
                    self.domain.name = domain_name

        kwd.setdefault('ctype', Var)

        IndexedComponent.__init__(self, *args, **kwd)

        # check to see if domains for individual _VarData objects are specified via a rule.
        if isfunctor(self.domain):
            self._domain_rule = self.domain
            self.domain = None # there is no general domain for the collection of variables.
        else:
            self._domain_rule = None # there is no domain rule!

        # cached for efficiency purposes - isinstance is not cheap. 
        # only truly valid if there is no domain rule specified.
        if self.domain is not None:
            self._is_binary = isinstance(self.domain, BooleanSet)
            # second case is required in the case of deferred domains (the set may not be constructed yet, so hasn't been translated to an IntegerSet)
            self._is_integer = isinstance(self.domain, IntegerSet) or (type(self.domain) is _SetContainer)
            self._is_continuous = not (self._is_binary or self._is_integer)
        else:
            self._is_binary = None
            self._is_integer = None
            self._is_continuous = None

        # the following are only applicable if a domain rule *has* been specified.
        self._binary_keys = []
        self._integer_keys = []
        self._continuous_keys = []

    def as_numeric(self):
        if None in self._data:
            return self._data[None]
        return self

    def is_indexed(self):
        return self._ndim > 0

    def is_expression(self):
        return False

    def is_relational(self):
        return False

    def keys(self):
        return self._data.keys()

    # sets the "stale" attribute of every var index to True.
    def flag_as_stale(self):
        for index, var_data in self._data.iteritems():
            var_data.stale = True

    # returns a dictionary of index-value pairs.
    def extract_values(self):
        return dict(((index, varval.value) for index, varval in self._data.iteritems()))

    # takes as input a dictionary of index-value pairs.
    def store_values(self, new_values):
        for index, varval in self._data.iteritems():
            varval.value = new_values[index]
            varval.stale = False

    def is_binary(self, index):
        if self._domain_rule is None:
            return self._is_binary
        else:
            return index in self._binary_keys

    def is_integer(self, index):
        if self._domain_rule is None:
            return self._is_integer
        else:
            return index in self._integer_keys

    def is_continuous(self, index):
        if self._domain_rule is None:
            return self._is_continuous
        else:
            return index in self._continuous_keys

    def binary_keys(self):
        """ Returns the keys of all binary variables """
        if self._domain_rule is None:
            if self._is_binary:
                return self._data.keys()
            else:
                return []
        else:
            return self._binary_keys

    def integer_keys(self):
        """ Returns the keys of all integer variables """
        if self._domain_rule is None:
            if self._is_integer:
                return self._data.keys()
            else:
                return []
        else:
            return self._integer_keys

    def continuous_keys(self):
        """ Returns the keys of all continuous variables """
        if self._domain_rule is None:
            if self._is_continuous:
                return self._data.keys()
            else:
                return []
        else:
            return self._continuous_keys

    def __iter__(self):
        return self._data.iterkeys()

    def iterkeys(self):
        return self._data.iterkeys()

    def itervalues(self):
        return self._data.itervalues()

    def iteritems(self):
        return self._data.iteritems()

    def __contains__(self, ndx):
        return ndx in self._data

    def dim(self):
        return self._ndim

    def reset(self):
        for value in self._data.itervalues():
            value.set_value(value.initial)

    def __len__(self):
        return len(self._data)

    def __setitem__(self,ndx,val):
        #print "HERE",ndx,val, self._valid_value(val,False), self.domain # XXX debugging
        if (len(self._index) == 1) and (None in self._index) and (ndx is not None): # a somewhat gory way to see if you have a singleton - the len()=1 check is needed to avoid "None" being passed illegally into set membership validation rules.
            # allow for None indexing if this is truly a singleton
            msg = "Cannot set an array value in singleton variable '%s'"
            raise KeyError, msg % self.name

        if ndx not in self._index:
            msg = "Cannot set the value of array variable '%s' with invalid " \
                  "index '%s'"
            raise KeyError, msg % ( self.name, str(ndx) )

        if not self._valid_value(val,False):
            msg = "Cannot set variable '%s[%s]' with invalid value: %s"
            raise ValueError, msg % ( self.name, str(ndx), str(val) )
        self._data[ndx].value = val
        self._data[ndx].stale = False

    def __getitem__(self,ndx):
        """This method returns a _VarData object.  This object can be
           coerced to a numeric value using the value() function, or using
           explicity coercion with float().
        """
        try:
            return self._data[ndx]
        except KeyError: # thrown if the supplied index is hashable, but not defined.
            msg = "Unknown index '%s' in variable %s;" % (str(ndx), self.name)
            if (isinstance(ndx, (tuple, list)) and len(ndx) != self.dim()):
                msg += "    Expecting %i-dimensional indices" % self.dim()
            else:
                msg += "    Make sure the correct index sets were used.\n"
                msg += "    Is the ordering of the indices correct?"
            raise KeyError, msg
        except TypeError, msg: # thrown if the supplied index is not hashable
            msg2 = "Unable to index variable %s using supplied index with " % self.name
            msg2 += str(msg)
            raise TypeError, msg2

    def _add_indexed_member(self, ndx):
        # Check for domain rules
        if self._domain_rule is not None:
            domain = apply_indexed_rule( self, self._domain_rule,
                                         self._parent(), ndx )
            if isinstance(domain, BooleanSet):
                self._binary_keys.append(ndx)
            elif isinstance(domain, IntegerSet):
                self._integer_keys.append(ndx)
            else:
                self._continuous_keys.append(ndx)
        else:
            domain = self.domain

        new_data = _VarData(create_name(self.name,ndx), domain, self)
        new_data.index = ndx
        
        self._data[ndx] = new_data


    def construct(self, data=None):
        if __debug__:   #pragma:nocover
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug("Constructing Variable, name=%s, from data=%s", self.name, `data`)
        if self._constructed:
            return
        self._constructed=True
        #
        # Construct _VarData objects for all index values
        #
        if self._ndim > 0:
            
            if type(self._initialize) is dict:
                self._index = self._initialize.keys()

            for ndx in self._index:
                # Ignore a None index.  This occurs when an empty VarList is
                # created;  the empty implicit set has the None index.
                if ndx is not None: 
                    self._add_indexed_member(ndx)


        #
        # Define the _XXX_keys objects if domain isn't a rule;
        # they were defined individually above in the case of
        # a rule
        #
        if self._domain_rule is None:
            if isinstance(self.domain, BooleanSet):
                self._binary_keys = self._data.keys()
            elif isinstance(self.domain, IntegerSet):
                self._integer_keys = self._data.keys()
            else:
                self._continuous_keys = self._data.keys()

        #
        # Initialize values with a dictionary if provided
        #
        if self._initialize is not None:
            #
            # Initialize values with the _rule function if provided
            #
            if self._initialize.__class__ is types.FunctionType:
                for key in self._data:
                    if key is None:
                        val = self._initialize(self._parent())
                    else:
                        val = apply_indexed_rule( self, self._initialize,
                                                  self._parent(), key )
                    val = value(val)
                    self._valid_value(val, True)
                    self._data[key].value = self._data[key].initial = val
                    self._data[key].stale = False
            elif self._initialize.__class__ is dict:
                for key in self._initialize:
                    val = self._initialize[key]
                    self._valid_value(val, True)
                    self._data[key].value = self._data[key].initial = val
                    self._data[key].stale = False                    
            else:
                for key in self._index:
                    val = self._initialize
                    self._valid_value(val, True)
                    self._data[key].value = self._data[key].initial = val
                    self._data[key].stale = False                    
        #
        # Initialize bounds with the bounds function if provided
        #
        if self.bounds is not None:

            if type(self.bounds) is tuple:

                # bounds are specified via a tuple - same lower and upper bounds for all var values!

                (lb, ub) = self.bounds

                # do some simple validation that the bounds are actually finite - otherwise, set them to None.
                if (lb is not None) and (not pyutilib.math.is_finite(value(lb))):
                    lb = None
                if (ub is not None) and (not pyutilib.math.is_finite(value(ub))):
                    ub = None

                for key,varval in self._data.iteritems():
                    if lb is not None:
                        varval.setlb(lb)
                    if ub is not None:
                        varval.setub(ub)

            else:

                # bounds are specified via a function

                for index, varval in self._data.iteritems():
                    if index is None:
                        (lb, ub) = self.bounds(self._parent())
                    else:
                        (lb, ub) = apply_indexed_rule( self, self.bounds,
                                                       self._parent(), index )
                    varval.setlb(lb)
                    varval.setub(ub)

                for varval in self._data.itervalues():
                    if varval.lb is not None and not pyutilib.math.is_finite(value(varval.lb)):
                        varval.setlb(None)
                    if varval.ub is not None and not pyutilib.math.is_finite(value(varval.ub)):
                        varval.setub(None)
        #
        # Iterate through all variables, and tighten the bounds based on
        # the domain bounds information.
        #
        # Only done if self.domain is not a rule. If it is, _VarArray level
        # bounds become meaningless, since the individual _VarElement objects
        # likely have more restricted domains.
        #
        if self._domain_rule is None:
            dbounds = self.domain.bounds()
            if not dbounds is None and dbounds != (None,None):
                for varval in self._data.itervalues():
                    if not dbounds[0] is None:
                        if varval.lb is None or                     \
                           dbounds[0] > value(varval.lb):
                            varval.setlb(dbounds[0])

                    if not dbounds[1] is None:
                        if varval.ub is None or                     \
                            dbounds[1] < value(varval.ub):
                            varval.setub(dbounds[1])
        #
        # Setup declared attributes for all variables
        #
        for suffix in self._suffix_declaration:
            self._suffix_value[suffix] = {}

    def fix_all(self):
        for key in self:
            self[key].fixed = True

    def unfix_all(self):
        for key in self:
            self[key].fixed = False


    def pprint(self, ostream=None, verbose=False):
        if ostream is None:
            ostream = sys.stdout
        print >>ostream, "  ",self.name,":",
        if not self.doc is None:
            print >>ostream, self.doc
            print >>ostream, "  ",
        print >>ostream, "\tSize="+str(len(self)),
        if self.domain is not None:
            print >>ostream, "\tDomain="+self.domain.name
        else:
            print >>ostream, "\tDomain=None"
        if self._index_set is not None:
            print >>ostream, "\tIndicies: ",
            for idx in self._index_set:
                print >>ostream, str(idx.name)+", ",
            print ""
        if None in self._data:
            print >>ostream, "\tInitial Value : Lower Bound : Upper Bound : "  \
                             "Current Value: Fixed: Stale"
            lb_value = None
            if self._data[None].lb is not None:
                lb_value = value(self._data[None].lb)
            ub_value = None
            if self._data[None].ub is not None:
                ub_value = value(self._data[None].ub)

            print >>ostream, "\t %s : %s : %s : %s : %s : %s" % (
              str(self._data[None].initial),
              str(lb_value),
              str(ub_value),
              str(self._data[None].value),
              str(self._data[None].fixed),
              str(self._data[None].stale)
            )
        else:
            print >>ostream, "\tKey : Initial Value : Lower Bound : "          \
                             "Upper Bound : Current Value: Fixed: Stale"
            tmp=self._data.keys()
            tmp.sort()
            for key in tmp:
                initial_val = self._data[key].initial
                lb_value = None
                if self._data[key].lb is not None:
                    lb_value = value(self._data[key].lb)
                ub_value = None
                if self._data[key].ub is not None:
                    ub_value = value(self._data[key].ub)

                print >>ostream, "\t%s : %s : %s : %s : %s : %s : %s" % (
                  str(key),
                  str(initial_val),
                  str(lb_value),
                  str(ub_value),
                  str(value(self._data[key].value)),
                  str(value(self._data[key].fixed)),
                  str(self._data[key].stale)
                )


    def display(self, prefix="", ostream=None):
        if ostream is None:
            ostream = sys.stdout
        print >>ostream, prefix+"Variable "+self.name,":",
        print >>ostream, "  Size="+str(len(self)),
        print >>ostream, "Domain="+self.domain.name
        if None in self._data:
            print >>ostream, "%s  Value=%s" % (
              prefix,
              pyutilib.misc.format_io(self._data[None].value)
            )
        else:
            for key in self._data:
                val = self._data[key].value
                print >>ostream, prefix+"  "+str(key)+" : "+str(val)

# a _VarElement is the implementation representing a "singleton" or non-indexed variable.
# NOTE: this class derives from both a "slot"ized base class (_VarData) and a normal
#       class with a dictionary (Var) - beware (although I believe the __getstate__
#       implementation should be attribute-independent).

class _VarElement(Var, _VarData):

    def __init__(self, *args, **kwd):
        _VarData.__init__(self,
                            kwd.get('name', None), 
                            kwd.get('within', kwd.get('domain', Reals)), 
                            self)
        Var.__init__(self, *args, **kwd)
        self._data[None] = self
        self._data[None].index = None

    def __call__(self, exception=True):
        if None in self._data:
            return self._data[None].value
        return None

    def __getstate__(self):
        #
        # picks up all slots in the _VarData class, and in particular
        # makes sure the "var" and "component" values are not weakrefs,
        # but the actual objects themselves.
        #
        varvalue_result = _VarData.__getstate__(self)
        varvalue_result['component'] = self
        varbase_result = Var.__getstate__(self)
        return dict(varvalue_result.items() + varbase_result.items())

    def __setstate__(self, state):
        for (slot_name, value) in state.iteritems():
            setattr(self, slot_name, value)

        self._data[None].component = weakref.ref(self)
        # this is hackish, in that it replicates code from the base Component setstate method - revisit at some point.
        if '_parent' in self.__dict__.keys() and self._parent is not None and type(self._parent) != weakref.ref:
            self._parent = weakref.ref(self._parent)

    def is_constant(self):
        return _VarData.is_constant(self)

# a _VarArray is the implementation representing an indexed variable.

class _VarArray(Var):
    
    def __init__(self, *args, **kwds):
        Var.__init__(self, *args, **kwds)
        self._dummy_val = _VarData(kwds.get('name', None), 
                                    kwds.get('within', kwds.get('domain', Reals)), 
                                    self)

    def __float__(self):
        raise TypeError, "Cannot access the value of array variable "+self.name

    def __int__(self):
        raise TypeError, "Cannot access the value of array variable "+self.name

    def _valid_value(self,value,use_exception=True):
        return self._dummy_val._valid_value(value, use_exception)

    def set_value(self, value):
        msg = "Cannot specify the value of array variable '%s'"
        raise ValueError, msg % self.name

    def __str__(self):
        return self.name

class VarList(_VarArray):
    """
    Variable-length indexed variable objects used to construct Pyomo models.
    """

    alias("VarList", "Variable-length list of decision variables in a model.")

    End = ( 1003, )

    def __init__(self, *args, **kwargs):
        if len(args) > 0:
            raise ValueError, "Cannot specify indices for a VarList object"
        # Construct parents...
        self._hidden_index = Set()
        _VarArray.__init__(self, self._hidden_index, **kwargs)
        self._ndim = 1
        self._nvars = 0

    def is_fixed(self):
        if self._nvars == 0:
            return False
        for idx in xrange(self._nvars):
            if not self[idx].is_fixed():
                return False
        return True

    def is_constant(self):
        return False

    def polynomial_degree(self):
        if self.is_fixed():
            return 0
        return 1

    def construct(self, data=None):
        if __debug__:
            logger.debug("Constructing variable list %s",self.name)
        self._hidden_index.construct()
        _VarArray.construct(self, data)

    def add(self):
        self._hidden_index.add(self._nvars)
        self._add_indexed_member(self._nvars)
        self._nvars += 1
        return self[self._nvars-1]



