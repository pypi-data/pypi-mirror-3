#
# Unit Tests for Python numeric values
#

import os
import sys
from os.path import abspath, dirname
sys.path.insert(0, dirname(dirname(abspath(__file__)))+"/../..")
currdir = dirname(abspath(__file__))+os.sep

import pyutilib.th as unittest
from coopr.pyomo import *
from nose.tools import nottest

class Test_value(unittest.TestCase):

    def test_none(self):
        val = None
        self.assertEquals(val, value(val))

    def test_bool(self):
        val = False
        self.assertEquals(val, value(val))

    def test_float(self):
        val = 1.1
        self.assertEquals(val, value(val))

    def test_int(self):
        val = 1
        self.assertEquals(val, value(val))

    def test_long(self):
        val = long(1e10)
        self.assertEquals(val, value(val))

    def test_nan(self):
        val = pyutilib.math.nan
        self.assertEquals(id(val), id(value(val)))

    def test_inf(self):
        val = pyutilib.math.infinity
        self.assertEquals(id(val), id(value(val)))

    def test_string(self):
        val = 'foo'
        self.assertEquals(val, value(val))

    def test_const1(self):
        val = NumericConstant(None, None, 1.0)
        self.assertEquals(1.0, value(val))

    def test_const2(self):
        val = NumericConstant(None, Any, 'foo')
        self.assertEquals('foo', value(val))

    def test_const3(self):
        val = NumericConstant(None, None, pyutilib.math.nan)
        self.assertEquals(id(pyutilib.math.nan), id(value(val)))

    def test_const4(self):
        val = NumericConstant(None, None, pyutilib.math.infinity)
        self.assertEquals(id(pyutilib.math.infinity), id(value(val)))

    def test_val1(self):
        val = NumericValue(None, None, 1.0)
        self.assertEquals(1.0, value(val))

    def test_val2(self):
        val = NumericValue(None, Any, 'foo')
        self.assertEquals('foo', value(val))

    def test_val3(self):
        val = NumericValue(None, None, pyutilib.math.nan)
        self.assertEquals(id(pyutilib.math.nan), id(value(val)))

    def test_val4(self):
        val = NumericValue(None, None, pyutilib.math.infinity)
        self.assertEquals(id(pyutilib.math.infinity), id(value(val)))

    def test_error1(self):
        class A(object): pass
        val = A()
        try:
            value(val)
            self.fail("Expected ValueError")
        except ValueError:
            pass

    def test_error2(self):
        val = NumericConstant(None, Any, None)
        try:
            value(val)
            self.fail("Expected ValueError")
        except ValueError:
            pass


class Test_is_constant(unittest.TestCase):

    def test_none(self):
        val = None
        try:
            is_constant(val)
            self.fail("Expected ValueError")
        except ValueError:
            pass

    def test_bool(self):
        self.assertTrue(is_constant(True))

    def test_float(self):
        self.assertTrue(is_constant(1.1))

    def test_int(self):
        self.assertTrue(is_constant(1))

    def test_long(self):
        val = long(1e10)
        self.assertTrue(is_constant(val))

    def test_string(self):
        self.assertTrue(is_constant('foo'))

    def test_const1(self):
        val = NumericConstant(None, None, 1.0)
        self.assertTrue(is_constant(val))

    def test_const2(self):
        val = NumericConstant(None, Any, 'foo')
        self.assertTrue(is_constant(val))

    def test_error(self):
        class A(object): pass
        val = A()
        try:
            is_constant(val)
            self.fail("Expected ValueError")
        except ValueError:
            pass


class Test_as_numeric(unittest.TestCase):

    def test_none(self):
        val = None
        try:
            as_numeric(val)
            self.fail("Expected ValueError")
        except:
            pass

    def test_bool(self):
        val = False
        self.assertEquals(val, as_numeric(val))

    def test_float(self):
        val = 1.1
        self.assertEquals(val, as_numeric(val))

    def test_int(self):
        val = 1
        self.assertEquals(val, as_numeric(val))

    def test_long(self):
        val = long(1e10)
        self.assertEquals(val, as_numeric(val))

    def test_string(self):
        val = 'foo'
        try:
            as_numeric(val)
            self.fail("Expected ValueError")
        except:
            pass

    def test_const1(self):
        val = NumericConstant(None, None, 1.0)
        self.assertEquals(1.0, as_numeric(val))

    def test_const2(self):
        val = NumericConstant(None, Any, 'foo')
        try:
            as_numeric(val)
            self.fail("Expected ValueError")
        except:
            pass

    def test_error1(self):
        class A(object): pass
        val = A()
        try:
            as_numeric(val)
            self.fail("Expected ValueError")
        except ValueError:
            pass

    def test_error2(self):
        val = NumericConstant(None, Any, None)
        num = as_numeric(val)
        try:
            value(num)
            self.fail("Expected ValueError")
        except ValueError:
            pass


if __name__ == "__main__":
    unittest.main()

