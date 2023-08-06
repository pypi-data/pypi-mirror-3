#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

__all__ = ['_ParamBase', 'Param']

import sys
import types
import logging

import pyutilib.misc
from component import Component
from set_types import Any
from indexed_component import IndexedComponent
from misc import apply_indexed_rule, apply_parameterized_indexed_rule
from numvalue import value
from plugin import ParamRepresentationFactory
from pyutilib.component.core import alias
from sets import _BaseSet
from param_repn import _ParamData

logger = logging.getLogger('coopr.pyomo')


class _ParamBase(IndexedComponent):
    """A parameter value, which may be defined over a index"""

    """ Constructor
        Arguments:
           name       The name of this parameter
           index      The index set that defines the distinct parameters.
                         By default, this is None, indicating that there
                         is a single parameter.
           within     A set that defines the type of values that
                         each parameter must be.
           validate   A rule for validating this parameter w.r.t. data
                         that exists in the model
           default    A set that defines default values for this parameter
           rule       A rule for setting up this parameter with existing model
                         data
           nochecking If true, various checks regarding valid domain and index
                      values are skipped. Only intended for use by algorithm
                      developers - not modelers!
    """
    def __init__(self, *args, **kwd):
        self._initialize = kwd.pop('initialize', None )
        self._initialize = kwd.pop('rule', self._initialize )
        self._validate   = kwd.pop('validate', None )
        self.domain      = kwd.pop('within', Any )
        self.nochecking  = kwd.pop('nochecking',False)
        defaultval       = kwd.pop('default', None )
        self.repn_type = kwd.pop('repn', 'pyomo_dict')
        #
        kwd.setdefault('ctype', Param)
        IndexedComponent.__init__(self, *args, **kwd)
        #
        self._default = _ParamData( self.name, self.domain, value(defaultval))
        #
        self.clear()

    def clear(self):
        """Clear the data in this component"""
        self._data = ParamRepresentationFactory( self.repn_type, args=(self,) )
        if self._data is None:
            raise ValueError, "Unknown parameter representation '%s'" % self.repn_type

    def initialize(self, data):
        self._initialize = data

    def pprint(self, ostream=None, verbose=False):
        if ostream is None:
            ostream = sys.stdout
        print >>ostream, "  ",self.name,":",
        if not self.doc is None:
            print >>ostream, self.doc
            print >>ostream, "  ",
        print >>ostream, "\tSize="+str(len(self)),
        print >>ostream, "\tDomain="+self.domain.name
        if None in self.keys():
            if self._constructed is True:
                print >>ostream, "\t", self._data(None)
            else:
                print >>ostream, "\t", "Not constructed"
        else:
            tmp=self._data.keys(nondefault=True)
            tmp.sort()
            for key in tmp:
                val = self._data(key)
                print >>ostream, "\t"+str(key)+" : "+str(val)
        if self._default.value is not None and not self._default.value is None:
            print >>ostream, "\tdefault: "+str(self._default.value)

    #
    # a utiliy to extract all index-value pairs defining this
    # parameter, returned as a dictionary. useful in many
    # contexts, in which key iteration and repeated __getitem__
    # calls are too expensive to extract the contents of a parameter.
    # NOTE: We are presently not careful if an index has not been
    #       explicitly defined - issues around defaults are bound
    #       to crop up.
    #
    def extract_values(self):
        return self._data.extract_values()

    # a utility to set values of a parameter "in bulk", using a dictionary of index<->value pairs.
    # far more efficient in some contexts than the approach of doing things by-index in an outer loop.    
    def store_values(self, new_values):
        return self._data.store_values(new_values)

    def set_default(self, value):
        self._default.value = value
        self._data.set_default(value)

    def as_numeric(self):
        if None in self._data:
            return self._data[None]
        return self

    def is_expression(self):
        return False

    def is_relational(self):
        return False

    def __setitem__(self, ndx, val):
        # Convert a tuple index value ...
        _type = type(ndx)
        if _type is tuple or _type is list:
            if self._ndim == 1:
                # An index for a single-dimensional parameter is just the first tuple value
                ndx = ndx[0]
            else:
                # Flatten index for a multi-dimensional non-singleton parameter
                ndx = tuple(pyutilib.misc.flatten(ndx))

        # a somewhat gory way to see if you have a singleton - the len()=1 check is needed to avoid "None" 
        # being passed illegally into set membership validation rules. the nochecking screen saves 
        # significant time here, as the len() computation is remarkably expensive.
        if (self.nochecking is False) and (len(self._index) == 1) and (None in self._index) and (ndx is not None):  
            # allow for None indexing only if this is truly a singleton
            msg = "Cannot set an array value in the simple parameter '%s'"
            raise KeyError, msg % self.name
        #
        if (self.nochecking is False) and (ndx not in self._index):
            msg = "Cannot set the value of array parameter '%s' with invalid index '%s'"
            raise KeyError, msg % ( self.name, str(ndx) )
        #
        self._data[ndx] = val
        #
        # This is at the end, so the user can write their validation
        # tests as if the data was already added.
        #
        if (self.nochecking is False) and (not self._valid_indexed_value(val, ndx, False)):
            msg = "Invalid parameter value: %s[%s] = '%s', value type=%s"
            raise ValueError, msg % ( self.name, str(ndx), str(val), str(type(val)) )

    def construct(self, data=None):
        """ Apply the rule to construct values in this set """
        if __debug__:
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug("Constructing Param, name="+self.name+", from data="+`data`)
        if self._constructed:
            raise IOError, "Cannot reconstruct parameter '%s'" % self.name
            return
        self.clear()
        self._constructed=True
        #
        # Code optimization with local variables
        #
        _name=self.name
        _domain=self.domain
        #
        self._data.update_index()
        rule = getattr(self,'rule',None)
        if not rule is None:
            self._initialize=rule
        #
        # Construct using the initial data or the data loaded from an
        # external source.  Note:  data values will be queried in to following
        # order:
        #   1) the 'data' dictionary
        #   2) the self._initialize dictionary
        #   3) the default value
        #
        if data is not None or type(self._initialize) is not types.FunctionType:
            #
            # Singleton (non-indexed) parameter
            #
            #print self._data, self._initialize, self._default.value, self._index
            if type(self._index) is dict:
                error = False
                if data is not None and None in data.keys():
                    self.value=data[None]
                elif not self._initialize is None:
                    if type(self._initialize) is not dict:
                        self.value=self._initialize
                    elif None in self._initialize:
                        self.value=self._initialize[None]
                    else:
                        error = True
                elif self._default.value is not None:
                    self.value=self._default.value
                else:
                    error = True
                if error:
                    msg = "Attempting to construct parameter '%s' without "   \
                          'parameter data'
                    raise ValueError, msg % _name

                #self.pprint()
                #print self.value#, self[None].value
                self[None] = self.value
                self._valid_indexed_value(self.value,(),True)
            else:
                #
                # Set external data values (if provided)
                #
                if data is not None:
                    #print 'z'
                    for key in data:
                        if type(key) is tuple and len(key)==1:
                            tmpkey=key[0]
                        else:
                            tmpkey=key
                        self.__setitem__(key, data[key])
                #
                # Initialize with initialization data.
                #
                elif self._initialize is not None:
                    #print 'y'
                    if type(self._initialize) is dict:
                        for key in self._initialize:
                            self.__setitem__(key, self._initialize[key])
                    else:
                        self._data.set_item(val=self._initialize)
        #
        # Construct using the rule
        #
        elif type(self._initialize) is types.FunctionType:
            if (type(self._index) is dict) and (None in self._index):
                # singleton
                self.value = self._initialize(self._model())
                self[None] = self.value
            else:
                # non-singleton
                for index in self._index:
                    # IMPORTANT: Do *not* call self.__setitem__ here - we already know the index is
                    #            valid (and flattened), and validating indices is far too expensive to 
                    #            waste time doing it again. however, we still need to validate the
                    #            value generated by the rule, relative to the parameter domain.
                    param_value = apply_indexed_rule(self, self._initialize, self._model(), index)
                    if not ((self.domain is Any) or (param_value in self.domain)):
                        msg = "Invalid value '%s' specified via rule initializer for parameter '%s', index '%s'"
                        raise ValueError, msg % (str(param_value), self.name, index)
                    self._data[index] = param_value
        #
        if self.repn_type != 'pyomo_dict':
            self._model().__dict__[self.name] = self._data.model_repn()

    def _valid_indexed_value(self, value, index, use_exception):
        if index is ():
            if None not in self._index:
                msg = "Invalid index '%s' for parameter '%s'"
                raise ValueError, msg % ( str(None), self.name )
        elif type(index) is tuple and len(index)==1:
            if index not in self._index and index[0] not in self._index:
                msg = "Invalid index '%s' for parameter '%s'"
                raise ValueError, msg % ( str(index[0]), self.name)
        elif index not in self._index:
            msg = "Invalid index '%s' for parameter '%s'"
            raise ValueError, msg % ( str(index), self.name)
        #
        if self._validate is not None:
            if index is None:
                tmp = ()
            elif index == ():
                tmp = (None,)*self._ndim 
            else:
                tmp = index

            if apply_parameterized_indexed_rule(
                self, self._validate, self._model(), value, tmp ):
                return True
        #
        elif self.domain is Any or value in self.domain:
            return True
        #
        if use_exception:           #pragma:nocover
            msg = "Invalid value '%s' for parameter '%s'"
            raise ValueError, msg % ( str(value), self.name )
        #
        return False

    def data(self):
        return self._data.data()


class _ParamElement(_ParamBase, _ParamData):

    def __init__(self, *args, **kwds):

        repn_name = kwds.get('repn', 'pyomo_dict')

        _ParamBase.__init__(self, *args, **kwds)
        _ParamData.__init__(self, kwds.get('name',None), kwds.get('within',Any), kwds.get('default',None))

        if repn_name == 'pyomo_dict':
            self._data.set_item(None, self)
        else:
            self._data.set_item(None, self._default.value)

    def __getstate__(self):
        parambase_result = _ParamBase.__getstate__(self)
        paramvalue_result = _ParamData.__getstate__(self)
        return dict(parambase_result.items() + paramvalue_result.items())   

    def __setstate__(self, state):
        for (slot_name, value) in state.iteritems():
            setattr(self, slot_name, value)
        
    def __len__(self):
        return 1

    def keys(self):
        return [None]

    def __getitem__(self, key):
        if not key is None:
            raise KeyError, "Undefined key %s for parameter %s" % (key, self.name)
        return _ParamBase.__getitem__(self,key)

    def __setitem__(self, key, value):
        if not key is None:
            raise KeyError, "Undefined key %s for parameter %s" % (key, self.name)
        return _ParamBase.__setitem__(self,key,value)        

    def check_values(self):         #pragma:nocover
        #
        # Validate the values
        #
        if None not in self._index:
            raise ValueError, "Undefined value for parameter "+self.name
        if not self._valid_indexed_value(self.value,None,False):
            msg = "Parameter '%s' failed validation test.  Value: %s"
            raise ValueError, msg % ( self.name, str(self.value) )

    def __call__(self, exception=True):
        return self.value


class _ParamArray(_ParamBase):

    def __init__(self, *args, **kwds):
        _ParamBase.__init__(self, *args, **kwds)

    def __float__(self):
        msg = "Cannot access the value of array parameter '%s'"
        raise ValueError, msg % self.name

    def __int__(self):
        msg = "Cannot access the value of array parameter '%s'"
        raise ValueError, msg % self.name

    def set_value(self, value):
        for key in self._data:
            self.__setitem__(key,value)

    def check_values(self):         #pragma:nocover
        #
        # Validate the values
        #
        for key in self._data:
            if key not in self._index:
                msg = "Undefined value for parameter %s[%s]"
                raise ValueError, msg % ( self.name, str(key) )

            val = self._data(key)
            if not self._valid_indexed_value( val, key, False ):
                msg = "Parameter %s[%s] failed validation test.  Value: %s"
                raise ValueError, msg % ( self.name, str(key), str(tval) )

    def reset(self):
        pass                        #pragma:nocover

    def display(self, ostream=None):
        self.pprint(ostream=ostream)

    def __str__(self):
        return str(self.name)


class Param(Component):
    """
    Data objects that are used to construct Pyomo models.
    """

    alias("Param", "Parameter data that is used to define a model instance.")

    def __new__(cls, *args, **kwds):
        if args == ():
            self = _ParamElement(*args, **kwds)
        else:
            self = _ParamArray(*args, **kwds)
        return self
