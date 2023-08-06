#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

"""
Block Properties:

1. Blocks are indexed components that contain other components
   (including blocks)

2. Blocks have a global attribute that defines whether construction is
   deferred.  This applies to all components that they contain except
   blocks.  Blocks contained by other blocks use their local attribute
   to determine whether construction is deferred.

NOTE: Blocks do not currently maintain statistics about the sets,
parameters, constraints, etc that they contain, including these
components from subblocks.
"""

__all__ = ['Block']

import sys
import weakref

from plugin import *

from pyutilib.component.core import alias, ExtensionPoint
from pyutilib.misc import Container

from component import Component
from sets import Set, _SetContainer, _BaseSet
from rangeset import RangeSet
from var import Var
from constraint import Objective, Constraint
from param import Param
from misc import apply_parameterized_indexed_rule
from set_types import IntegerSet, BooleanSet

from indexed_component import IndexedComponent
try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

import logging
logger = logging.getLogger('coopr.pyomo')


class BlockComponents(object):

    #
    # IMPT: Default __getstate__ and __setstate__ are fine - this class owns no weakrefs or slots.
    #

    def __init__(self):
        #
        # Define component dictionary: component type -> instance
        #
        self._component={}
        for item in ModelComponentFactory.services():
            self._component[  ModelComponentFactory.get_class(item) ] = OrderedDict()
        #
        # A list of the declarations, in the order that they are
        # specified.
        #
        self._declarations=OrderedDict()

    def __getitem__(self, name):
        if isinstance(name,basestring):
            return self._declarations.get(name, None)
        return self._component.get(name, None)

    def _clear_attribute(self, name):
        val = self[name]
        if val is None:
            return

        if (type(val) == weakref and isinstance(val(), Block)):
            val().__dict__['_parent'] = None
            val()._model = weakref.ref(val)
        elif isinstance(val, Block):
            val.__dict__['_parent'] = None
            val._model = weakref.ref(val)
        else:
            val._model = None
            val._parent = None

        del self._component[ val.type() ][name]
        del self._declarations[name]
        self.__dict__[name]=None

    def _add_component(self, name, val):
        self._component[val.type()][name]=val
        self._declarations[name] = val
        self.__dict__[name]=val

    def __setattr__(self,name,val):
            #
            # Try to set the value. This may fail if the attribute
            # does not already exist in this model, if the set_value
            # function is not defined, or if a bad value is
            # provided. In the latter case, a ValueError will be
            # thrown, which we raise. Otherwise, this is an object
            # that we need to set directly.
            #
        try:
            self.__dict__[name].set_value(val)
        except ValueError, e:
            raise
        except Exception, e:
            self.__dict__[name]=val

    def keys(self):
        return self._declarations.keys()

    def __iter__(self):
        return self._declarations.iterkeys()

    def iterkeys(self):
        return self._declarations.iterkeys()

    def itervalues(self):
        return self._declarations.itervalues()

    def iteritems(self):
        return self._declarations.iteritems()

    def contains_component(self, ctype):
        return ctype in self._component

    def components(self, ctype=None):
        """
        Return information about the block components.  If ctype is None, return the dictionary
        that maps {component type -> {name -> instance}}.  Otherwise, return the dictionary
        that maps {name -> instance} for the specified component type.
        """
        if ctype is None:
            return self._component
        if ctype in self._component:
            return self._component[ctype]
        # FIXME: is this really an exception?  Shouldn't it return {}?
        raise KeyError, "Unknown component type: %s" % str(ctype)

    def active_components(self, _ctype=None):
        """
        Returns the active components in this block.  If _ctype is None, return the
        dictionary that maps {component type -> {name -> instance}}.  Otherwise, return
        the dictionary that maps {name -> instance} for the specified component type.
        """
        tmp = {}
        if _ctype is None:
            for ctype in self._component:
                tmp[ctype]=OrderedDict()
        elif _ctype in self._component:
            tmp[_ctype]=OrderedDict()
        else:
            raise KeyError, "Unknown component type: %s" % str(_ctype)
        for ctype in tmp:
            for name in self._component[ctype]:
                comp = self._component[ctype][name]
                if comp.active:
                    tmp[ctype][name] = comp
        if not _ctype is None:
            return tmp[_ctype]
        return tmp

    def is_constructed(self):
        """
        A boolean indicating whether or not all *active* components of the
        input model have been properly constructed.
        """
        component_map = arg.active_components()
        for type, entries in component_map.iteritems():
            for component_name, component in entries.iteritems():
                if component.is_constructed() is False:
                    return False
        return True

    def pprint(self, filename=None, ostream=None, verbose=False):
        """
        Print a summary of the model info
        """
        if ostream is None:
            ostream = sys.stdout
        if filename is not None:
            OUTPUT=open(filename,"w")
            self.pprint(ostream=OUTPUT, verbose=verbose)
            OUTPUT.close()
            return
        if ostream is None:
            ostream = sys.stdout
        #
        # We hard-code the order of the core Pyomo modeling
        # components, to ensure that the output follows the logical order
        # that expected by a user.
        #
        items = [Set, RangeSet, Param, Var, Objective, Constraint, Block]
        for item in ExtensionPoint(IModelComponent):
            if not item in items:
                items.append(item)

        # Currently, model components are not actually being registered
        # with the IModelComponent extension point (1 Nov 2010), so as a
        # workaround, we will loop through the components and add any
        # new components that actually have defined members.
        extra_items = []
        for item, members in self._component.iteritems():
            if item not in items and len(members):
                extra_items.append(item)
        # extra items get added alphabetically (so output is consistent)
        items.extend(sorted(extra_items))

        for item in items:
            if not item in self._component:
                continue
            keys = self._component[item].keys()
            keys.sort()
            #
            # NOTE: these conditional checks should not be hard-coded.
            #
            print >>ostream, len(keys), item.__name__+" Declarations"
            for key in keys:
                self._component[item][key].pprint(ostream=ostream, verbose=verbose)
            print >>ostream, ""
        #
        # Model Order
        #
        print >>ostream, len(self._declarations),"Declarations:",
        for name in self._declarations:
            print >>ostream, name,
        print >>ostream, ""


class Block(IndexedComponent):
    """
    A block in an optimization model.  By default, this defers construction of
    components until data is loaded.
    """

    alias("Block", "Blocks are indexed components that contain one or more " + \
          "other model components.")

    #
    # IMPT: Must over-ride __getstate__ and __setstate__ - this class owns 
    #       weakrefs via the '_model' and '_parent' attributes.
    #

    def __init__(self, *args, **kwargs):
        """Constructor"""
        self._rule = kwargs.pop('rule', None )
        kwargs.setdefault('ctype', Block)
        IndexedComponent.__init__(self, *args, **kwargs)
        #
        self._constructed = False
        self._defer_construction=True
        # By default, a Block is a top-level (i.e. Model) block
        self._model = weakref.ref(self)
        self._parent = None
        self.components =  BlockComponents()

    def __getstate__(self):

         return IndexedComponent.__getstate__(self)

    def __setstate__(self, state):

        IndexedComponent.__setstate__(self, state)
        if '_parent' in self.__dict__.keys() and self._parent is not None and type(self._parent) != weakref.ref:
            self._parent = weakref.ref(self._parent)
      
    def all_blocks(self, blockList=None):
        ans = blockList or [ self ]
        subBlocks = self.components.components(Block).values()
        ans.extend(subBlocks)
        for block in subBlocks:
            block.all_blocks(ans)
        return ans

    def block_namespace(self):
        fullName = ''
        b = self
        while b._parent is not None and b._parent() is not None:
            fullName = b.name + '.' + fullName
            b = b._parent()
        return fullName


    def concrete_mode(self):
        """Configure block to immediately construct components"""
        self._defer_construction=False

    def symbolic_mode(self):
        """Configure block to defer construction of components"""
        self._defer_construction=True

    def components(self, ctype=None):
        """
        Return information about the block components.  If ctype is None, return the dictionary
        that maps {component type -> {name -> instance}}.  Otherwise, return the dictionary
        that maps {name -> instance} for the specified component type.
        """
        return self.components.components(ctype)

    def active_components(self, _ctype=None):
        """
        Returns the active components in this block.  If _ctype is None, return the
        dictionary that maps {component type -> {name -> instance}}.  Otherwise, return
        the dictionary that maps {name -> instance} for the specified component type.
        """
        return self.components.active_components(_ctype)

    def has_discrete_variables(self):

        for variable_name, variable in self.active_components(Var).items():
            if isinstance(variable.domain, IntegerSet) or isinstance(variable.domain, BooleanSet):
                return True

        for block in self.components.components(Block).values():
           if block.has_discrete_variables() is True:
              return True
            
        return False

    def find_component(self, label):
        cList = label.split('.')
        obj = self
        while cList:
            c = cList.pop(0).split(':')
            if len(c) > 1:
                idx = c[1].split(',')
                for i, val in enumerate(idx):
                    if val[0]=='#':
                        idx[i] = int(val[1:])
                    elif val[0]=='$':
                        idx[i] = val[1:]
                    elif val[0]=='!':
                        idx[i] = None
                    else:
                        # last-ditch effort to find things
                        try:
                            tmp = int(val)
                            idx[i] = tmp
                        except ValueError:
                            pass
                        #raise ValueError(
                        #    "missing index type specifier for index %s in canonical label %s" % (val,label) )
                if len(idx) > 1:
                    idx = tuple(idx)
                else:
                    idx = idx[0]
            else:
                idx = None
            try:
                obj = getattr(obj, c[0])[idx]
            except AttributeError:
                return None
        return obj

    def construct(self, data=None):
        if __debug__ and logger.isEnabledFor(logging.DEBUG):
            logger.debug( "Constructing %s %s",
                          self.__class__.__name__, self.name )
        if self._constructed:
            return
        self._constructed=True
        if self._rule is None:
            # FIXME: The following code needs to be re-established once the "FIXME" 
            #        on line 175 of PyomoModel.py is addressed.
#            logger.warn("No construction rule or expression specified for "
#                        "%s '%s'", self.__class__.__name__, self.name)
            return

        def _generate_name(idx):
            if type(idx) in (tuple, list):
                return '['+','.join([_generate_name(x) for x in idx])+']'
            else:
                return str(idx)

        for val in self._index:
            name = _generate_name(val)
            if __debug__ and logger.isEnabledFor(logging.DEBUG):
                logger.debug( "   Constructing %s index %s",
                              self.__class__.__name__, str(name) )
            if val is None:
                apply_parameterized_indexed_rule(
                    self, self._rule, self._model(), self, () )
            else:
                block = self.__class__()
                self._add_component(name, block)
                apply_parameterized_indexed_rule(
                    self, self._rule, self._model(), block, val )
                for tmp in block.components.itervalues():
                    tmp.construct(None)
                self._data[val] = block
        #self._index=constructed_indices

    def _add_temporary_set(self,val):
        if val._index_set is not None:
            ctr=0
            for tset in val._index_set:
                if tset.name == "_unknown_":
                    self._construct_temporary_set(
                      tset,
                      val.name+"_index_"+str(ctr)
                    )
                ctr += 1
            val._index = self._construct_temporary_set(
              val._index_set,
              val.name+"_index"
            )
        if isinstance(val._index,_SetContainer) and \
            val._index.name == "_unknown_":
            self._construct_temporary_set(val._index,val.name+"_index")
        if getattr(val,'domain',None) is not None and val.domain.name == "_unknown_":
            self._construct_temporary_set(val.domain,val.name+"_domain")

    def _construct_temporary_set(self, obj, name):
        if type(obj) is tuple:
            if len(obj) == 1:                #pragma:nocover
                raise Exception, "Unexpected temporary set construction"
            else:
                tobj = obj[0]
                for t in obj[1:]:
                    tobj = tobj*t
                setattr(self,name,tobj)
                tobj.virtual=True
                return tobj
        if isinstance(obj,_BaseSet):
            setattr(self,name,obj)
            return obj

    def _clear_attribute(self, name, only_block=False):
        """
        Cleanup the pre-existing model attribute
        """
        #
        # We don't delete here because that would destruct the component, which might
        # be shared with another block.
        #
        self.__dict__[name]=None
        if only_block:
            return

        self.components._clear_attribute(name)

    def _add_component(self, name, val):
        if not val.valid_model_component():
            raise RuntimeError, "Cannot add '%s' as a component to a model" % str(type(val))
        self._clear_attribute(name)

        # all Pyomo components have names. 
        val.name=name

        self._add_temporary_set(val)
        self.components._add_component(name,val)
        self.__dict__[name]=val

        # Presumably self._model refers to the 'root' Block that will
        # eventually be solved, whereas '_parent' refers to the
        # immediate parent.

        # Update the (new) child block's parent.
        if isinstance(val, Block):
            if val._parent is not None and val._parent() is not None:
                # Nothing really wrong here, but until we are more
                # careful about checking that this actually works,
                # complain loudly.
                print "WARNING: Reassigning a block attached to a model"
            # NB: use __dict__ directly to prevent infinite recursion
            val.__dict__['_parent'] = weakref.ref(self)
        else:
            val._parent = weakref.ref(self)

        # Update the new component's model pointer
        val._model = self._model

        # Support implicit rule names
        frame = sys._getframe(2)
        locals_ = frame.f_locals
        if getattr(val,'rule',None) is None and val.name+'_rule' in locals_:
            val.rule = locals_[val.name+'_rule']
        if not self._defer_construction:
            val.construct(None)

    def __setattr__(self,name,val):
        """Set attributes"""
        #
        # Set Model Declaration
        #
        if name == '_model':
            if val is not None and not isinstance(val, Block) and \
                    not (type(val) == weakref.ref and isinstance(val(), Block)):
                raise ValueError, "Cannot set Block._model to a non-Block " \
                      "object (%s)" % ( val )
            self.__dict__['_model'] = val
            # Update all child components.  
            #
            # NB: use __dict__.get because Component.__init__() assigns
            # "self._model = None" before Block.__init__ defines the
            # _declarations map.
            #
            # NB: this recursion is critical for pickling to work: when
            # the model is pickled, its __getstate__ reassigns the
            # weakref model pointer to a hard reference, which trickles
            # down to all child components through here.
            components = self.__dict__.get('components', None)
            if not components is None:
                for subcomp in components.itervalues():
                    subcomp._model = val
        elif name == '_parent':
            if val is not None and not isinstance(val, Block) and \
                    not (type(val) == weakref.ref and isinstance(val(), Block)):
                raise ValueError, "Cannot set the '_parent' attribute of a Block with name=%s to a non-Block object with type=%s; Did you introduce a model component named '_parent'?" % (self.name, type(val))
            self.__dict__['_parent'] = val
        elif name != 'components' and name != '_index' \
                 and isinstance(val, Component):
            #
            # If this is a component type, then simply set it
            #
            self._add_component(name,val)
        else:
            #
            # Try to set the value. This may fail if the attribute
            # does not already exist in this model, if the set_value
            # function is not defined, or if a bad value is
            # provided. In the latter case, a ValueError will be
            # thrown, which # we raise. Otherwise, this is an object
            # that we need to set directly.
            #
            try:
                self.__dict__[name].set_value(val)
            except ValueError, e:
                raise
            except Exception, e:
                self.__dict__[name]=val

    def pprint(self, filename=None, ostream=None, verbose=False):
        """
        Print a summary of the model info
        """
        self.components.pprint(filename=filename, ostream=ostream, verbose=verbose)

    def display(self, filename=None, ostream=None):
        """
        Print the Pyomo model in a verbose format.
        """
        if filename is not None:
            OUTPUT=open(filename,"w")
            self.display(ostream=OUTPUT)
            OUTPUT.close()
            return
        if ostream is None:
            ostream = sys.stdout
        if self._parent is not None and self._parent() is not None:
            print >>ostream, "Block "+self.name
        else:
            print >>ostream, "Model "+self.name
        #
        print >>ostream, ""
        print >>ostream, "  Variables:"
        VAR = self.active_components(Var)
        if len(VAR) == 0:
            print >>ostream, "    None"
        else:
            for ndx in VAR:
                VAR[ndx].display(prefix="    ",ostream=ostream)
        #
        print >>ostream, ""
        print >>ostream, "  Objectives:"
        OBJ = self.active_components(Objective)
        if len(OBJ) == 0:
            print >>ostream, "    None"
        else:
            for ndx in OBJ:
                OBJ[ndx].display(prefix="    ",ostream=ostream)
        print >>ostream, ""
        #
        CON = self.active_components(Constraint)
        print >>ostream, "  Constraints:"
        if len(CON) == 0:
            print >>ostream, "    None"
        else:
            for ndx in CON:
                CON[ndx].display(prefix="    ",ostream=ostream)
