#
# Test the canonical expressions
#

import os
import sys
from os.path import abspath, dirname
sys.path.insert(0, dirname(dirname(abspath(__file__)))+os.sep+".."+os.sep+"..")
currdir = dirname(abspath(__file__))+os.sep

from coopr.pyomo import *
from coopr.opt import *
#from coopr.pyomo.base.var import _VarElement
import pyutilib.th as unittest
import pyutilib.services
from coopr.pyomo.preprocess.simple_preprocessor import SimplePreprocessor
from pyutilib.component.core import PluginGlobals

class frozendict(dict):
    __slots__ = ('_hash',)
    def __hash__(self):
        rval = getattr(self, '_hash', None)
        if rval is None:
            rval = self._hash = hash(frozenset(self.iteritems()))
        return rval


class Test(unittest.TestCase):

    def setUp(self):
        #
        # Create Model
        #
        #PluginGlobals.pprint()
        self.plugin = SimplePreprocessor()
        self.plugin.deactivate_action("compute_canonical_repn")

    def tearDown(self):
        if os.path.exists("unknown.lp"):
            os.unlink("unknown.lp")
        pyutilib.services.TempfileManager.clear_tempfiles()
        self.plugin.activate_action("compute_canonical_repn")

    def test_abstract_linear_expression(self):
        m = AbstractModel()
        m.A = RangeSet(1,3)
        def p_init(model, i):
            return 2*i
        m.p = Param(m.A, initialize=p_init)
        m.x = Var(m.A, bounds=(-1,1))
        def obj_rule(model):
            return summation(model.p, model.x)
        m.obj = Objective(rule=obj_rule)
        i = m.create()
        #self.instance.obj[None].expr.pprint()
        rep = generate_canonical_repn(i.obj[None].expr)
        # rep should only have [-1,1]
        self.assertEqual(len(rep), 2)
        self.assertTrue(1 in rep)
        self.assertTrue(-1 in rep)
        # rep[-1] should have the 3 variables...
        self.assertEqual(rep[-1], { id(i.x[1]): i.x[1],
                                    id(i.x[2]): i.x[2],
                                    id(i.x[3]): i.x[3]})
        # check the expression encoding
        self.assertEqual(rep[1], { id(i.x[1]): 2.0, 
                                   id(i.x[2]): 4.0, 
                                   id(i.x[3]): 6.0 })


    def test_concrete_linear_expression(self):
        m = ConcreteModel()
        m.A = RangeSet(1,3)
        def p_init(model, i):
            return 2*i
        m.p = Param(m.A, initialize=p_init)
        m.x = Var(m.A, bounds=(-1,1))
        m.obj = Objective(expr=summation(m.p, m.x))
        rep = generate_canonical_repn(m.obj[None].expr)
        # rep should only have [-1,1]
        self.assertEqual(len(rep), 2)
        self.assertTrue(1 in rep)
        self.assertTrue(-1 in rep)
        # rep[-1] should have the 3 variables...
        self.assertEqual(rep[-1], { id(m.x[1]): m.x[1],
                                    id(m.x[2]): m.x[2],
                                    id(m.x[3]): m.x[3]})
        # check the expression encoding
        self.assertEqual(rep[1], { id(m.x[1]): 2.0, 
                                   id(m.x[2]): 4.0, 
                                   id(m.x[3]): 6.0 })

    def test_linear_expression(self):
        I = range(3)
        x = [Var(bounds=(-1,1)) for i in I]
        expr = sum(2*(i+1)*x[i] for i in I)
        rep = generate_canonical_repn(expr)
        # rep should only have [-1,1]
        self.assertEqual(len(rep), 2)
        self.assertTrue(1 in rep)
        self.assertTrue(-1 in rep)
        # rep[-1] should have the 3 variables... 
        self.assertEqual(rep[-1], { id(x[0]): x[0],
                                    id(x[1]): x[1],
                                    id(x[2]): x[2] })
        # check the expression encoding
        self.assertEqual(rep[1], { id(x[0]): 2.0, 
                                   id(x[1]): 4.0, 
                                   id(x[2]): 6.0 } )

    def test_complex_linear_expression(self):
        I = range(3)
        x = [Var(bounds=(-1,1)) for i in I]
        expr = 2*x[1] + 3*x[1] + 4*(x[1]+x[2])
        rep = generate_canonical_repn(expr)
        # rep should only have [-1,1]
        self.assertEqual(len(rep), 2)
        self.assertTrue(1 in rep)
        self.assertTrue(-1 in rep)
        # rep[-1] should have the 2 of the 3 variables...
        self.assertEqual(rep[-1], { id(x[1]): x[1],
                                    id(x[2]): x[2] })
        # check the expression encoding
        self.assertEqual(rep[1], { id(x[1]): 9.0, 
                                   id(x[2]): 4.0 } )


    def test_linear_expression_with_constant(self):
        I = range(3)
        x = [Var(bounds=(-1,1)) for i in I]
        expr = 1.2 + 2*x[1] + 3*x[1]
        rep = generate_canonical_repn(expr)
        # rep should only have [-1,0,1]
        self.assertEqual(len(rep), 3)
        self.assertTrue(0 in rep)
        self.assertTrue(1 in rep)
        self.assertTrue(-1 in rep)
        # rep[-1] should have the 1 of the 3 variables...
        self.assertEqual(rep[-1], { id(x[1]): x[1] })
        # check the expression encoding
        self.assertEqual(rep[0], { None: 1.2 } )
        self.assertEqual(rep[1], { id(x[1]): 5.0 } )


    def test_complex_linear_expression_with_constant(self):
        I = range(3)
        x = [Var(bounds=(-1,1)) for i in I]
        expr =  2.0*(1.2 + 2*x[1] + 3*x[1]) + 3.0*(1.0+x[1])
        rep = generate_canonical_repn(expr)
        # rep should only have [-1,0,1]
        self.assertEqual(len(rep), 3)
        self.assertTrue(0 in rep)
        self.assertTrue(1 in rep)
        self.assertTrue(-1 in rep)
        # rep[-1] should have the 1 of the 3 variables...
        self.assertEqual(rep[-1], { id(x[1]): x[1] })
        # check the expression encoding
        self.assertEqual(rep[0], { None: 5.4 } )
        self.assertEqual(rep[1], { id(x[1]): 13.0 } )


    def test_polynomial_expression(self):
        I = range(4)
        x = [Var(bounds=(-1,1)) for i in I]
        expr = x[1]*(x[1]+x[2]) + x[2]*(x[1]+3.0*x[3]*x[3])
        rep = generate_canonical_repn(expr)
        # rep should only have [-1,2,3]
        self.assertEqual(len(rep), 3)
        self.assertTrue(2 in rep)
        self.assertTrue(3 in rep)
        self.assertTrue(-1 in rep)
        # rep[-1] should have the 3 of the 4 variables...
        self.assertEqual(rep[-1], { id(x[1]): x[1],
                                    id(x[2]): x[2],
                                    id(x[3]): x[3] })
        # check the expression encoding
        self.assertEqual(rep[2], {frozendict({id(x[1]):2}):1.0, 
                                  frozendict({id(x[1]):1, id(x[2]):1}):2.0})
        self.assertEqual(rep[3], {frozendict({id(x[2]):1, id(x[3]):2}):3.0})


    def test_polynomial_expression_with_fixed(self):
        I = range(4)
        x = [Var() for i in I]
        expr = x[1]*(x[1]+x[2]) + x[2]*(x[1]+3.0*x[3]*x[3])
        x[1].value = 5
        x[1].fixed = True
        rep = generate_canonical_repn(expr)
        # rep should only have [-1,0,1,3]
        self.assertEqual(len(rep), 4)
        self.assertTrue(0 in rep)
        self.assertTrue(1 in rep)
        self.assertTrue(3 in rep)
        self.assertTrue(-1 in rep)
        # rep[-1] should have the 2 of the 4 variables...
        self.assertEqual(rep[-1], { id(x[2]): x[2],
                                    id(x[3]): x[3] })
        # check the expression encoding
        self.assertEqual(rep[0], {None: 25.0})
        self.assertEqual(rep[1], {id(x[2]): 10.0})
        self.assertEqual(rep[3], {frozendict({id(x[2]):1, id(x[3]):2}):3.0})


    def test_linear_expression_with_constant_division(self):
        m = ConcreteModel()
        m.A = RangeSet(1,3)
        def p_init(model, i):
            return 2*i
        m.p = Param(m.A, initialize=p_init)
        m.x = Var(m.A, bounds=(-1,1))
        expr = summation(m.p, m.x)/2.0
        rep = generate_canonical_repn(expr)
        # rep should only have [-1,1]
        self.assertEqual(len(rep), 2)
        self.assertTrue(1 in rep)
        self.assertTrue(-1 in rep)
        # rep[-1] should have the 3 variables... 
        self.assertEqual(rep[-1], { id(m.x[1]): m.x[1],
                                    id(m.x[2]): m.x[2],
                                    id(m.x[3]): m.x[3] })
        # check the expression encoding
        self.assertEqual(rep[1], { id(m.x[1]): 1.0, 
                                   id(m.x[2]): 2.0, 
                                   id(m.x[3]): 3.0 } )

    def test_linear_expression_with_fixed_division(self):
        m = ConcreteModel()
        m.A = RangeSet(1,3)
        def p_init(model, i):
            return 2*i
        m.p = Param(m.A, initialize=p_init)
        m.x = Var(m.A, bounds=(-1,1))
        m.y = Var(initialize=2.0)
        m.y.fixed = True
        expr = summation(m.p, m.x)/m.y
        rep = generate_canonical_repn(expr)
        # rep should only have [-1,1]
        self.assertEqual(len(rep), 2)
        self.assertTrue(1 in rep)
        self.assertTrue(-1 in rep)
        # rep[-1] should have the 3 variables... 
        self.assertEqual(rep[-1], { id(m.x[1]): m.x[1],
                                    id(m.x[2]): m.x[2],
                                    id(m.x[3]): m.x[3] })
        # check the expression encoding
        self.assertEqual(rep[1], { id(m.x[1]): 1.0, 
                                   id(m.x[2]): 2.0, 
                                   id(m.x[3]): 3.0 } )

    def test_linear_expression_with_complex_fixed_division(self):
        m = ConcreteModel()
        m.A = RangeSet(1,3)
        def p_init(model, i):
            return 2*i
        m.p = Param(m.A, initialize=p_init)
        m.x = Var(m.A, bounds=(-1,1))
        m.y = Var(initialize=1.0)
        m.y.fixed = True
        expr = summation(m.p, m.x)/(m.y+1)
        rep = generate_canonical_repn(expr)
        # rep should only have [-1,1]
        self.assertEqual(len(rep), 2)
        self.assertTrue(1 in rep)
        self.assertTrue(-1 in rep)
        # rep[-1] should have the 3 variables... 
        self.assertEqual(rep[-1], { id(m.x[1]): m.x[1],
                                    id(m.x[2]): m.x[2],
                                    id(m.x[3]): m.x[3] })
        # check the expression encoding
        self.assertEqual(rep[1], { id(m.x[1]): 1.0, 
                                   id(m.x[2]): 2.0, 
                                   id(m.x[3]): 3.0 } )


    def test_expr_rational_summation(self):
        m = ConcreteModel()
        m.A = RangeSet(1,3)
        def p_init(model, i):
            return 2*i
        m.p = Param(m.A, initialize=p_init)
        m.x = Var(m.A, bounds=(-1,1))
        m.y = Var(initialize=1.0)
        expr = summation(m.p, m.x)/(1+m.y)
        #expr.pprint()
        rep = generate_canonical_repn(expr)
        # rep should only have [-1,None]
        self.assertEqual(len(rep), 2)
        self.assertTrue(None in rep)
        self.assertTrue(-1 in rep)
        # rep[-1] should have the 4 variables... 
        self.assertEqual(rep[-1], { id(m.y): m.y,
                                    id(m.x[1]): m.x[1],
                                    id(m.x[2]): m.x[2],
                                    id(m.x[3]): m.x[3] })
        # check the expression encoding
        self.assertIs(rep[None], expr)

    def test_expr_rational(self):
        m = ConcreteModel()
        m.A = RangeSet(1,4)
        m.x = Var(m.A, bounds=(-1,1))
        m.y = Var(initialize=1.0)
        expr = (1.25+m.x[1]+1/m.y) + (2.0+m.x[2])/m.y
        #expr.pprint()
        rep = generate_canonical_repn(expr)
        # rep should only have [-1,None]
        self.assertEqual(len(rep), 2)
        self.assertTrue(None in rep)
        self.assertTrue(-1 in rep)
        # rep[-1] should have the 3 variables... 
        self.assertEqual(rep[-1], { id(m.y): m.y,
                                    id(m.x[1]): m.x[1],
                                    id(m.x[2]): m.x[2] })
        # check the expression encoding
        self.assertIs(rep[None], expr)

    def test_expr_rational_fixed(self):
        m = ConcreteModel()
        m.A = RangeSet(1,4)
        m.x = Var(m.A, bounds=(-1,1))
        m.y = Var(initialize=2.0)
        m.y.fixed = True
        expr = (1.25+m.x[1]+1/m.y) + (2.0+m.x[2])/m.y
        #expr.pprint()
        rep = generate_canonical_repn(expr)
        # rep should only have [-1,0,1]
        self.assertEqual(len(rep), 3)
        self.assertTrue(0 in rep)
        self.assertTrue(1 in rep)
        self.assertTrue(-1 in rep)
        # rep[-1] should have the 2 of 3 variables... 
        self.assertEqual(rep[-1], { id(m.x[1]): m.x[1],
                                    id(m.x[2]): m.x[2] })
        # check the expression encoding 
        self.assertEqual(rep[0], {None: 2.75})
        self.assertEqual(rep[1], {id(m.x[1]): 1,
                                  id(m.x[2]): 0.5 })

    def test_general_nonlinear(self):
        I = range(3)
        x = [Var() for i in I]
        expr = x[1] + 5*cos(x[2])
        #expr.pprint()
        rep = generate_canonical_repn(expr)
        # rep should only have [-1,None]
        self.assertEqual(len(rep), 2)
        self.assertTrue(None in rep)
        self.assertTrue(-1 in rep)
        # rep[-1] should have 2 variables... 
        self.assertEqual(rep[-1], { id(x[1]): x[1],
                                    id(x[2]): x[2] })
        # check the expression encoding
        self.assertIs(rep[None], expr)
        
    def test_general_nonlinear_fixed(self):
        I = range(3)
        x = [Var() for i in I]
        expr = x[1] + 5*cos(x[2])
        x[2].value = 0
        x[2].fixed = True
        #expr.pprint()
        rep = generate_canonical_repn(expr)
        # rep should only have [-1,0,1]
        self.assertEqual(len(rep), 3)
        self.assertTrue(0 in rep)
        self.assertTrue(1 in rep)
        self.assertTrue(-1 in rep)
        # rep[-1] should have 1 variable... 
        self.assertEqual(rep[-1], { id(x[1]): x[1] })
        # check the expression encoding
        self.assertEqual(rep[0], {None: 5.0})
        self.assertEqual(rep[1], {id(x[1]): 1})

    def test_deterministic_var_labeling(self):
        m = ConcreteModel()
        m.x = Var(initialize=3.0)
        m.y = Var(initialize=2.0)
        exprA = m.x - m.y
        exprB = m.y - m.x

        # Nondeterministic form should not care which expression comes first
        rep_A = generate_canonical_repn(exprA)
        rep_B = generate_canonical_repn(exprB)
        self.assertEqual( rep_A[-1], rep_B[-1] )
        
        # Deterministic form should care which expression comes first
        idMap_1 = {}
        rep_A = generate_canonical_repn(exprA, idMap_1)
        rep_B = generate_canonical_repn(exprB, idMap_1)
        self.assertEqual( rep_A[-1], rep_B[-1] )
        
        idMap_2 = {}
        rep_B = generate_canonical_repn(exprB, idMap_2)
        rep_A = generate_canonical_repn(exprA, idMap_2)
        self.assertEqual( rep_A[-1], rep_B[-1] )

        self.assertNotEqual( idMap_1, idMap_2 )
        

if __name__ == "__main__":
    unittest.main()
