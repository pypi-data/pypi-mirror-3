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

    implements(IModelComponent, service=False)

    #
    # IMPT: Must over-ride __getstate__ and __setstate__ - this class owns 
    #       a weakref via the 'model'.
    #

    def __init__ ( self, ctype=None, **kwargs ):
        # Error check for ctype
        if ctype is None:
            raise DeveloperError, "Must specify a class for the component type!"

        self.doc = None
        self.active=True
        self._type=ctype
        self._constructed=False
        # IMPT: the model attribute should be a weakref in all derived classes.
        # NOTE: JPW believes the base Component class should also have a 'parent'
        #       attribute defined and None-assigned by default, mirroring the 'model' attribute.
        self.model=None  # should be a weakref
        self.parent=None # should be a weakref

    def __getstate__(self):

        result = dict(self.__dict__.items())
        if ('model' in result) and (type(result['model']) is weakref.ref):
            result['model'] = result['model']()
        if ('parent' in result) and (type(result['parent']) is weakref.ref):
            result['parent'] = result['parent']()
        return result

    def __setstate__(self, state):

        for (slot_name, value) in state.iteritems():
            self.__dict__[slot_name] = value
        if 'model' in self.__dict__.keys() and self.model is not None and type(self.parent) != weakref.ref:
            self.model = weakref.ref(self.model)
        if 'parent' in self.__dict__.keys() and self.parent is not None and type(self.parent) != weakref.ref:
            self.parent = weakref.ref(self.parent)

    def activate(self):
        self.active=True

    def deactivate(self):
        self.active=False

    def type(self):
        return self._type

    def construct(self, data=None):
        pass

    def is_constructed(self):
        return self._constructed

    def valid_model_component(self):
        """Return true if this can be used as a model component."""
        return True



class DeveloperError(Exception):
    """
    Exception class used to throw errors stemming from Pyomo
    programming errors, rather than user modeling errors (e.g., a
    component not declaring a 'ctype')

    """

    def __init__(self, val):
        self.parameter = val

    def __str__(self):
        return repr(self.parameter)
