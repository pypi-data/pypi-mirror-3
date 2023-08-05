import types

import pyutilib.th as unittest
from coopr.pyomo import *

from coopr.opt.base import SymbolMap
from coopr.pyomo.io.ampl import _trivial_labeler

from helper import MockFixedValue

_campl_available = False
try:
    import coopr.pyomo.io.ampl.cAmpl as cAmpl
    _campl_available = True
    cgar = coopr.pyomo.io.ampl.cAmpl.generate_ampl_repn
    gar = coopr.pyomo.io.ampl.ampl.py_generate_ampl_repn
except ImportError:
    gar = coopr.pyomo.io.ampl.ampl.generate_ampl_repn

class _GenericAmplRepnEqualityTests(unittest.TestCase):
    def setUp(self):
        # Helper function for param init
        def q_initialize(model, i):
            return [2,3,5,7,11,13,17,19,23,29][i-1]
        # Need a model so that variables can be distinguishable
        self.model = ConcreteModel()
        self.model.s = RangeSet(10)
        self.model.p = Param(default=42)
        self.model.q = Param(self.model.s, initialize=q_initialize)
        self.model.w = Var(self.model.s)
        self.model.x = Var()
        self.model.y = Var()
        self.model.z = Var(self.model.s)
        self.symbol_map = SymbolMap(self.model)
        self.labeler = _trivial_labeler()

    def tearDown(self):
        self.model = None

    def assertAmplRepnMatch(self, rep1, rep2):
        self.assertEqual(rep1, rep2)
        self.assertEqual(rep1.is_constant(), rep2.is_constant())
        self.assertEqual(rep1.is_linear(), rep2.is_linear())
        self.assertEqual(rep1.is_nonlinear(), rep2.is_nonlinear())
        self.assertEqual(rep1.needs_sum(), rep2.needs_sum())

class AmplRepnEqualityTests(_GenericAmplRepnEqualityTests):
    """Serves as a test class for the ampl_representation.__eq__ method."""

    def testBasicEquality(self):
        self.assertEqual(io.ampl.ampl_representation(), io.ampl.ampl_representation())

    def testBasicInequality(self):
        self.assertNotEqual(io.ampl.ampl_representation(), None)

    def testVarEquality(self):
        self.assertEqual(gar(self.model.x, self.symbol_map, self.labeler), gar(self.model.x, self.symbol_map, self.labeler))

    def testVarInequality(self):
        self.assertNotEqual(gar(self.model.x, self.symbol_map, self.labeler), gar(self.model.y, self.symbol_map, self.labeler))

    def testVarCoefInequality(self):
        self.assertNotEqual(gar(self.model.x, self.symbol_map, self.labeler), gar(2.0 * self.model.x, self.symbol_map, self.labeler))

    def testFixedValueEquality(self):
        self.assertEqual(gar(MockFixedValue(), self.symbol_map, self.labeler), gar(MockFixedValue(), self.symbol_map, self.labeler))

    def testFixedValueInequality(self):
        self.assertNotEqual(gar(MockFixedValue(1), self.symbol_map, self.labeler), gar(MockFixedValue(2), self.symbol_map, self.labeler))

    def testProductEquality(self):
        expr = self.model.x * self.model.y
        self.assertEqual(gar(expr, self.symbol_map, self.labeler), gar(expr, self.symbol_map, self.labeler))

    def testProductInequality(self):
        e1 = self.model.x * self.model.x
        e2 = self.model.y * self.model.y
        self.assertNotEqual(gar(e1,self.symbol_map, self.labeler), gar(e2, self.symbol_map, self.labeler))

    def testSumEquality(self):
        expr = self.model.x + self.model.y
        self.assertEqual(gar(expr, self.symbol_map, self.labeler), gar(expr, self.symbol_map, self.labeler))

    def testSumInequality(self):
        e1 = self.model.x + self.model.y
        e2 = self.model.x + self.model.x
        self.assertNotEqual(gar(e1, self.symbol_map, self.labeler), gar(e2, self.symbol_map, self.labeler))

    def testSumCommutativeEquality(self):
        e1 = self.model.x + self.model.y
        e2 = self.model.y + self.model.x
        self.assertEqual(gar(e1, self.symbol_map, self.labeler), gar(e2, self.symbol_map, self.labeler))

    def testPowEquality(self):
        expr = self.model.x ** 2
        self.assertEqual(gar(expr, self.symbol_map, self.labeler), gar(expr, self.symbol_map, self.labeler))

    def testPowInequality(self):
        e1 = self.model.x ** 2
        e2 = self.model.x ** 3
        self.assertNotEqual(gar(e1, self.symbol_map, self.labeler), gar(e2, self.symbol_map, self.labeler))

    def testIntrinsicEquality(self):
        fns = [sin, cos, tan, sinh, cosh, tanh, asin, acos, atan, asinh, acosh, atanh, log, exp]
        for fn in fns:
            expr = fn(self.model.x)
            self.assertEqual(gar(expr, self.symbol_map, self.labeler), gar(expr, self.symbol_map, self.labeler))

    def testIntrinsicInequality(self):
        e1 = sin(self.model.x)
        e2 = cos(self.model.x)
        self.assertNotEqual(gar(e1, self.symbol_map, self.labeler), gar(e2, self.symbol_map, self.labeler))

    def testCompoundEquality(self):
        expr = self.model.x + self.model.y + self.model.x * self.model.y
        self.assertEqual(gar(expr, self.symbol_map, self.labeler), gar(expr, self.symbol_map, self.labeler))

    def testMoreCompoundEquality(self):
        expr = ((self.model.x + self.model.y) * self.model.x) ** 2
        self.assertEqual(gar(expr, self.symbol_map, self.labeler), gar(expr, self.symbol_map, self.labeler))

    def testCompoundCoefficientInequality(self):
        e1 = self.model.x * self.model.y
        e2 = 2.0 * self.model.x * self.model.y
        self.assertNotEqual(gar(e1, self.symbol_map, self.labeler), gar(e2, self.symbol_map, self.labeler))
    
    def testQuotientEquality(self):
        expr = self.model.x / self.model.y
        self.assertEqual(gar(expr, self.symbol_map, self.labeler), gar(expr, self.symbol_map, self.labeler))

    def testCompoundQuotientEquality(self):
        expr = self.model.y + self.model.x / self.model.y + self.model.y ** 2
        self.assertEqual(gar(expr, self.symbol_map, self.labeler), gar(expr, self.symbol_map, self.labeler))

    def testQuotientInequality(self):
        e1 = self.model.x / self.model.y
        e2 = self.model.y / self.model.x
        self.assertNotEqual(gar(e1, self.symbol_map, self.labeler), gar(e2, self.symbol_map, self.labeler))

    def testSumEquality(self):
        expr = sum(self.model.z[i] for i in self.model.s)
        self.assertEqual(gar(expr, self.symbol_map, self.labeler), gar(expr, self.symbol_map, self.labeler))

    def testCompoundSumEquality(self):
        expr = sum(self.model.z[i] for i in self.model.s) + self.model.x / self.model.y
        self.assertEqual(gar(expr, self.symbol_map, self.labeler), gar(expr, self.symbol_map, self.labeler))

@unittest.skipUnless(_campl_available, "C AMPL module required")
class CAmplEqualityCompatTests(_GenericAmplRepnEqualityTests):
    """Tests whether the Python and cAmpl implementations produce identical repns."""

    def testEnvironment(self):
        # Simply ensure the import environment is working.
        with self.assertRaises(ValueError) as cm:
            cAmpl.generate_ampl_repn(None, None, None)

    def testEnvironmentTypes(self):
        self.assertEqual(type(gar), types.FunctionType)
        self.assertEqual(type(cgar), types.BuiltinFunctionType)

    def testFixedValue(self):
        expr = MockFixedValue()
        self.assertAmplRepnMatch(gar(expr, self.symbol_map, self.labeler), cgar(expr, self.symbol_map, self.labeler))

    def testVar(self):
        expr = self.model.x
        self.assertAmplRepnMatch(gar(expr, self.symbol_map, self.labeler), cgar(expr, self.symbol_map, self.labeler))

    def testProduct(self):
        expr = self.model.x * self.model.y
        self.assertAmplRepnMatch(gar(expr, self.symbol_map, self.labeler), cgar(expr, self.symbol_map, self.labeler))

    def testSum(self):
        expr = self.model.x + self.model.y
        self.assertAmplRepnMatch(gar(expr, self.symbol_map, self.labeler), cgar(expr, self.symbol_map, self.labeler))

    def testSumCommutative(self):
        e1 = self.model.x + self.model.y
        e2 = self.model.y + self.model.x
        self.assertAmplRepnMatch(gar(e1, self.symbol_map, self.labeler), cgar(e2, self.symbol_map, self.labeler))

    def testPow(self):
        expr = self.model.x ** 2
        self.assertAmplRepnMatch(gar(expr, self.symbol_map, self.labeler), cgar(expr, self.symbol_map, self.labeler))

    def testIntrinsic(self):
        fns = [sin, cos, tan, sinh, cosh, tanh, asin, acos, atan, asinh, acosh, atanh, log, exp]
        for fn in fns:
            expr = fn(self.model.x)
            self.assertAmplRepnMatch(gar(expr, self.symbol_map, self.labeler), cgar(expr, self.symbol_map, self.labeler))

    def testCompound(self):
        expr = self.model.x + self.model.y + self.model.x * self.model.y
        self.assertAmplRepnMatch(gar(expr, self.symbol_map, self.labeler), cgar(expr, self.symbol_map, self.labeler))

    def testMoreCompound(self):
        expr = ((self.model.x + self.model.y) * self.model.x) ** 2
        self.assertAmplRepnMatch(gar(expr, self.symbol_map, self.labeler), cgar(expr, self.symbol_map, self.labeler))

    def testQuotient(self):
        expr = self.model.x / self.model.y
        self.assertAmplRepnMatch(gar(expr, self.symbol_map, self.labeler), cgar(expr, self.symbol_map, self.labeler))

    def testCompoundQuotient(self):
        expr = self.model.y + self.model.x / self.model.y + self.model.y ** 2
        self.assertAmplRepnMatch(gar(expr, self.symbol_map, self.labeler), cgar(expr, self.symbol_map, self.labeler))

    def testSum(self):
        expr = sum(self.model.z[i] for i in self.model.s)
        self.assertAmplRepnMatch(gar(expr, self.symbol_map, self.labeler), cgar(expr, self.symbol_map, self.labeler))

    def testCompoundSum(self):
        expr = sum(self.model.z[i] for i in self.model.s) + self.model.x / self.model.y
        self.assertAmplRepnMatch(gar(expr, self.symbol_map, self.labeler), cgar(expr, self.symbol_map, self.labeler))

    def testSumExpression(self):
        expr = sum(self.model.w[i] / self.model.z[i] ** 3 for i in self.model.s)
        self.assertAmplRepnMatch(gar(expr, self.symbol_map, self.labeler), cgar(expr, self.symbol_map, self.labeler))

    def testSumExpressionParam(self):
        expr = sum(value(self.model.q[i]) / self.model.z[i] ** 3 for i in self.model.s)
        self.assertAmplRepnMatch(gar(expr, self.symbol_map, self.labeler), cgar(expr, self.symbol_map, self.labeler))

    def testCantilvrConstraintExpr(self):
        # originally from coopr.data.cute cantilvr model.
        expr = sum(value(self.model.q[i]) / self.model.z[i] ** 3 for i in self.model.s) - 1.0
        self.assertAmplRepnMatch(gar(expr, self.symbol_map, self.labeler), cgar(expr, self.symbol_map, self.labeler))

    def testCantilvrObjective(self):
        # originally from coopr.data.cute cantilvr model.
        # exposes problem in linear product handling, if present.
        expr = sum(self.model.z[i] for i in self.model.s) * 0.0624
        self.assertAmplRepnMatch(gar(expr, self.symbol_map, self.labeler), cgar(expr, self.symbol_map, self.labeler))

if __name__ == "__main__":
    unittest.main(verbosity=2)
