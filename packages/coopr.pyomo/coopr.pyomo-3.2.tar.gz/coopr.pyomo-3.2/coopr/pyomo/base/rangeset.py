#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

__all__ = ['RangeSet']

import math
import itertools
import sets
import expr
import set_types
from misc import apply_indexed_rule
from numvalue import value
from pyutilib.component.core import *

def count(start=0, step=1):
    n = start
    while True:
        yield n
        n += step

class RangeSetValidator(object):

    def __init__(self, start, end, step):
        self.start=start
        self.end=end
        self.step=step

    def __call__(self, model, val):
        if not type(val) in [int, float, long]:
            return False
        if val + 1e-7 < self.start:
            return False
        if val > self.end+1e-7:
            return False
        if type(self.start) is int and type(self.end) is int and type(self.step) is int and (val-self.start)%self.step != 0:
            return False
        return True


class RangeSet(sets._SetContainer):
    """A set that represents a list of numeric values"""

    alias("RangeSet", "A sequence of numeric values.  RangeSet(start,end,step) is a sequence starting a value 'start', and increasing in values by 'step' until a value greater than or equal to 'end' is reached.")

    def __init__(self,*args,**kwds):
        """Construct a list of integers"""
        tmp=()
        sets._SetContainer.__init__(self,*tmp,**kwds)
        if len(args) == 0:
            raise RuntimeError, "Attempting to construct a RangeSet object with no arguments!"

        self._type=RangeSet
        if len(args) == 1:
            self._start=1
            self._end=args[0]
            self._step=1
        elif len(args) == 2:
            self._start=args[0]
            self._end=args[1]
            self._step=1
        else:
            self._start=args[0]
            self._end=args[1]
            self._step=args[2]
        self.ordered=True
        self.value = None
        self.virtual = True
        self.concrete = True
        self._len = 0

    def construct(self, values=None):
        if self._constructed:
            return
        self._constructed=True
        if isinstance(self._start,expr.Expression):
            self._start_val = self._start()
        else:
            self._start_val = value(self._start)

        if isinstance(self._end,expr.Expression):
            self._end_val = self._end()
        else:
            self._end_val = value(self._end)

        if isinstance(self._step,expr.Expression):
            self._step_val = self._step()
        else:
            self._step_val = value(self._step)

        if type(self._start_val) is int and type(self._step) is int and type(self._end_val) is int:
            self.domain = set_types.Integers
        else:
            self.domain = set_types.Reals
        lb = self._start_val

        if self.filter is None and self.validate is None:
            self._len = int(math.floor((self._end_val-self._start_val+self._step_val+1e-7)//self._step_val))
            ub = self._start_val + (self._len-1)*self._step_val
        else:
            ub = self._start_val
            ctr=0
            for i in self:
                ub = i
                ctr += 1
            self._len = ctr
        self._bounds = (lb,ub)

    def __len__(self):
        return self._len

    def __iter__(self):
        if self.filter is None and self.validate is None:
            #for i in itertools.islice(count(), (self._end_val-self._start_val+self._step_val+1e-7)//self._step_val):
            for i in xrange(int((self._end_val-self._start_val+self._step_val+1e-7)//self._step_val)):
                yield self._start_val + i*self._step_val
        else:
            #for i in itertools.islice(count(), (self._end_val-self._start_val+self._step_val+1e-7)//self._step_val):
            for i in xrange(int((self._end_val-self._start_val+self._step_val+1e-7)//self._step_val)):
                val = self._start_val + i*self._step_val
                if not self.filter is None and not apply_indexed_rule(self, self.filter, self._model(), val):
                    continue
                if not self.validate is None and not apply_indexed_rule(self, self.validate, self._model(), val):
                    continue
                yield val

    def data(self):
        """The underlying set data."""
        return set(self)

    def first(self):
        return self._bounds[0]

    def last(self):
        return self._bounds[1]

    def member(self, key):
        if key >= 1:
            if key > self._len:
                raise IndexError, "Cannot index a RangeSet past the last element"
            return self._start_val + (key-1)*self._step_val
        elif key < 0:
            if self._len+key < 0:
                raise IndexError, "Cannot index a RangeSet past the first element"
            return self._start_val + (self._len+key)*self._step_val
        else:
            raise IndexError, "Valid index values for sets are 1 .. len(set) or -1 .. -len(set)"

    def __eq__(self, other):
        """ Equality comparison """
        if other is None:
            return False
        tmp = self._set_repn(other)
        if self.dimen != other.dimen:
            return False
        ctr = 0
        for i in self:
            if not i in other:
                return False
            ctr += 1
        return ctr == len(other)

    def _set_contains(self, element):
        # As the test for type -- or conversion to float -- is
        # expensive, we will work on the assumption that folks will "do
        # the right thing"... and let system exceptions handle the case
        # where they do not.
        
        #if not type(element) in [int,float]:
        #    return False
        try:
            x = element - self._start_val
            if x % self._step_val != 0:
                # If we are doing floating-point arithmetic, there is a
                # chance that we are seeing roundoff error...
                if math.fabs((x + 1e-7) % self._step_val) > 2e-7:
                    return False
            if element < self._bounds[0] or element > self._bounds[1]:
                return False
        except:
            return False
        if self.filter is not None and not self.filter(element):
            return False
        if self.validate is not None and not self.validate(self, element):
            return False
        return True

