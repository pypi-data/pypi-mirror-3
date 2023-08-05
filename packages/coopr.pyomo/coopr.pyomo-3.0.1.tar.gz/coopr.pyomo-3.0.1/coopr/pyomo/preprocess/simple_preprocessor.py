#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the FAST README.txt file.
#  _________________________________________________________________________

import pyutilib.misc
import pyutilib.component.core
from coopr.pyomo.base import IPyomoPresolver, IPyomoPresolveAction


class SimplePreprocessor(pyutilib.component.core.SingletonPlugin):
    """
    This plugin simply applies preprocess actions in a fixed order
    and then returns the modified model instance.
    """

    pyutilib.component.core.implements(IPyomoPresolver)

    def __init__(self, **kwds):
        kwds['name'] = "simple_preprocessor"
        pyutilib.component.core.Plugin.__init__(self, **kwds)
        self.actions = pyutilib.component.core.ExtensionPoint(IPyomoPresolveAction)
        self.active_actions = set()
        self.action_rank = {}
        self.initialized = False

    def _initialize(self):
        if self.initialized:
            return
        self.initialized = True
        for action in self.actions():
            self.activate_action(action.name)

    def get_actions(self):
        """Return a list of preprocess actions, with their ranks"""
        self._initialize()
        ans = []
        for action in self._order_actions():
            ans.append( (action, self.action_rank[action]) )
        return ans

    def activate_action(self, action, rank=None):
        """Activate an action"""
        self._initialize()
        tmp = self.actions.service(action)
        if tmp is None:
            raise ValueError, "Cannot activate unknown action %s" % action
        self.active_actions.add(action)
        if rank is None:
            rank = tmp.rank()
        self.action_rank[action] = rank

    def deactivate_action(self, action):
        """Deactivate an action"""
        self._initialize()
        if action in self.active_actions:
            self.active_actions.remove(action)
            del self.action_rank[action]

    def preprocess(self,model):
        """
        Apply the preprocess actions to this instance, and return the revised instance.
        """
        self._initialize()
        for action in self._order_actions():
            model = self.actions.service(action).preprocess(model)
        return model

    def _order_actions(self):
        actions = list(self.active_actions)
        ranks = []
        for item in actions:
            ranks.append(self.action_rank[item])
        index = pyutilib.misc.sort_index(ranks)
        sorted=[]
        for i in index:
            sorted.append( actions[i] )
        return sorted
