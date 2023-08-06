#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

__all__ = ['IndexedComponent']

import component
from sets import Set


def process_setarg(arg):
    """
    Process argument and return an associated set object.
    """
    if isinstance(arg,Set):
        # Argument is a Set instance
        return arg
    elif isinstance(arg,IndexedComponent):
        raise TypeError, "Cannot index a component with a non-set component"
    else:
        try:
            # Argument has set_options attribute, which is used to initialize the set
            options = getattr(arg,'set_options')
            options['initialize'] = arg
            return Set(**options)
        except:
            pass
    # Argument is assumed to be an initialization function
    return Set(initialize=arg)


class IndexedComponent(component.Component):
    """
    This is the base class for all indexed modeling components.

    Constructor arguments:
        ctype       The class type for the derived subclass
        doc         A text string describing this component

    Private class attributes:
        _data       A dictionary from the index set to component data objects
        _index      The set of valid indices
        _index_set  A tuple of set objects that represents the index set
        _ndim       The dimension of the index set
    """

    def __init__(self, *args, **kwds):
        component.Component.__init__(self, **kwds)
        #
        self._ndim = 0
        self._index_set = None
        self._index = {}
        self._data = {}
        #
        if len(args) == 0:
            #
            # If no indexing sets are provided, generate a dummy index
            #
            self._index={None:None}
        elif len(args) == 1:
            #
            # If a single argument is provided, the define the index using that
            # argument
            #
            self._index = process_setarg(args[0])
        else:
            #
            # If multiple arguments are provided, define _index_set with a tuple
            # of set objects
            #
            tmp = []
            for arg in args:
                tmp.append(process_setarg(arg))
            self._index_set=tuple(tmp)
        #
        # Compute the dimension of the indexing sets
        #
        self._compute_dim()
        #
        # Setup indices for suffix data
        #
        self._suffix_declaration = {}
        self._suffix_value = {}

    def clear(self):
        """Clear the data in this component"""
        self._data = {}

    def __len__(self):
        return len(self._data)

    def __contains__(self, ndx):
        return ndx in self._data

    def keys(self):
        return self._data.keys()

    def values(self):
        return self._data.values()

    def __iter__(self):
        return self._data.__iter__()

    def iteritems(self):
        return self._data.iteritems()

    def itervalues(self):
        return self._data.itervalues()

    def __getitem__(self, ndx):
        """
        This method returns the data corresponding to the given index.
        """
        if ndx in self._data:
            return self._data[ndx]
        raise KeyError, "Unknown index in component '%s': %s" % ( self.name, str(ndx) )

    def index(self):
        """Return the index set"""
        return self._index

    def is_indexed(self):
        """Return true if this component is indexed"""
        return self._ndim > 0

    def dim(self):
        """Return the dimension of the index"""
        return self._ndim

    def _compute_dim(self):
        """Compute the dimension of the set"""
        if self._ndim is 0:
            if self._index_set is None:
                # A single index set
                if type(self._index) is dict:
                    # If the index set is dictionary, then the argument list was empty
                    self._ndim = 0
                else:
                    # If the index set is Pyomo Set, then use its dimen attribute
                    self._ndim = self._index.dimen
            else:
                # A multi-set index
                self._ndim = 0
                for iset in self._index_set:
                    # Each index set is a Pyomo Set, so use its dimen attribute
                    self._ndim += iset.dimen

    def declare_suffix(self, suffix, default=None, rule=None):
        """
        Declare a suffix attribute.
        """
        if suffix[0] == "_":
            msg = "Cannot define a suffix that begins with  '_'"
            raise AttributeError, msg
        if suffix in self._suffix_declaration:
            raise AttributeError, "Suffix %s is already defined" % suffix
        self._suffix_declaration[suffix] = (default,rule)
        #
        # If this variable has been constructed, then
        # generate this attribute for all variables
        #
        #if len(self._data) > 0:
            #self._suffix_value[suffix] = {}

    def suffix_defined(self, suffix):
        """
        Determine if a suffix has aready been declared.
        """
        return suffix in self._suffix_declaration

    def get_suffix_value(self, suffix, index=None):
        try:
            return self._suffix_value[suffix, index]
        except KeyError:
            default = self._suffix_declaration[suffix]
            if not default[0] is None:
                return default[0]
            if not default[1] is None:
                val = default[1](self)
                self._suffix_value[suffix, index] = val
                return val
            return None

    def set_suffix_value(self, suffix, value, index=None, define=False):
        if define and suffix not in self._suffix_declaration:
            self.declare_suffix(suffix)
        self._suffix_value[suffix, index] = value

