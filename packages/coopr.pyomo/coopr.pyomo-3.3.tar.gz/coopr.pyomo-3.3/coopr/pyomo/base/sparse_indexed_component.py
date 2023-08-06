#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

__all__ = ['SparseIndexedComponent']

import weakref
import pyutilib.misc

import component
from sets import Set
from indexed_component import IndexedComponent

def process_setarg(arg):
    """
    Process argument and return an associated set object.
    """
    if isinstance(arg,Set):
        # Argument is a Set instance
        return arg
    elif isinstance(arg,IndexedComponent) or \
            isinstance(arg,SparseIndexedComponent):
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


UnindexedComponent_set = set([None])

class SparseIndexedComponent(component.Component):
    """
    This is the base class for all indexed modeling components.

    Constructor arguments:
        ctype       The class type for the derived subclass
        doc         A text string describing this component

    Private class attributes:
        _data       A dictionary from the index set to component data objects
        _index      The set of valid indices
    """

    def __init__(self, *args, **kwds):
        component.Component.__init__(self, **kwds)
        #
        self._data = {}
        #
        if len(args) == 0:
            #
            # If no indexing sets are provided, generate a dummy index
            #
            self._implicit_subsets = None
            self._index = UnindexedComponent_set
            self._data = {None: weakref.ref(self)}
        elif len(args) == 1:
            self._implicit_subsets = None
            self._index = process_setarg(args[0])
        else:
            # NB: Pyomo requires that all modelling components are
            # assigned to the model.  The trick is that we allow things
            # like "Param([1,2,3], range(100), initialize=0)".  This
            # needs to create *3* sets: two SetOf components and then
            # the SetProduct.  That means that teh component needs to
            # hold on to the implicit SetOf objects until the component
            # is assigned to a model (where the implicit subsets can be
            # "transferred" to the model).
            tmp = [process_setarg(x) for x in args]
            self._implicit_subsets = tmp
            self._index = tmp[0].cross(*tmp[1:])
        #
        # Setup indices for suffix data
        #
        self._suffix_declaration = {}
        self._suffix_value = {}

    def clear(self):
        """Clear the data in this component"""
        if UnindexedComponent_set != self._index:
            self._data = {}
        else:
            raise NotImplementedError(
                "Derived singleton component %s failed to define clear().\n"
                "\tPlease report this to the Pyomo developers"
                % (self.__class__.__name__,))

    def __len__(self):
        return len(self._index)

    def __contains__(self, ndx):
        return ndx in self._index

    #
    # NB: The standard access / iteration methods treat this component
    # as a dense set.  For some sparse components, this may result in
    # "filling in" the sparse matrix (through the derived class'
    # _default(idx) method).
    #
    
    def __iter__(self):
        return self._index.__iter__()

    def keys(self):
        # Leverage the iterator (generator) to generate the dense 
        return [ x for x in self ]

    def values(self):
        # Leverage the iterator (generator) to generate the dense 
        return [ self[x] for x in self ]

    def items(self):
        # Leverage the iterator (generator) to generate the dense 
        return [ (x, self[x]) for x in self ]

    def iterkeys(self):
        return self._index.__iter__()

    def itervalues(self):
        for key in self:
            yield self[key]
    
    def iteritems(self):
        for key in self:
            yield (key, self[key])

    #
    # NB: These are "sparse equivalent" access / iteration methods that
    # only loop over the defined data.  This preserves the object's
    # sparsity, but explicitly excludes non-defined values.
    #

    def sparse_keys(self):
        return self._data.keys()

    def sparse_values(self):
        return [ self[x] for x in self._data.keys() ]

    def sparse_items(self):
        return [ (x, self[x]) for x in self._data.keys() ]

    def sparse_iterkeys(self):
        return self._data.iterkeys()

    def sparse_itervalues(self):
        for key in self._data.iterkeys():
            yield self[key]
    
    def sparse_iteritems(self):
        for key in self._data.iterkeys():
            yield (key, self[key])


    def __getitem__(self, ndx):
        """
        This method returns the data corresponding to the given index.
        """
        if ndx in self._data:
            if ndx is None:
                return self
            else:
                return self._data[ndx]
        elif ndx in self._index:
            return self._default(ndx)
        else:
            ndx = self.normalize_index(ndx)
            if ndx in self._data:
                if ndx is None:
                    return self
                else:
                    return self._data[ndx]
            if ndx in self._index:
                return self._default(ndx)

        if not self.is_indexed():
            msg = "Error accessing indexed component: " \
                  "Cannot treat the scalar component '%s' as an array" \
                  % ( self.name, )
        else:
            msg = "Error accessing indexed component: " \
                  "Index '%s' is not valid for array component '%s'" \
                  % ( ndx, self.name, )
        raise KeyError(msg)

    def _default(self, index):
        raise NotImplementedError(
            "Derived component %s failed to define _default().\n"
            "\tPlease report this to the Pyomo developers"
            % (self.__class__.__name__,))

    def normalize_index(self, index):
        ndx = pyutilib.misc.flatten(index)
        if type(ndx) is list:
            if len(ndx) == 1:
                ndx = ndx[0]
            else:
                ndx = tuple(ndx)
        return ndx
            

    def index(self):
        """Return the index set"""
        return self._index

    def is_indexed(self):
        """Return true if this component is indexed"""
        return UnindexedComponent_set != self._index

    def dim(self):
        """Return the dimension of the index"""
        if UnindexedComponent_set != self._index:
            return self._index.dimen
        else:
            return 0

    def set_value(self, value):
        if UnindexedComponent_set != self._index:
            raise ValueError(
                "Cannot set the value for the indexed component '%s' "
                "without specifying an index value.\n"
                "\tFor example, model.%s[i] = value"
                % (self.name, self.name))
        else:
            raise NotImplementedError(
                "Derived component %s failed to define set_value() "
                "for singleton instances.\n"
                "\tPlease report this to the Pyomo developers"
                % (self.__class__.__name__,))
            

    def declare_suffix(self, suffix, default=None, rule=None):
        """
        Declare a suffix attribute.
        """
        if suffix[0] == "_":
            raise AttributeError(
                "Cannot define a suffix that begins with  '_'")
        if suffix in self._suffix_declaration:
            raise AttributeError("Suffix %s is already defined" % suffix)
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

