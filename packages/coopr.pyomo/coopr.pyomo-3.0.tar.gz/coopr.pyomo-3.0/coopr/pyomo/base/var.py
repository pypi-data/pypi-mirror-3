#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

__all__ = ['Var', 'VarList', 'VarStatus', '_VarBase', '_VarValue']

import logging
from component import Component
from misc import apply_indexed_rule
from numvalue import *
from numvalue import create_name
from sets import Set
from pyutilib.component.core import alias
import types
from set_types import *
from indexed_component import IndexedComponent
import pyutilib.math
import pyutilib.misc
from pyutilib.enum import Enum
import sys
from param import _ParamValue
from coopr.pyomo.base.util import isfunctor
import weakref

logger = logging.getLogger('coopr.pyomo')

VarStatus = Enum( 'undefined', 'fixed_by_presolve', 'fixed_by_optimizer',
                  'unused', 'used', )

class _VarValue(NumericValue):
    """Holds the numeric value of a variable"""

    __slots__ = ['component','index','id','initial','active','lb','ub','fixed','status','_is_binary','_is_integer','_is_continuous']

    #
    # IMPT: This class over-rides __getstate__ and __setstate__, due to the 'var' and 'component' weakrefs, and because of slots.
    #

    # IMPT: If a specific argument is intended to be left unassigned, use the following default values in the constructor below:
    # name: None
    # domain: None

    def __init__(self, name, domain):
        """Constructor"""

        # IMPT: The following three lines are equivalent to calling the
        #       basic NumericValue constructor, i.e., as follows:
        #       NumericValue.__init__(self, name, domain, None, False)
        #       That particular constructor call takes a lot of time
        #       for big models, and is unnecessary because we're not
        #       validating any values.
        self.name = name
        self.domain = domain
        self.value = None

        # NOTE: the "name" attribute (part of the base NumericValue class) is
        #       typically something like some_var[x,y,z] - an easy-to-read
        #       representation of the variable/index pair.

        # NOTE: the following is presently set by the parent. arguably, we
        #       should provide keywords to streamline initialization.
        self.component = None # the "parent" variable
        self.index = None # the index of this variable within the "parent"

        # TBD: Document where this gets populated.
        self.id = None

        # the default initial value for this variable.
        self.initial = None

        # is this variable an active component of the current model?
        self.active = True

        # IMPORTANT: in contrast to the initial value, the lower and upper
        #             bounds of a variable can in principle be either numeric constants,
        #             parameter values, or expressions - anything is OK, as long as
        #             invoking () is legal.
        self.lb = None
        self.ub = None

        self.fixed = False
        self.status = VarStatus.undefined

        # cached for efficiency purposes - isinstance is not cheap.
        self._is_binary = isinstance(self.domain, BooleanSet)
        self._is_integer = isinstance(self.domain, IntegerSet)
        self._is_continuous = not (self._is_binary or self._is_integer)

    def __str__(self):
        # the name can be None, in which case simply return "".
        if self.name is None:
            return ""
        else:
            return self.name

    def __getstate__(self):

        result = NumericValue.__getstate__(self)
        for i in _VarValue.__slots__:
            result[i] = getattr(self, i)
        if type(result['component']) is weakref.ref:
            result['component'] = result['component']()
        return result

    def __setstate__(self, state):
        for (slot_name, value) in state.iteritems():
            setattr(self, slot_name, value)
        if self.component is not None:
            self.component = weakref.ref(self.component)

    def getattrvalue(self, attr_name):
        if attr_name not in self.component()._attr_values:
            raise RuntimeError,"Variable="+str(self.component().name)+" does not have an attribute defined with name="+str(attr_name)
        return self.component()._attr_values[attr_name][self.index]

    def setattrvalue(self, attr_name, attr_value, define=False):
        if attr_name not in self.component()._attr_values:
            if define:
                self.component().declare_attribute(attr_name)
            else:
                raise RuntimeError,"Variable="+str(self.component().name)+" does not have an attribute defined with name="+str(attr_name)
        self.component()._attr_values[attr_name][self.index] = attr_value

    def activate(self):
        self.active=True

    def deactivate(self):
        self.active=False

    def setlb(self, value):
        # python only has 3 numeric built-in type that we deal with (we ignore
        # complex numbers).
        if value is None:
            self.lb = None
        elif isinstance(value, (int, long, float)):
            self.lb = NumericConstant(None,None,value)
        elif value.is_constant():
            self.lb = NumericConstant(None,None,value())
        else:
            msg = "Unknown type '%s' supplied as variable lower bound - "     \
                  'legal types are numeric constants or parameters'
            raise ValueError, msg % str( type(value) )

    def setub(self, value):
        # python only has 3 numeric built-in type that we deal with (we ignore
        # complex numbers).
        if isinstance(value, (int, long, float)):
            self.ub = NumericConstant(None,None,value)
        elif value is None:
            self.ub = None
        elif value.is_constant():
            self.ub = NumericConstant(None,None,value())
        else:
            msg = "Unknown type '%s' supplied as variable lower bound - "     \
                  'legal types are numeric constants or parameters'
            raise ValueError, msg % str( type(value) )


    def fixed_value(self):
        if self.fixed:
            return True
        return False

    def is_constant(self):
        if self.fixed:
            return True
        return False

    def polynomial_degree(self):
        if self.fixed:
            return 0
        return 1

    def is_binary(self):
        return self._is_binary

    def is_integer(self):
        return self._is_integer

    def is_continuous(self):
        return self._is_continuous

    def pprint(self, ostream=None, verbose=False):
        if ostream is None:
            ostream = sys.stdout
        print >>ostream, str(self),

    def _tighten_bounds(self):
        """
        Attempts to tighten the lower and upper bounds on
        this variable by using the domain.
        """
        try:
            dlb, dub = self.domain.bounds()
        except:
            # No explicit domain bounds
            return

        if (dlb is not None):
            if (self.lb is None) or (dlb > self.lb.value):
                self.setlb(dlb)

        if (dub is not None):
            if (self.ub is None) or (dub < self.ub.value):
                self.setub(dub)


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

class _VarBase(IndexedComponent):
    """A numeric variable, which may be defined over a index"""

    """ Constructor
        Arguments:
           name         The name of this variable
           index        The index set that defines the distinct variables.
                          By default, this is None, indicating that there
                          is a single variable.
           domain       A set that defines the type of values that
                          each variable must be.
           default      A set that defines default values for this
                          variable.
           bounds       A rule for defining bounds values for this
                          variable.
           rule         A rule for setting up this variable with
                          existing model data
    """

    #
    # IMPT: The default __getstate__ and __setstate__ are fine - this class owns no weakrefs or slots,
    #       and should be able to rely on the base IndexedComponent methods.
    #

    # TODO: default and rule keywords are not used?  Need to talk to Bill ...?
    def __init__(self, *args, **kwd):
        # Default keyword values
        #
        self._initialize = kwd.pop('initialize', None )
        self.name   = kwd.pop('name', 'unknown')
        self.domain = kwd.pop('within', Reals )
        self.domain = kwd.pop('domain', self.domain )
        self.bounds = kwd.pop('bounds', None )
        self._defer_domain = False

        #Handle within=not_pyomo_object 
        if not hasattr(self.domain,'virtual') or not self.domain.virtual:
            if self.domain == [] or self.domain == set([]):
                raise ValueError,"Attempting to set a variable's domain to an empty set"
            else: 
                from rangeset import RangeSet
                from sets import _SetContainer
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

        self._attr_declarations = {} # maps the name of an attribute (i.e., a suffix) to its default value.
        self._attr_values = {} # maps the name of an attribute to a dictionary containing (index, value) pairs.
        self._varval = {}
        self._binary_keys = []
        self._continuous_keys = []
        self._integer_keys = []

        # Check for domain rules
        if isfunctor(self.domain):
            self._domain_rule = self.domain

            # Individual variables will be restricted
            self.domain = None
        else:
            self._domain_rule = None

    def as_numeric(self):
        if None in self._varval:
            return self._varval[None]
        return self

    def is_indexed(self):
        return self._ndim > 0

    def is_expression(self):
        return False

    def is_relational(self):
        return False

    def keys(self):
        return self._varval.keys()

    # returns a dictionary of index-value pairs.
    def extract_values(self):
        return dict(((index, varval.value) for index, varval in self._varval.iteritems()))

    # takes as input a dictionary of index-value pairs.
    def store_values(self, new_values):
        for index, varval in self._varval.iteritems():
            varval.value = new_values[index]

    def binary_keys(self):
        """ Returns the keys of all binary variables """
        return self._binary_keys

    def continuous_keys(self):
        """ Returns the keys of all continuous variables """
        return self._continuous_keys

    def integer_keys(self):
        """ Returns the keys of all integer variables """
        return self._integer_keys

    def __iter__(self):
        return self._varval.keys().__iter__()

    def iteritems(self):
        return self._varval.iteritems()

    def itervalues(self):
        return self._varval.itervalues()

    def __contains__(self,ndx):
        return ndx in self._varval

    def dim(self):
        return self._ndim

    def reset(self):
        for value in self._varval.itervalues():
            value.set_value(value.initial)

    def __len__(self):
        return len(self._varval)

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
        self._varval[ndx].value = val

    def __getitem__(self,ndx):
        """This method returns a _VarValue object.  This object can be
           coerced to a numeric value using the value() function, or using
           explicity coercion with float().
        """
        try:
            return self._varval[ndx]
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

    def _add_domain_key(self, ndx, domain):
        """ Register an index with a specific set of keys """
        if isinstance(domain, BooleanSet):
            self._binary_keys.append(ndx)
        elif isinstance(domain, IntegerSet):
            self._integer_keys.append(ndx)
        else:
            self._continuous_keys.append(ndx)

    def _add_indexed_member(self, ndx):
        # Check for domain rules
        if self._domain_rule is not None:
            domain = apply_indexed_rule( self, self._domain_rule,
                                         self.model(), ndx )
            if isinstance(domain, BooleanSet):
                self._binary_keys.append(ndx)
            elif isinstance(domain, IntegerSet):
                self._integer_keys.append(ndx)
            else:
                self._continuous_keys.append(ndx)
        else:
            domain = self.domain

        new_varval = _VarValue(create_name(self.name,ndx), domain)
        new_varval.component = weakref.ref(self)
        new_varval.index = ndx
        
        self._varval[ndx] = new_varval


    def construct(self, data=None):
        if __debug__:   #pragma:nocover
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug("Constructing Variable, name=%s, from data=%s", self.name, `data`)
        if self._constructed:
            return
        self._constructed=True
        #
        # Construct _VarValue objects for all index values
        #
        if self._ndim > 0:
            if type(self._initialize) is dict:
                self._index = self._initialize.keys()

            for ndx in self._index:
                # TODO: it is common to construct empty VarLists... and
                # when that happens, the empty implicit set comes in
                # with a "None" index!
                if ndx is not None: 
                    self._add_indexed_member(ndx)


        #
        # Define the _XXX_keys objects if domain isn't a rule;
        # they were defined individually above in the case of
        # a rule
        #
        if not self._domain_rule is not None:
            if isinstance(self.domain, BooleanSet):
                self._binary_keys = self._varval.keys()
            elif isinstance(self.domain, IntegerSet):
                self._integer_keys = self._varval.keys()
            else:
                self._continuous_keys = self._varval.keys()

        #
        # Initialize values with a dictionary if provided
        #
        if self._initialize is not None:
            #
            # Initialize values with the _rule function if provided
            #
            if self._initialize.__class__ is types.FunctionType:
                for key in self._varval:
                    if key is None:
                        val = self._initialize(self.model())
                    else:
                        val = apply_indexed_rule( self, self._initialize,
                                                  self.model(), key )
                    val = value(val)
                    self._valid_value(val, True)
                    self._varval[key].value = self._varval[key].initial = val
            elif self._initialize.__class__ is dict:
                for key in self._initialize:
                    val = self._initialize[key]
                    self._valid_value(val, True)
                    self._varval[key].value = self._varval[key].initial = val
            else:
                for key in self._index:
                    val = self._initialize
                    self._valid_value(val, True)
                    self._varval[key].value = self._varval[key].initial = val
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

                for key,varval in self._varval.iteritems():
                    if lb is not None:
                        varval.setlb(lb)
                    if ub is not None:
                        varval.setub(ub)

            else:

                # bounds are specified via a function

                for key,varval in self._varval.iteritems():
                    if key is None:
                        (lb, ub) = self.bounds(self.model())
                    else:
                        (lb, ub) = apply_indexed_rule( self, self.bounds,
                                                       self.model(), key )
                    varval.setlb(lb)
                    varval.setub(ub)

                for key in self._varval:
                    if self._varval[key].lb is not None and not pyutilib.math.is_finite(self._varval[key].lb()):
                        self._varval[key].setlb(None)
                    if self._varval[key].ub is not None and not pyutilib.math.is_finite(self._varval[key].ub()):
                        self._varval[key].setub(None)
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
                for key in self._varval:
                    if not dbounds[0] is None:
                        if self._varval[key].lb is None or                     \
                            dbounds[0] > self._varval[key].lb():
                            self._varval[key].setlb(dbounds[0])

                    if not dbounds[1] is None:
                        if self._varval[key].ub is None or                     \
                            dbounds[1] < self._varval[key].ub():
                            self._varval[key].setub(dbounds[1])
        #
        # Setup declared attributes for all variables
        #
        for attr_name in self._attr_declarations:
            default_value = self._attr_declarations[attr_name][0]
            suffix_dict = {}
            for key in self._varval:
                suffix_dict[key]=default_value
            self._attr_values[attr_name] = suffix_dict

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
        if None in self._varval:
            print >>ostream, "\tInitial Value : Lower Bound : Upper Bound : "  \
                             "Current Value: Fixed: Status"
            lb_value = None
            if self._varval[None].lb is not None:
                lb_value = self._varval[None].lb()
            ub_value = None
            if self._varval[None].ub is not None:
                ub_value = self._varval[None].ub()

            print >>ostream, "\t %s : %s : %s : %s : %s : %s" % (
              str(self._varval[None].initial),
              str(lb_value),
              str(ub_value),
              str(self._varval[None].value),
              str(self._varval[None].fixed),
              str(self._varval[None].status)
            )
        else:
            print >>ostream, "\tKey : Initial Value : Lower Bound : "          \
                             "Upper Bound : Current Value: Fixed: Status"
            tmp=self._varval.keys()
            tmp.sort()
            for key in tmp:
                initial_val = self._varval[key].initial
                lb_value = None
                if self._varval[key].lb is not None:
                    lb_value = self._varval[key].lb()
                ub_value = None
                if self._varval[key].ub is not None:
                    ub_value = self._varval[key].ub()

                print >>ostream, "\t%s : %s : %s : %s : %s : %s : %s" % (
                  str(key),
                  str(initial_val),
                  str(lb_value),
                  str(ub_value),
                  str(value(self._varval[key].value)),
                  str(value(self._varval[key].fixed)),
                  str(self._varval[key].status)
                )


    def display(self, prefix="", ostream=None):
        if ostream is None:
            ostream = sys.stdout
        print >>ostream, prefix+"Variable "+self.name,":",
        print >>ostream, "  Size="+str(len(self)),
        print >>ostream, "Domain="+self.domain.name
        if None in self._varval:
            print >>ostream, "%s  Value=%s" % (
              prefix,
              pyutilib.misc.format_io(self._varval[None].value)
            )
        else:
            for key in self._varval:
                val = self._varval[key].value
                print >>ostream, prefix+"  "+str(key)+" : "+str(val)

    def declare_attribute(self, name, default=None):
        """
        Declare a user-defined attribute.
        """
        if name[0] == "_":
            msg = "Cannot define an attribute that begins with  '_'"
            raise AttributeError, msg
        if name in self._attr_declarations:
            raise AttributeError, "Attribute %s is already defined" % name
        self._attr_declarations[name] = (default,)
        #if not default is None:
            #self._valid_value(default)
        #
        # If this variable has been constructed, then
        # generate this attribute for all variables
        #
        # add to self._attr_values
        if len(self._varval) > 0:
            suffix_dict = {}
            for key in self._varval:
                suffix_dict[key]=default
            self._attr_values[name] = suffix_dict

    def attribute_defined(self, name):
        """
        Determine if a user-defined attribute actually exists!
        """
        return name in self._attr_declarations

# a _VarElement is the implementation representing a "singleton" or non-indexed variable.
# NOTE: this class derives from both a "slot"ized base class (_VarValue) and a normal
#       class with a dictionary (_VarBase) - beware (although I believe the __getstate__
#       implementation should be attribute-independent).

class _VarElement(_VarBase, _VarValue):

    def __init__(self, *args, **kwd):

        _VarValue.__init__(self, \
                           kwd.get('name', None), \
                           kwd.get('within', kwd.get('domain', Reals)))
        _VarBase.__init__(self, *args, **kwd)
        self._varval[None] = self
        self._varval[None].component = weakref.ref(self)
        self._varval[None].index = None

    def __call__(self, exception=True):
        if None in self._varval:
            return self._varval[None].value
        return None

    def __getstate__(self):

        # picks up all slots in the _VarValue class, and in particular
        # makes sure the "var" and "component" values are not weakrefs,
        # but the actual objects themselves.

        varvalue_result = _VarValue.__getstate__(self)
        varvalue_result['component'] = self
        varbase_result = _VarBase.__getstate__(self)
        return dict(varvalue_result.items() + varbase_result.items())

    def __setstate__(self, state):

        for (slot_name, value) in state.iteritems():
            setattr(self, slot_name, value)
        self._varval[None].component = weakref.ref(self)

    def is_constant(self):
        return _VarValue.is_constant(self)

# a _VarArray is the implementation representing an indexed variable.

class _VarArray(_VarBase):
    
    def __init__(self, *args, **kwds):

        _VarBase.__init__(self, *args, **kwds)
        self._dummy_val = _VarValue(kwds.get('name', None), \
                                    kwds.get('within', kwds.get('domain', Reals)))

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

    def construct(self, data=None):
        _VarBase.construct(self, data)

        for (ndx, var) in self._varval.iteritems():
            var._tighten_bounds()


class Var(Component):
    """
    Variable objects that are used to construct Pyomo models.
    """

    alias("Var", "Decision variables in a model.")

    def __new__(cls, *args, **kwds):
        if args == ():
            self = _VarElement(*args, **kwds)
        else:
            self = _VarArray(*args, **kwds)
        return self


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

    def fixed_value(self):
        if self._nvars == 0:
            return False
        for idx in xrange(self._nvars):
            if not self[idx].fixed_value():
                return False
        return True

    def is_constant(self):
        return self.fixed_value()

    def polynomial_degree(self):
        if self.is_constant():
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
