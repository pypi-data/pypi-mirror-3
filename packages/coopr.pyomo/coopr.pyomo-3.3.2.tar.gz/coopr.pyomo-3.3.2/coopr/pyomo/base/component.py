#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

__all__ = ['Component']

import weakref

from pyutilib.component.core import Plugin, implements
from plugin import IModelComponent


class Component(Plugin):
    """
    This is the base class for all Pyomo modeling components.
    This class is derived from the PyUtilib Plugin class, which
    allows components to be instantiated from a plugin factory.

    Constructor arguments:
        ctype           The class type for the derived subclass
        doc             A text string describing this component
        name            A name for this component

    Public class attributes:
        active          A boolean that is true if this component will be 
                            used to construct a model instance
        doc             A text string describing this component

    Private class attributes:
        _constructed    A boolean that is true if this component has been
                            constructed
        _model          A weakref to the model that owns this component
        _parent         A weakref to the parent block that owns this component
        _type           The class type for the derived subclass
    """

    #
    # This plugin class implements the IModelComponent interface.  This is
    # is not a service plugin, so no plugin instance is created by default.
    #
    implements(IModelComponent, service=False)

    def __init__ (self, **kwds):
        #
        # Get arguments
        #
        self.doc   = kwds.pop('doc', None)
        self.name  = kwds.pop('name', None)
        self._type = kwds.pop('ctype', None)
        if kwds:
            raise ValueError(
                "Unexpected keyword options found while constructing '%s':\n\t%s"
                % ( type(self).__name__, ','.join(sorted(kwds.keys())) ))
        #
        # Verify that ctype has been specified.
        #
        if self._type is None:
            raise DeveloperError, "Must specify a class for the component type!"
        #
        self.active = True
        self._constructed = False
        self._model = None     # Must be a weakref
        self._parent = None    # Must be a weakref

    def __getstate__(self):
        """
        This method must be defined to support pickling because this class
        owns weakrefs for '_model' and '_parent'.
        """
        result = dict(self.__dict__.items())
        if ('_model' in result) and (type(result['_model']) is weakref.ref):
            result['_model'] = result['_model']()
        if ('_parent' in result) and (type(result['_parent']) is weakref.ref):
            result['_parent'] = result['_parent']()
        return result

    def __setstate__(self, state):
        """
        This method must be defined to support pickling because this class
        owns weakrefs for '_model' and '_parent'.
        """
        for (slot_name, value) in state.iteritems():
            self.__dict__[slot_name] = value
        if '_model' in self.__dict__.keys() and self._model is not None and type(self._parent) != weakref.ref:
            self._model = weakref.ref(self._model)
        if '_parent' in self.__dict__.keys() and self._parent is not None and type(self._parent) != weakref.ref:
            self._parent = weakref.ref(self._parent)

    def activate(self):
        """Set the active attribute to True"""
        self.active=True

    def deactivate(self):
        """Set the active attribute to False"""
        self.active=False

    def type(self):
        """Return the class type for this component"""
        return self._type

    def construct(self, data=None):                     #pragma:nocover
        """API definition for constructing components"""
        pass

    def is_constructed(self):                           #pragma:nocover
        """Return True if this class has been constructed"""
        return self._constructed

    def valid_model_component(self):
        """Return True if this can be used as a model component."""
        return True

    def pprint(self, ostream=None, verbose=False):
        """Print component information"""
        if ostream is None:
            ostream = sys.stdout
        print >>ostream, "  ",self.name,":",


class DeveloperError(Exception):
    """
    Exception class used to throw errors that result from
    programming errors, rather than user modeling errors (e.g., a
    component not declaring a 'ctype').
    """

    def __init__(self, val):
        self.parameter = val

    def __str__(self):                                  #pragma:nocover
        return repr(self.parameter)

