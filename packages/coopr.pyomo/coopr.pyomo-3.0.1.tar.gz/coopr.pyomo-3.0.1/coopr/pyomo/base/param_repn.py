#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

__all__ = ['_ParamValue']

from numvalue import NumericConstant
from pyutilib.component.core import *
from plugin import IParamRepresentation
from pyutilib.misc import SparseMapping
from numvalue import create_name


class SparseMappingRepn(Plugin):

    implements(IParamRepresentation, service=False)

    alias('sparse_dict', 'A class that manages the sparse dictionary parameter representation, which maps keys to numeric values while respecting default values')

    def __init__(self, param):
        self._paramdata = SparseMapping(default=param._default.value, index=param._index, within=param.domain)
        self._param = param

    def model_repn(self):
        if None in self.keys():
            return self._paramdata[None]
        return self._paramdata

    def set_default(self, value):
        self._paramdata.default = value

    def update_index(self):
        self._paramdata.index = self._param._index

    def data(self):
        return self._paramdata

    def keys(self, nondefault=False):
        if nondefault:
            self._paramdata.nondefault_keys()
        return self._paramdata.keys()

    # a utiliy to extract all index-value pairs defining this
    # parameter, returned as a dictionary. useful in many
    # contexts, in which key iteration and repeated __getitem__
    # calls are too expensive to extract the contents of a parameter.
    # NOTE: We are presently not careful if an index has not been
    #       explicitly defined - issues around defaults are bound
    #       to crop up. specifically, we're assuming here that
    #       all indices are represented in _paramdata.
    def extract_values(self):
        raise RuntimeError, "extract_values method not yet implemented for SparseMappingRepn"

    def store_values(self, new_values):
        raise RuntimeError, "store_values method not yet implemented for SparseMappingRepn"    

    def __contains__(self, key):
        return key in self._paramdata

    def __iter__(self):
        return self._paramdata.__iter__()

    def __len__(self):
        return len(self._paramdata)

    def __getitem__(self, key):
        return self._paramdata[key]

    def __setitem__(self,key,val):
        self._paramdata[key] = val

    def set_item(self, key=None, val=None):
        if key is None:
            self._param._default.value = val
            self._paramdata = SparseMapping(default=self._param._default.value, index=self._param._index, within=self._param.domain)
        else:
            self._paramdata.set_item(key,val)

    def __call__(self, key):
        return self._paramdata[key]


class _ParamValue(NumericConstant):
    """Holds the numeric value of a parameter"""

    __slots__ = []

    """Constructor"""
    def __init__(self, name=None, domain=None, value=None):
        try:
            NumericConstant.__init__(self, name, domain, value)
        except ValueError, e:
            msg = "Problem constructing parameter %s : %s"
            raise ValueError, msg % (name, str(e))

    def fixed_value(self):
        return True

    def __str__(self):
        return self.name


class DefaultRepn(Plugin):

    implements(IParamRepresentation, service=False)

    alias('pyomo_dict', 'A class that manages the default Pyomo parameter representation, which maps keys to ParamValue objects')

    def __init__(self, param):
        self._paramdata = {} # mapping between indicies and _ParamValue objects.
        self._default = param._default
        self._index = param._index
        self._param = param

    def model_repn(self):
        return self._param

    def set_default(self, value):
        pass

    def update_index(self):
        self._index = self._param._index

    def data(self):
        tmp = SparseMapping(default=self._default.value, index=self._param._index, within=self._param.domain)
        for key in self._paramdata.keys():
            tmp[key] = self._paramdata[key].value
        return tmp

    def keys(self, nondefault=False):
        if nondefault or self._default.value is None:
            return self._paramdata.keys()
        return self._index

    # a utiliy to extract all index-value pairs defining this
    # parameter, returned as a dictionary. useful in many
    # contexts, in which key iteration and repeated __getitem__
    # calls are too expensive to extract the contents of a parameter.
    # NOTE: We are presently not careful if an index has not been
    #       explicitly defined - issues around defaults are bound
    #       to crop up. specifically, we're assuming here that
    #       all indices are represented in _paramdata.
    def extract_values(self):
        return dict(((index, paramval.value) for index, paramval in self._paramdata.iteritems()))

    # a utility to set values of a parameter "in bulk", using a dictionary of index<->value pairs.
    # far more efficient in some contexts than the approach of doing things by-index in an outer loop.
    def store_values(self, new_values):
        for index, new_value in new_values.iteritems():
            self._paramdata[index].value = new_value            

    def __contains__(self, key):
        if self._default.value is None:
            return key in self._paramdata
        else:
            return key in self._index

    def __iter__(self):
        if self._default.value is None:
            return self._paramdata.keys().__iter__()
        else:
            return self._index.__iter__()

    def __len__(self):
        if self._default.value is None:
            return len(self._paramdata)
        return len(self._index)

    def __getitem__(self, key):
        if key in self._paramdata:
            return self._paramdata[key]
        if key in self._index:
            if self._default.value is not None:
                return self._default
            else: 
                raise ValueError( "Legal key '%s' for parameter '%s', but "
                                  "value is uninitialized and there is no "
                                  "default value" % (key, self._param.name) )
        raise KeyError( "Undefined key '%s' for parameter '%s'"
                        % (key, self._param.name) )

    def __setitem__(self,key,val):
        if key in self._paramdata:
            self._paramdata[key].value = val
        else:
            self._paramdata[key]= _ParamValue(
                        name   = create_name(self._param.name,key),
                        domain = self._param.domain,
                        value  = val
                        )

    def set_item(self, key=None, val=None):
        if key is None:
            self._paramdata = {}
            self._default.value = getattr(val,'value',val)
        else:
            self._paramdata[key] = val

    def __call__(self, key):
        return self.__getitem__(key).value
