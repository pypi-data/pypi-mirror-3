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

from component import *
from indexed_component import IndexedComponent
from misc import apply_indexed_rule, apply_parameterized_indexed_rule
from numvalue import create_name, value
from plugin import ParamRepresentationFactory
from pyutilib.component.core import alias
from set_types import *
from sets import _BaseSet
from param_repn import _ParamValue

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
        tkwd = {'ctype': kwd.pop("ctype", Param), 'doc':kwd.pop('doc',None)}
        IndexedComponent.__init__(self, *args, **tkwd)

        self._initialize = kwd.pop('initialize', None )
        self._initialize = kwd.pop('rule', self._initialize )
        self._validate   = kwd.pop('validate', None )
        self.domain      = kwd.pop('within', Any )
        self.name        = kwd.pop('name', 'unknown')
        self.nochecking  = kwd.pop('nochecking',False)
        defaultval       = kwd.pop('default', None )

        self._default = _ParamValue(
            name   = self.name,
            domain = self.domain,
            value  = value(defaultval)
            )

        self.repn_type = kwd.pop('repn', 'pyomo_dict')
        self._repn        = ParamRepresentationFactory( self.repn_type, args=(self,) )
        if self._repn is None:
            raise ValueError, "Unknown parameter representation '%s'" % self.repn_type

        if ( kwd ):
            msg = "Unknown keywords to Param constructor: %s"
            raise ValueError, msg % repr(kwd)

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
                print >>ostream, "\t", self._repn(None)
            else:
                print >>ostream, "\t", "Not constructed"
        else:
            tmp=self._repn.keys(nondefault=True)
            tmp.sort()
            for key in tmp:
                val = self._repn(key)
                print >>ostream, "\t"+str(key)+" : "+str(val)
        if self._default.value is not None and not self._default.value is None:
            print >>ostream, "\tdefault: "+str(self._default.value)

    def keys(self):
        return self._repn.keys()

    # a utiliy to extract all index-value pairs defining this
    # parameter, returned as a dictionary. useful in many
    # contexts, in which key iteration and repeated __getitem__
    # calls are too expensive to extract the contents of a parameter.
    # NOTE: We are presently not careful if an index has not been
    #       explicitly defined - issues around defaults are bound
    #       to crop up.
    def extract_values(self):
        return self._repn.extract_values()

    # a utility to set values of a parameter "in bulk", using a dictionary of index<->value pairs.
    # far more efficient in some contexts than the approach of doing things by-index in an outer loop.    
    def store_values(self, new_values):
        return self._repn.store_values(new_values)

    def __contains__(self, element):
        return element in self._repn

    def __iter__(self):
        return self._repn.__iter__()

    def set_default(self, value):
        self._default.value = value
        self._repn.set_default(value)

    def as_numeric(self):
        if None in self._repn:
            return self._repn[None]
        return self

    def is_indexed(self):
        return self._ndim > 0

    def is_expression(self):
        return False

    def is_relational(self):
        return False

    def dim(self):
        return self._ndim

    def __len__(self):
        return len(self._repn)

    def __getitem__(self,ndx):
        """This method returns a _ParamVal object.  This object can be
           coerced to a numeric value using the value() function, or using
           explicity coercion with float().
        """
        return self._repn[ndx]

    def __setitem__(self, ndx, val):
        if self._index_set is not None:
            # this is a "hack", in that we still need to check for legal
            # sub-components in the input index.
            self._repn[ndx] = val
            return

        # why do we have this test / transformation?
        if type(ndx) is tuple and len(ndx) == 1 and ndx[0] in self._index:
            ndx = ndx[0]

        # a somewhat gory way to see if you have a singleton - the len()=1 check is needed to avoid "None" 
        # being passed illegally into set membership validation rules. the nochecking screen saves 
        # significant time here, as the len() computation is remarkably expensive.
        if (self.nochecking is False) and (len(self._index) == 1) and (None in self._index) and (ndx is not None):  
            # allow for None indexing only if this is truly a singleton
            msg = "Cannot set an array value in the simple parameter '%s'"
            raise KeyError, msg % self.name
        #
        if (self.nochecking is False) and (ndx not in self._index):
            msg = "Cannot set the value of array parameter '%s' with invalid " \
                  "index '%s'"
            raise KeyError, msg % ( self.name, str(ndx) )
        #
        self._repn[ndx] = val
        #
        # This is at the end, so the user can write their validation
        # tests as if the data was already added.
        #
        if (self.nochecking is False) and (not self._valid_indexed_value(val ,ndx, False)):

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
        self._constructed=True
        #
        # Code optimization with local variables
        #
        _name=self.name
        _domain=self.domain
        #
        self._repn.update_index()
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
            #print self._repn, self._initialize, self._default.value, self._index
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
                        self._repn.set_item(val=self._initialize)
        #
        # Construct using the rule
        #
        elif type(self._initialize) is types.FunctionType:
            if (type(self._index) is dict) and (None in self._index):
                # singleton
                self.value = self._initialize(self.model())
                self[None] = self.value
            else:
                # non-singleton
                for val in self._index:
                    self.__setitem__( val, apply_indexed_rule(
                            self, self._initialize, self.model(), val ) )
        #
        if self.repn_type != 'pyomo_dict':
            self.model().__dict__[self.name] = self._repn.model_repn()

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
                self, self._validate, self.model(), value, tmp ):
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
        return self._repn.data()


class _ParamElement(_ParamBase, _ParamValue):

    def __init__(self, *args, **kwds):

        repn_name = kwds.get('repn', 'pyomo_dict')

        _ParamBase.__init__(self, *args, **kwds)
        _ParamValue.__init__(self, name=kwds.get('name',None), domain=kwds.get('within',Any), value=kwds.get('default',None))

        if repn_name == 'pyomo_dict':
            self._repn.set_item(None, self)
        else:
            self._repn.set_item(None, self._default.value)

    def __getstate__(self):

        parambase_result = _ParamBase.__getstate__(self)
        paramvalue_result = _ParamValue.__getstate__(self)
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
        for key in self._repn:
            self.__setitem__(key,value)

    def check_values(self):         #pragma:nocover
        #
        # Validate the values
        #
        for key in self._repn:
            if key not in self._index:
                msg = "Undefined value for parameter %s[%s]"
                raise ValueError, msg % ( self.name, str(key) )

            val = self._repn(key)
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
