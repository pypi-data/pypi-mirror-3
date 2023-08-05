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

from component import Component
from sets import _BaseSet, Set, set_options


class IndexedComponent(Component):

    #
    # IMPT: Technically doesn't need to over-ride __getstate__ and __setstate__, as this
    #       class doesn't directly own weakrefs or slots. However, we are providing them
    #       presently as pass-thrus, just in case they are added.
    #
    
    def __init__(self, *args, **kwds):
        doc = kwds.pop('doc', None)
        #
        # The default ctype is None, which triggers an error in the
        # Component base class.
        #
        component_type = kwds.pop('ctype', None)
        if kwds:
            raise ValueError(
                "Unexpected keyword options found while constructing '%s':\n\t%s",
                ( type(self).__name__, ','.join(sorted(kwds.keys())) ))
        Component.__init__(self, component_type)
        self.doc = doc

        self._ndim=0
        self._index_set=None
        self._index={}
        if len(args) == 0:
            self._index={None:None}
        elif len(args) == 1:
            if isinstance(args[0],_BaseSet):
                self._index=args[0]
            elif isinstance(args[0],IndexedComponent):
                raise TypeError, "Cannot index a component with a non-set component"
            else:
                try:
                    options = getattr(args[0],'set_options')
                    options['initialize'] = args[0]
                    self._index=Set(**options)
                except:
                    self._index=Set(initialize=args[0])
        else:
            tmp = []
            for arg in args:
                if isinstance(arg,_BaseSet):
                    tmp.append(arg)
                elif isinstance(arg,IndexedComponent):
                    raise ValueError, "Cannot index a component with a non-set component"
                else:
                    try:
                        options = getattr(arg,'set_options')
                        options['initialize'] = arg
                        tmp.append( Set(**options) )
                    except:
                        tmp.append( Set(initialize=arg) )
            self._index_set=tuple(tmp)
        self._compute_dim()

    def __getstate__(self):
        return Component.__getstate__(self)

    def __setstate__(self, state):
        return Component.__setstate__(self, state)

    def index(self):
        return self._index

    def _compute_dim(self):
        if self._ndim is None or self._ndim is 0:
            if self._index_set is None:
                if type(self._index) is dict:
                    if len(self._index) is 0:
                        self._ndim = 0
                    else:
                        val = self._index[self._index.keys()[0]]
                        if type(val) is tuple:
                            self._ndim = len(val)
                        elif val is None:
                            self._ndim = 0
                        else:
                            self._ndim = 1
                else:
                    self._ndim = self._index.dimen
            else:
                self._ndim = 0
                for iset in self._index_set:
                    self._ndim += iset.dimen
