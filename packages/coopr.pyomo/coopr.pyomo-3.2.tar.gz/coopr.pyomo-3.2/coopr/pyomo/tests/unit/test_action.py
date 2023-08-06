#
# Unit Tests for BuildAction() Objects
#
# PyomoModel                Base test class
# Simple                    Test singleton parameter
# Array1                    Test arrays of parameters
#

import unittest
import os
import sys
from os.path import abspath, dirname
sys.path.insert(0, dirname(dirname(abspath(__file__)))+"/../..")
from coopr.pyomo import *

class PyomoModel(unittest.TestCase):

    def setUp(self):
        self.model = AbstractModel()

    def construct(self,filename):
        self.instance = self.model.create(filename)


def action1_fn(model):
    model.A = 4.3

def action2_fn(model, i):
    if i in model.A:
        model.A[i] = value(model.A[i])+i


class Simple(PyomoModel):

    def setUp(self):
        #
        # Create Model
        #
        PyomoModel.setUp(self)
        #
        # Create model instance
        #
        self.model.A = Param(initialize=3.3)
        self.model.action1 = BuildAction(rule=action1_fn)
        self.instance = self.model.create()

    def tearDown(self):
        if os.path.exists("param.dat"):
            os.remove("param.dat")

    def test_value(self):
        """Check the value of the parameter"""
        tmp = value(self.instance.A.value)
        self.assertEqual( type(tmp), float)
        self.assertEqual( tmp, 4.3 )
        # BUG  TODO: this is a bug ... but we're going to ignore it for now
        #self.assertEqual( value(self.instance.A.value), value(self.instance.A) )

    def test_getattr(self):
        """Check the use of the __getattr__ method"""
        self.assertEqual( self.instance.A.value, 4.3)



class Array1(PyomoModel):

    def setUp(self):
        #
        # Create Model
        #
        PyomoModel.setUp(self)
        #
        # Create model instance
        #
        self.model.Z = Set(initialize=[1,3])
        self.model.A = Param(self.model.Z, initialize={1:1.3})
        self.model.action2 = BuildAction(self.model.Z, rule=action2_fn)
        self.instance = self.model.create()

    def test_value(self):
        """Check the value of the parameter"""
        tmp = value(self.instance.A[1])
        self.assertEqual( type(tmp), float)
        self.assertEqual( tmp, 2.3 )


class Array2(PyomoModel):

    def setUp(self):
        #
        # Create Model
        #
        PyomoModel.setUp(self)
        #
        # Create model instance
        #
        self.model.Z = Set(initialize=[1,3])
        self.model.A = Param(self.model.Z, initialize=1.3)
        self.model.action2 = BuildAction(self.model.Z, rule=action2_fn)
        self.instance = self.model.create()

    def test_getitem(self):
        """Check the use of getitem"""
        self.assertEqual( self.instance.A[1], 2.3)
        self.assertEqual( value(self.instance.A[3]), 4.3)


if __name__ == "__main__":
    unittest.main()
