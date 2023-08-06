#
# Test that the Pyomo NL writer does not modify the original model
#

import os
import sys
from os.path import abspath, dirname
currdir = dirname(abspath(__file__))+os.sep
import re
import glob

import pyutilib.th as unittest
import json
from coopr.pyomo import *
from coopr.pyomo.base.var import _VarData
from coopr.opt import ProblemFormat
import StringIO
from coopr.pyomo.base import expr as Expr
import itertools

# NOTE: The following line and the call to reload() in the function 'nlwriter_exprmod_test' are absolutely
#       critical so that the test suite that checks if expressions are modified by the
#       NL writer will not erroneously report as all passing. The test functions seems to 
#       pre-execute when run through 'test.coopr' and therefore if the model is modified it will 
#       actually start out that way in the true test, and therefore pass.
sys.path.append(currdir)

"""
This following function checks that expr1 is an
identical clone of expr2. By this I mean, all nested expressions
are the same, and all contained variables reference the same object
in memory ((Var1 is Var2) is True).
"""
@unittest.nottest
def expressions_equal(expr1,expr2):
    if not type(expr1) == type(expr2):
        print type(expr1), "!=", type(expr2)
        return False
    if isinstance(expr1,Var) or isinstance(expr1,_VarData):
        if not expr1 is expr2:
            print expr1, "is not", expr2
            return False
    elif isinstance(expr1,Expr.Expression):
        if not expr1.is_constant() is expr2.is_constant():
            print expr1.is_constant(), "is not", expr2.is_constant()
            return False
        if not expr1.polynomial_degree() == expr2.polynomial_degree():
            print expr1.polynomial_degree(), "!=", expr2.polynomial_degree()
            return False
        if isinstance(expr1,Expr._ProductExpression):
            if not expr1.coef == expr2.coef:
                print expr1.coef, "!=", expr2.coef
                return False
            if not len(expr1._denominator) == len(expr2._denominator):
                print len(expr1._denominator), "!=", len(expr2._denominator)
                return False
            if not all(expressions_equal(expr1._denominator[i],expr2._denominator[i]) for i in xrange(len(expr1._denominator))):
                return False
            if not len(expr1._numerator) == len(expr2._numerator):
                print len(expr1._numerator), "!=", len(expr2._numerator)
                return False
            if not all(expressions_equal(expr1._numerator[i],expr2._numerator[i]) for i in xrange(len(expr1._numerator))):
                return False
        if isinstance(expr1,Expr._SumExpression):
            if not expr1._const == expr2._const:
                print expr1._const, "!=", expr2._const
                return False
            if not len(expr1._coef) == len(expr2._coef):
                print len(expr1._coef), "!=", len(expr2._coef)
                return False
            if not all(expressions_equal(expr1._coef[i],expr2._coef[i]) for i in xrange(len(expr1._coef))):
                return False
            if not all(expressions_equal(expr1._args[i],expr2._args[i]) for i in xrange(len(expr1._args))):
                return False
        if isinstance(expr1,Expr._IdentityExpression) or \
           isinstance(expr1,Expr._EqualityExpression):
            if not len(expr1._args) == len(expr2._args):
                print len(expr1._args), "!=", len(expr2._args)
                return False
            if not all(expressions_equal(expr1._args[i],expr2._args[i]) for i in xrange(len(expr1._args))):
                return False
        if isinstance(expr1,Expr._InequalityExpression):
            if not len(expr1._args) == len(expr2._args):
                print len(expr1._args), "!=", len(expr2._args)
                return False
            if not all(expressions_equal(expr1._args[i],expr2._args[i]) for i in xrange(len(expr1._args))):
                return False
            if not len(expr1._cloned_from) == len(expr2._cloned_from):
                print len(expr1._cloned_from), "!=", len(expr2._cloned_from)
                return False
            if not all(expressions_equal(expr1._cloned_from[i],expr2._cloned_from[i]) for i in xrange(len(expr1._cloned_from))):
                return False
            
        # check that they pprint the same
        output1 = StringIO.StringIO()
        output2 = StringIO.StringIO()
        try:
            expr1.pprint(ostream=output1)
        except:
            output1.write(str(repr(expr1)))
        try:
            expr2.pprint(ostream=output2)
        except:
            output2.write(str(repr(expr2)))
        if not output1.getvalue() == output2.getvalue():
            print output1.getvalue(), "!=", output2.getvalue()
            output1.close()
            output2.close()
            return False
        output1.close()
        output2.close()
    else:
        if not value(expr1) == value(expr2):
            print value(expr1), "!=", value(expr2)
            return False

    return True

class ExprModTests(unittest.TestCase): pass
ExprModTests = unittest.category('smoke', 'nightly','expensive')(ExprModTests)


"""
The following test checks that sending a model to the nl writer does not
modify the original expressions on the model.
"""
@unittest.nottest
def nlwriter_exprmod_test(self,name):
    
    m = __import__(name)
    # This is critical, see note above
    reload(m)
    model = None
    if os.path.exists(currdir+name+'.dat'):
        model = m.model.create(filename=currdir+name+'.dat')
    else:
        model = m.model.create()
    del m
    model.concrete_mode()

    # Clone the original expressions
    Obj = model.active_components(Objective)
    orig_model_exprs = [ Obj[obj][i].expr.clone() for obj in Obj for i in Obj[obj] if isinstance(Obj[obj][i].expr,Expr.Expression) ]
    orig_model_exprs.extend([ Obj[obj][i].expr for obj in Obj for i in Obj[obj] if not isinstance(Obj[obj][i].expr,Expr.Expression) ])
    orig_model_exprs.extend([constraint[index].body.clone() \
                              for block in model.all_blocks() \
                              for constraint in itertools.chain(block.active_components(Constraint).itervalues(), block.active_components(ConstraintList).itervalues()) \
                              for index in sorted(constraint.keys()) if isinstance(constraint[index].body,Expr.Expression)])
    # Don't try to clone things that can't be cloned, e.g., a single var    
    orig_model_exprs.extend([constraint[index].body \
                              for block in model.all_blocks() \
                              for constraint in itertools.chain(block.active_components(Constraint).itervalues(), block.active_components(ConstraintList).itervalues()) \
                              for index in sorted(constraint.keys()) if not isinstance(constraint[index].body,Expr.Expression)])
    
    # Send the model to the nl writer
    model.write(filename=currdir+'exprtest.nl', format=ProblemFormat.nl, generate_symbolic_labels=False)

    # Generate a list of new model expressions
    Obj = model.active_components(Objective)
    model_exprs = [ Obj[obj][i].expr for obj in Obj for i in Obj[obj] if isinstance(Obj[obj][i].expr,Expr.Expression) ]
    model_exprs.extend([ Obj[obj][i].expr for obj in Obj for i in Obj[obj] if not isinstance(Obj[obj][i].expr,Expr.Expression) ])
    model_exprs.extend([constraint[index].body \
                              for block in model.all_blocks() \
                              for constraint in itertools.chain(block.active_components(Constraint).itervalues(), block.active_components(ConstraintList).itervalues()) \
                              for index in sorted(constraint.keys()) if isinstance(constraint[index].body,Expr.Expression)])
    # Don't try to clone things that can't be cloned, e.g., a single var    
    model_exprs.extend([constraint[index].body \
                              for block in model.all_blocks() \
                              for constraint in itertools.chain(block.active_components(Constraint).itervalues(), block.active_components(ConstraintList).itervalues()) \
                              for index in sorted(constraint.keys()) if not isinstance(constraint[index].body,Expr.Expression)])
    
    # Check that the expression in the new list match those in the old list
    for (expr1,expr2) in itertools.izip(model_exprs, orig_model_exprs):
        if not expressions_equal(expr1,expr2):
            try:
                expr1.pprint()
            except:
                print str(repr(expr1))
            try:
                expr2.pprint()
            except:
                print str(repr(expr2))
            self.fail(msg="expression not equal")
                
    # delete temp test files
    os.remove(currdir+'exprtest.nl')
    

for f in glob.glob(currdir+'*_testCase.py'):
    name = re.split('.',os.path.basename(f))[0]
    name = os.path.basename(f).replace('.py','')
    ExprModTests.add_fn_test(fn=nlwriter_exprmod_test, name=name)

if __name__ == "__main__":
    unittest.main()
