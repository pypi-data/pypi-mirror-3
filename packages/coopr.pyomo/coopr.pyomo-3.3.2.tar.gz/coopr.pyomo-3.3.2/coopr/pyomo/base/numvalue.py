#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

__all__ = [ 'value', 'NumericValue', 'as_numeric', 'NumericConstant',
            'is_constant', 'is_fixed']

import sys
import logging

import pyutilib.math
from set_types import Reals, Any

logger = logging.getLogger('coopr.pyomo')

def create_name(name, ndx):
    """
    Create a canonical name for a component using the given index.
    """
    if ndx is None:
        return name
    if type(ndx) is tuple:
        tmp = str(ndx).replace(', ',',')
        return name+"["+tmp[1:-1]+"]"
    return name+"["+str(ndx)+"]"


##------------------------------------------------------------------------
##
## Standard types of expressions
##
##------------------------------------------------------------------------


def _old_value(obj):
    """
    A utility function that returns the value of a Pyomo object or expression.

    If the argument is None, a numeric value or a string, then this
    function simply returns the argument.  Otherwise, if the argument is
    a NumericValue then the __call__ method is executed.
    """
    if obj is None:
        return None
    if type(obj) in (bool,int,long,float,str):
        return obj
    if not isinstance(obj, NumericValue):
        raise ValueError("Object %s is not a NumericValue object" % (obj,))
    tmp = obj()
    if tmp is None:
        raise ValueError("No value for uninitialized NumericValue object %s"
                         % (obj.name,))
    return tmp

# It is *significantly* faster to build the list of types we want to
# test against as a "static" set, and not to regenerate it locally for
# every call.  Plus, this allows us to dynamically augment the set with
# new "native" types (e.g., from NumPy)
native_numeric_types = set([ int, float, long ])
native_types = set([ bool, str, type(None) ]).union( native_numeric_types )

def value(obj):
    """
    A utility function that returns the value of a Pyomo object or expression.

    If the argument is None, a numeric value or a string, then this
    function simply returns the argument.  Otherwise, if the argument is
    a NumericValue then the __call__ method is executed.
    """
    if obj.__class__ in native_types:
        return obj
    try:
        numeric = obj.as_numeric()
    except AttributeError:
        numeric = as_numeric(obj)
    try:
        tmp = numeric()
    except:
        logger.error(
            "evaluating object as numeric value: %s\n\t(object: %s)\n\t%s"
            % (obj, type(obj), sys.exc_info()[1]))
        raise ValueError
    
    if tmp is None:
        raise ValueError("No value for uninitialized NumericValue object %s"
                         % (obj.name,))
    return tmp


def is_constant(obj):
    """
    A utility function that returns a boolean that indicates whether the
    object is a constant
    """
    # This method is rarely, if ever, called.  Plus, since the
    # expression generation (and constraint generation) system converts
    # everything to NumericValues, it is better (i.e., faster) to assume
    # that the obj is a NumericValue
    #
    # JDS: NB: I am not sure why we allow str to be a constant, but
    # since we have historically done so, we check for type membership
    # in native_types and not in native_numeric_types.
    #
    if obj.__class__ in native_types:
        return True
    try:
        return obj.is_constant()
    except AttributeError:
        pass
    return as_numeric(obj).is_fixed()

def is_fixed(obj):
    """
    A utility function that returns a boolean that indicates whether the
    input object's value is fixed.
    """
    # JDS: NB: I am not sure why we allow str to be a constant, but
    # since we have historically done so, we check for type membership
    # in native_types and not in native_numeric_types.
    #
    if obj.__class__ in native_types:
        return True
    try:
        return obj.is_fixed()
    except AttributeError:
        pass
    return as_numeric(obj).is_fixed()


# It is very common to have only a few constants in a model, but those
# constants get repeated many times.  KnownConstants lets us re-use /
# share constants we have seen before.
KnownConstants = {}

def as_numeric(obj):
    """
    Verify that this obj is a NumericValue or intrinsic value.
    """
    # int and float are *so* common that it pays to treat them specially
    if obj.__class__ in native_numeric_types:
        if obj in KnownConstants:
            return KnownConstants[obj]
        else:
            # Because INT, FLOAT, and sometimes LONG hash the same, we
            # want to convert them to a common type (at the very least,
            # so that the order in which tests run does not change the
            # results!)
            try:
                tmp = float(obj)
                if tmp == obj:
                    tmp = NumericConstant(None, None, tmp)
                    KnownConstants[obj] = tmp
                    return tmp
            except:
                pass

            tmp = NumericConstant(None, None, tmp)
            KnownConstants[obj] = tmp
            return tmp
    try:
        return obj.as_numeric()
    except AttributeError:
        pass
    try: 
        if obj.__class__ is (obj + 0).__class__:
            # obj may (or may not) be hashable, so we need this try
            # block so that things proceed normally for non-hashable
            # "numeric" types
            try:
                if obj in KnownConstants:
                    return KnownConstants[obj]
                else:
                    tmp = NumericConstant(None,None,obj)
                    KnownConstants[obj] = tmp
                    
                    # If we get here, this is a reasonably well-behaving
                    # numeric type: add it to the native numeric types
                    # so that future lookups will be faster.
                    native_numeric_types.add(obj.__class__)
                    # native numeric types are also native types
                    native_types.add(obj.__class__)

                    return tmp
            except:
                return NumericConstant(None, None, obj)
    except:
        pass
    raise ValueError("This object is not a numeric value: %s" % (obj,))


class NumericValue(object):
    """
    This is the base class for numeric values used in Pyomo.

    For efficiency purposes, some derived classes do not call this
    constructor (e.g. see the "Expression" class defined in "expr.py").
    This is fine if the value is finite or unspecified.  In that
    case, no validation is performed, so the subclass can simply
    specify the name, domain and value.

    Constructor Arguments:
        domain          The value domain.  Unspecified default: None.
        name            The value name.  Unspecified default: None
        value           The initial value.  Unspecified default: None.

    Public Class Attributes:
        domain          A domain object that restricts possible values for
                        this object.
        name            A name for this object.
        value           The numeric value of this object.
    """

    __slots__ = ['name','domain','value']

    __hash__ = None

    def __init__(self, name, domain, value):
        self.name = name
        self.domain = domain
        if value is None:
            self.value = None
        elif pyutilib.math.is_nan(value):
            self.value = pyutilib.math.nan
        else:
            self.value = value

    def __getstate__(self):
        """
        This method is required because this class uses slots.

        Derived classes need to over-ride this method to both call the
        base class method (which will populate the dictionary with slots
        specific to the base class, and to add any slots to the
        dictionary unique to the derived class.
        """
        return dict((i, getattr(self, i, None)) for i in NumericValue.__slots__)

    def __setstate__(self, state):
        """
        This method is required because this class uses slots.

        Derived classes need to over-ride this method to both call the
        base class method (which will populate the dictionary with slots
        specific to the base class, and to add any slots to the
        dictionary unique to the derived class.
        """
        for (slot_name, value) in state.iteritems():
            setattr(self, slot_name, value)

    def is_constant(self):
        """Return True if this numeric value is a constant value."""
        return True

    def is_expression(self):
        """Return True if this numeric value is an expression."""
        return False

    def is_relational(self):
        """
        Return True if this numeric value represents a relational
        expression.
        """
        return False

    def is_indexed(self):
        """Return True if this numeric value is an indexed object."""
        return False

    def polynomial_degree(self):
        """Return the polynomial degree of this expression."""
        return 0

    def is_fixed(self):               #pragma:nocover
        """Return True is this is a non-constant value that has been fixed."""
        return False

    def as_numeric(self):
        return self

    def pprint(self, ostream=None, verbose=False):
        """Print the value of this numeric object"""
        raise IOError("NumericValue:pprint is not defined")     #pragma:nocover

    def display(self, ostream=None):    #pragma:nocover
        """Provide a verbose display of this numeric object"""
        self.pprint(ostream=ostream)

    def reset(self):            #pragma:nocover
        """Reset the value of this numeric object"""
        pass                    #pragma:nocover

    def set_value(self, val):
        """Set the value of this numeric object, after validating its value."""
        if self._valid_value(val):
            self.value=val

    def __nonzero__(self):
        """Return True if the value is defined and non-zero."""
        if self.value is None:
            raise ValueError("Numeric value is undefined")
        if self.value:
            return True
        return False

    def __call__(self, exception=True):
        """Return the value of this object."""
        return self.value

    def __float__(self):
        """Coerce the value to a floating point."""
        tmp = self.__call__()
        if tmp is None:
            raise ValueError("Cannot coerce numeric value `%s' to float "
                             "because it is uninitialized." % (self.name,))
        return float(tmp)

    def __int__(self):
        """Coerce the value to an integer point."""
        tmp = self.__call__()
        if tmp is None:
            raise ValueError("Cannot coerce numeric value `%s' to integer "
                             "because it is uninitialized." % (self.name,))
        return int(tmp)

    def _valid_value(self, value, use_exception=True):
        """
        Validate the value.  If use_exception is True, then raise an
        exception.
        """
        ans = value is None or self.domain is None or value in self.domain
        if not ans and use_exception:
            raise ValueError("Numeric value `%s` is not in domain %s"
                             % (value, self.domain))
        return ans

    def __lt__(self,other):
        """Less than operator

        (Called in response to 'self < other' or 'other > self'.)
        """
        return generate_relational_expression('<', self, as_numeric(other))

    def __gt__(self,other):
        """Greater than operator

        (Called in response to 'self > other' or 'other < self'.)
        """
        return generate_relational_expression('<', as_numeric(other), self)

    def __le__(self,other):
        """Less than or equal operator

        (Called in response to 'self <= other' or 'other >= self'.)
        """
        return generate_relational_expression('<=', self, as_numeric(other))

    def __ge__(self,other):
        """Greater than or equal operator

        (Called in response to 'self >= other' or 'other <= self'.)
        """
        return generate_relational_expression('<=', as_numeric(other), self)

    def __eq__(self,other):
        """Equal to operator

        (Called in response to 'self = other'.)
        """
        return generate_relational_expression('==', self, as_numeric(other))

    def __add__(self,other):
        """Binary addition

        (Called in response to 'self + other'.)
        """
        return generate_expression(_add,self,other)

    def __sub__(self,other):
        """ Binary subtraction

        (Called in response to 'self - other'.)
        """
        return generate_expression(_sub,self,other)

    def __mul__(self,other):
        """ Binary multiplication

        (Called in response to 'self * other'.)
        """
        return generate_expression(_mul,self,other)

    def __div__(self,other):
        """ Binary division

        (Called in response to 'self / other'.)
        """
        return generate_expression(_div,self,other)

    def __truediv__(self,other):
        """ Binary division

        (Called in response to 'self / other' with __future__.division.)
        """
        return generate_expression(_div,self,other)

    def __pow__(self,other):
        """ Binary power

        (Called in response to 'self ** other'.)
        """
        return generate_expression(_pow,self,other)

    def __radd__(self,other):
        """Binary addition

        (Called in response to 'other + self'.)
        """
        return generate_expression(_radd,self,other)

    def __rsub__(self,other):
        """ Binary subtraction

        (Called in response to 'other - self'.)
        """
        return generate_expression(_rsub,self,other)

    def __rmul__(self,other):
        """ Binary multiplication

        (Called in response to 'other * self'.)
        """
        return generate_expression(_rmul,self,other)

    def __rdiv__(self,other):
        """ Binary division

        (Called in response to 'other / self'.)
        """
        return generate_expression(_rdiv,self,other)

    def __rtruediv__(self,other):
        """ Binary division

        (Called in response to 'other / self' with __future__.division.)
        """
        return generate_expression(_rdiv,self,other)

    def __rpow__(self,other):
        """ Binary power

        (Called in response to 'other ** self'.)
        """
        return generate_expression(_rpow,self,other)

    def __iadd__(self,other):
        """Binary addition

        (Called in response to 'self += other'.)
        """
        return generate_expression(_iadd,self,other)

    def __isub__(self,other):
        """ Binary subtraction

        (Called in response to 'self -= other'.)
        """
        return generate_expression(_isub,self,other)

    def __imul__(self,other):
        """ Binary multiplication

        (Called in response to 'self *= other'.)
        """
        return generate_expression(_imul,self,other)

    def __idiv__(self,other):
        """ Binary division

        (Called in response to 'self /= other'.)
        """
        return generate_expression(_idiv,self,other)

    def __itruediv__(self,other):
        """ Binary division

        (Called in response to 'self /= other' with __future__.division.)
        """
        return generate_expression(_idiv,self,other)

    def __ipow__(self,other):
        """ Binary power

        (Called in response to 'self **= other'.)
        """
        return generate_expression(_ipow,self,other)

    def __neg__(self):
        """ Negation

        (Called in response to '- self'.)
        """
        return generate_expression(_neg,self, None)

    def __pos__(self):
        """ Positive expression

        (Called in response to '+ self'.)
        """
        return self

    def __abs__(self):
        """ Absolute value

        (Called in response to 'abs(self)'.)
        """
        return generate_expression(_abs,self, None)


class NumericConstant(NumericValue):
    """An object that contains a constant numeric value.

    If domain is None, then the domain is assumed to be Reals.
    Additionally, this class does not validate the values of numeric
    constants.  The user specifies the value, so we assume that the
    value is valid.

    Constructor Arguments:
        name            The value name.  Unspecified default: None
        domain          The value domain.  Unspecified default: None.
        value           The initial value.  Unspecified default: None.
    """


    __slots__ = [] # adds no attributes above and beyond those defined in the base class.

    def __init__(self, name, domain, value):
        if domain is None:
            self.domain = Reals
        else:
            self.domain = domain
        self.name = name
        if pyutilib.math.is_nan(value):
            self.value = pyutilib.math.nan
        else:
            self.value = value

    def is_fixed(self):
        return True

    def __str__(self):
        return str(self.value)

    def pprint(self, ostream=None, verbose=False):
        if ostream is None:         #pragma:nocover
            ostream = sys.stdout
        print >>ostream, str(self),

# We use as_numeric() so that the constant is also in the cache
ZeroConstant = as_numeric(0)

# TODO - Why is this here???
from expr import generate_expression, generate_relational_expression, \
     _add, _sub, _mul, _div, _pow, _neg, _abs, _inplace, \
     _radd, _rsub, _rmul, _rdiv, _rpow, _iadd, _isub, _imul, _idiv, _ipow
