#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

__all__ = [ 'Connector' ]

import logging
import weakref

import sys

from block import Block
from component import Component
from constraint import Constraint, ConstraintList
from expr import _ProductExpression
from indexed_component import IndexedComponent
from numvalue import NumericValue
from plugin import IPyomoScriptModifyInstance
from var import VarList

from pyutilib.component.core import alias, Plugin, implements

logger = logging.getLogger('coopr.pyomo')

class _ConnectorValue(NumericValue):
    """Holds the actual connector information"""

    __slots__ = ('connector','index','vars','aggregators')

    def __init__(self, name):
        """Constructor"""

        # IMPT: The following three lines are equivalent to calling the
        #       basic NumericValue constructor, i.e., as follows:
        #       NumericValue.__init__(self, name, domain, None, False)
        #       That particular constructor call takes a lot of time
        #       for big models, and is unnecessary because we're not
        #       validating any values.
        self.name = name
        self.domain = None
        self.value = None

        # NOTE: the "name" attribute (part of the base NumericValue class) is
        #       typically something like some_var[x,y,z] - an easy-to-read
        #       representation of the variable/index pair.

        # NOTE: both of the following are presently set by the parent. arguably, we
        #       should provide keywords to streamline initialization.
        self.connector = None # the "parent" variable.
        self.index = None # the index of this variable within the "parent"
        self.vars = {}
        self.aggregators = {}
    
    def __str__(self):
        # the name can be None, in which case simply return "".
        if self.name is None:
            return ""
        else:
            return self.name

    def __getstate__(self):
        result = NumericValue.__getstate__(self)
        for i in _ConnectorValue.__slots__:
            result[i] = getattr(self, i)
        if type(result['connector']) is weakref.ref:
            result['connector'] = result['connector']()
        return result

    def __setstate__(self, dict):
        for (slot_name, value) in state.iteritems():
            self.__dict__[slot_name] = value
        if 'connector' in self.__dict__.keys() and self.connector is not None:
            self.connector = weakref.ref(self.connector)

    def set_value(self, value):
        msg = "Cannot specify the value of a connector '%s'"
        raise ValueError, msg % self.name

    def fixed_value(self):
        if len(self.vars) == 0:
            return False
        for var in self.vars.itervalues():
            if not var.fixed_value():
                return False
        return True

    def is_constant(self):
        for var in self.vars.itervalues():
            if not var.is_constant():
                return False
        return True

    def polynomial_degree(self):
        if self.fixed_value():
            return 0
        return 1

    def is_binary(self):
        for var in self.vars.itervalues():
            if var.is_binary():
                return True
        return False

    def is_integer(self):
        for var in self.vars.itervalues():
            if var.is_integer():
                return True
        return False

    def is_continuous(self):
        for var in self.vars.itervalues():
            if var.is_continuous():
                return True
        return False

    def pprint(self, ostream=None, verbose=False):
        if ostream is None:
            ostream = sys.stdout
        print >>ostream, str(self),

    def add(self, var, name=None, aggregate=None):
        if name is None:
            name = var.name
        if name in self.vars:
            raise ValueError("Cannot insert duplicate variable name "
                             "'%s' into Connector '%s'" % ( name, self.name ))
        self.vars[name] = var
        if aggregate is not None:
            self.aggregators[var] = aggregate


class _ConnectorBase(IndexedComponent):
    """A collection of variables, which may be defined over a index"""

    """ Constructor
        Arguments:
           name         The name of this connector
           index        The index set that defines the distinct connectors.
                          By default, this is None, indicating that there
                          is a single connector.
    """

    # TODO: default and rule keywords are not used?  Need to talk to Bill ...?
    def __init__(self, *args, **kwd):
        kwd.setdefault('ctype', Connector)
        IndexedComponent.__init__(self, *args, **kwd)
        self._conval = {}

    def as_numeric(self):
        if None in self._conval:
            return self._conval[None]
        return self

    def is_indexed(self):
        return self._ndim > 0

    def is_expression(self):
        return False

    def is_relational(self):
        return False

    def keys(self):
        return self._conval.keys()

    def __iter__(self):
        return self._conval.keys().__iter__()

    def iteritems(self):
        return self._conval.iteritems()

    def __contains__(self,ndx):
        return ndx in self._conval

    def dim(self):
        return self._ndim

    def __len__(self):
        return len(self._conval)

    def __getitem__(self,ndx):
        """This method returns a _ConnectorValue object.
        """
        try:
            return self._conval[ndx]
        except KeyError: # thrown if the supplied index is hashable, but not defined.
            msg = "Unknown index '%s' in connector %s;" % (str(ndx), self.name)
            if (isinstance(ndx, (tuple, list)) and len(ndx) != self.dim()):
                msg += "    Expecting %i-dimensional indices" % self.dim()
            else:
                msg += "    Make sure the correct index sets were used.\n"
                msg += "    Is the ordering of the indices correct?"
            raise KeyError, msg
        except TypeError, msg: # thrown if the supplied index is not hashable
            msg2 = "Unable to index connector %s using supplied index with " % self.name
            msg2 += str(msg)
            raise TypeError, msg2

    def _add_indexed_member(self, ndx):
        new_conval = _ConnectorValue(create_name(self.name,ndx))
        new_conval.component = weakref.ref(self)
        new_conval.index = ndx
        
        self._conval[ndx] = new_conval

    def construct(self, data=None):
        if __debug__:   #pragma:nocover
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug("Constructing Connector, name=%s, from data=%s", self.name, `data`)
        if self._constructed:
            return
        self._constructed=True
        #
        # Construct _VarData objects for all index values
        #
        if self._ndim > 0:
            if type(self._initialize) is dict:
                self._index = self._initialize.keys()

            for ndx in self._index:
                self._add_indexed_member(ndx)

        else:
            # if the dimension is a singleton (i.e., we're dealing
            # with a _ConElement), and the _varval is already initialized.
            pass

    def pprint(self, ostream=None, verbose=False):
        if ostream is None:
            ostream = sys.stdout
        print >>ostream, "  ",self.name,":",
        print >>ostream, "\tSize="+str(len(self)),
        if self._index_set is not None:
            print >>ostream, "\tIndicies: ",
            for idx in self._index_set:
                print >>ostream, str(idx.name)+", ",
            print ""
        if None in self._conval:
            print >>ostream, "\tName : Variable"
            for item in self._conval[None].iteritems():
                print >>ostream, "\t %s : %s" % item
        else:
            print >>ostream, "\tKey : Name : Variable"
            tmp=self._conval.keys()
            tmp.sort()
            for key in tmp:
                for name, var in self._conval[key].iteritems():
                    print >>ostream, "\t %s : %s : %s" % ( key, name, var )


    def display(self, prefix="", ostream=None):
        if ostream is None:
            ostream = sys.stdout
        print >>ostream, prefix+"Connector "+self.name,":",
        print >>ostream, "  Size="+str(len(self)),
        if None in self._conval:
            print >>ostream, prefix+"  : {"+\
                ', '.join(sorted(self._conval[key].keys()))+"}"
        else:
            for key in sorted(self._conval.keys()):
                print >>ostream, prefix+"  "+str(key)+" : {"+\
                  ', '.join(sorted(self._conval[key].keys()))+"}"


class _ConnectorElement(_ConnectorBase, _ConnectorValue):

    def __init__(self, *args, **kwd):

        _ConnectorValue.__init__(self, kwd.get('name', None) )
        _ConnectorBase.__init__(self, *args, **kwd)
        self._conval[None] = self
        self._conval[None].component = weakref.ref(self)
        self._conval[None].index = None

    def __getstate__(self):
        result = _VarData.__getstate__(self)
        for key,value in self.__dict__.iteritems():
            result[key]=value
        if type(result['_conval'][None].component) is weakref.ref:
            result['_conval'][None].component = None
        return result

    def __setstate__(self, dict):
        for key in dict:
            setattr(self, key, dict[key])
        self._conval[None].component = weakref.ref(self)

    def is_constant(self):
        return _ConnectorValue.is_constant(self)


# a _ConnectorArray is the implementation representing an indexed connector.

class _ConnectorArray(_ConnectorBase):
    
    def __init__(self, *args, **kwds):

        _ConnectorBase.__init__(self, *args, **kwds)
        self._dummy_val = _ConnectorValue(kwds.get('name', None))

    def __float__(self):
        raise TypeError, "Cannot access the value of array connector "+self.name

    def __int__(self):
        raise TypeError, "Cannot access the value of array connector "+self.name

    def set_value(self, value):
        msg = "Cannot specify the value of a connector '%s'"
        raise ValueError, msg % self.name

    def __str__(self):
        return self.name

    def construct(self, data=None):
        _ConnectorBase.construct(self, data)


class Connector(Component):
    """A 'bundle' of variables that can be manipulated together"""

    alias( "Connector", 
           "A bundle of variables that can be manipilated together." )

    @classmethod
    def conserved_quantity():
        pass

    # The idea behind a Connector is to create a bundle of variables
    # that can be manipulated as a single variable within constraints.
    # While Connectors inherit from variable (mostly so that the
    # expression infrastucture can manipulate them), they are not actual
    # variables that are exposed to the solver.  Instead, a preprocessor
    # (ConnectorExpander) will look for expressions that involve
    # connectors and replace the single constraint with a list of
    # constraints that involve the original variables contained within
    # the Connector.

    def __new__(cls, *args, **kwds):
        if args == ():
            self = _ConnectorElement(*args, **kwds)
        else:
            self = _ConnectorArray(*args, **kwds)
        return self




class ConnectorExpander(Plugin):
    implements(IPyomoScriptModifyInstance)

    def apply(self, **kwds):
        logger.debug("Calling ConnectorExpander")
                
        instance = kwds['instance']
        blockList = instance.all_blocks()
        noConnectors = True
        for b in blockList:
            if b.components.components(Connector):
                noConnectors = False
                break
        if noConnectors:
            return

        logger.debug("   Connectors found!")

        #
        # At this point, there are connectors in the model, so we must
        # look for constraints that involve connectors and expand them.
        #
        #options = kwds['options']
        #model = kwds['model']


        # Expand each constraint involving a connector
        for block in blockList:
            logger.debug("   block: " + block.name)
            for name, constraint in \
                    block.components.components(Constraint).iteritems():
                for idx, c in constraint._data.iteritems():
                    logger.debug("   (looking at constraint %s[%s])", name, idx)
                    connectors = []
                    self._gather_connectors(c.body, connectors)
                    if len(connectors) == 0:
                        continue
                    logger.debug("   (found connectors in constraint)")
                    
                    # Validate that all connectors match
                    errors = self._validate_connectors(connectors)
                    if errors:
                        logger.error(
                            ( "Connector mismatch: errors detected when "
                              "constructing constraint %s\n    " %
                              (name + (idx and '[%s]' % idx or '')) ) +
                            '\n    '.join(reversed(errors)) )
                        raise ValueError(
                            "Connector mismatch in constraint %s" % \
                            name + (idx and '[%s]' % idx or ''))
                    
                    logger.debug("   (connectors valid)")
                    
                    # OK - expand this constraint
                    self._expand_constraint(block, name, idx, c, connectors[0])
                    # Now deactivate the original constraint
                    c.deactivate()

        # Now, go back and implement VarList aggregators
        for block in blockList:
            for conn in block.components.components(Connector).itervalues():
                for var, aggregator in conn.aggregators.iteritems():
                    c = Constraint(expr=aggregator(block._model(), block, var))
                    block._add_component(
                        conn.name + '.' + var.name + '.aggregate', c)
                    c.construct()
        

        # REQUIRED: re-call preprocess()
        instance.preprocess()

    def _gather_connectors(self, expr, connectors):
        if expr.is_expression():
            if expr.__class__ is _ProductExpression:
                for e in expr._numerator:
                    self._gather_connectors(e, connectors)
                for e in expr._denominator:
                    self._gather_connectors(e, connectors)
            else:
                for e in expr._args:
                    self._gather_connectors(e, connectors)
        elif isinstance(expr, _ConnectorValue):
            connectors.append(expr)

    def _validate_connectors(self, connectors):
        ref = connectors.pop()
        errors = []
        for tmp in connectors:
            a = sorted(ref.vars.keys())
            b = sorted(tmp.vars.keys())
            while a:
                if not b:
                    break
                if a[-1] == b[-1]:
                    #if len(ref.vars[a[-1]]) != len(tmp.vars[a[-1]]):
                    #    errors.append(
                    #        "Variable dimension mismatch for variable "
                    #        "'%s' in connectors '%s' and '%s'" %
                    #        ( a[-1], ref.name, tmp.name ) )
                    a.pop()
                    b.pop()
                elif a[-1] > b[-1]:
                    # TODO: add a fq_name so we can easily get
                    # the full model.block.connector name
                    errors.append(
                        "Connector '%s' missing variable '%s' "
                        "(appearing in reference connector '%s')" %
                        ( tmp.name, a[-1], ref.name ) )
                    a.pop()
                else:
                    errors.append(
                        "Reference connector '%s' missing variable '%s' "
                            "(appearing in connector '%s')" %
                        ( ref.name, b[-1], tmp.name ) )
                    b.pop()
            for x in reversed(a):
                errors.append(
                    "Reference connector '%s' missing variable '%s' "
                    "(appearing in connector '%s')" %
                    ( tmp.name, x, ref.name ) )
            for x in reversed(b):
                errors.append(
                    "Connector '%s' missing variable '%s' "
                    "(appearing in reference connector '%s')" %
                    ( ref.name, x, tmp.name ) )
        return errors

    def _expand_constraint(self, block, name, idx, constraint, ref):
        cList = ConstraintList()
        block._add_component( name+( idx and '.'+str(idx) or '' )+'.expanded',
                              cList )

        def _substitute_vars(args, var):
            for idx, arg in enumerate(args):
                if arg.is_expression():
                    if arg.__class__ is _ProductExpression:
                        _substitute_vars(arg._numerator, var)
                        _substitute_vars(arg._denominator, var)
                    else:
                        _substitute_vars(arg._args, var)
                elif isinstance(arg, _ConnectorValue):
                    tmp = [ arg.vars[var] ]
                    _substitute_vars(tmp, var)
                    args[idx] = tmp[0]
                elif arg.__class__ is VarList:
                    args[idx] = arg.add()

        for var in ref.vars.iterkeys():
            c = [ constraint.body.clone() ]
            _substitute_vars(c, var)
            if constraint._equality:
                cList.add( ( c[0], constraint.upper ) )
            else:
                cList.add( ( constraint.lower, c[0], constraint.upper ) )

        cList.construct()

transform = ConnectorExpander()
