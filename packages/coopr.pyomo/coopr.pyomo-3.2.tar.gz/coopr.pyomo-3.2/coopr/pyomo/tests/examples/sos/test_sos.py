import os
import pyutilib.th as unittest
from pyutilib.misc.pyyaml_util import *
import coopr.pyomo.scripting.util as util
import coopr.plugins
from pyutilib.misc import Options
import pickle
import pyutilib
from coopr.pyomo.base import Var

currdir = os.path.dirname(os.path.abspath(__file__))
os.sys.path.append(currdir)

problem_list = ['multidimen_sos2','sos2','multidimen_sos1','sos1','sos1_no_index','sos2_no_index']

def module_available(module):
    try:
        __import__(module)
        return True
    except ImportError:
        return False

def has_python(name):
    if module_available(name):
        return True
    return False

def has_gurobi_lp():
    try:
        gurobi = coopr.plugins.solvers.GUROBI(keepFiles=True)
        available = (not gurobi.executable() is None) and gurobi.available(False)
        return available
    except pyutilib.common.ApplicationError:
        return False

def has_gurobi_nl():
    try:
        gurobi = coopr.plugins.solvers.GUROBI(keepFiles=True)
        available = (not gurobi.executable() is None) and gurobi.available(False)
        asl = coopr.plugins.solvers.ASL(keepFiles=True, options={'solver':'gurobi_ampl'})
        return available and (not asl.executable() is None) and asl.available(False)
    except pyutilib.common.ApplicationError:
        return False

def has_cplex_lp():
    try:
        cplex = coopr.plugins.solvers.CPLEX(keepFiles=True)
        available = (not cplex.executable() is None) and cplex.available(False)
        return available
    except pyutilib.common.ApplicationError:
        return False
    
def has_cbc_lp():
    try:
        cbc = coopr.plugins.solvers.CBC(keepFiles=True)
        available = (not cbc.executable() is None) and cbc.available(False)
        return available
    except pyutilib.common.ApplicationError:
        return False
    
def has_pico_lp():
    try:
        PICO = coopr.plugins.solvers.PICO(keepFiles=True)
        available = (not PICO.executable() is None) and PICO.available(False)
        return available
    except pyutilib.common.ApplicationError:
        return False

def has_cplex_nl():
    try:
        cplex = coopr.plugins.solvers.CPLEX(keepFiles=True)
        available = (not cplex.executable() is None) and cplex.available(False)
        asl = coopr.plugins.solvers.ASL(keepFiles=True, options={'solver':'cplexamp'})
        return available and (not asl.executable() is None) and asl.available(False)
    except pyutilib.common.ApplicationError:
        return False

def has_glpk_lp():
    try:
        glpk = coopr.plugins.solvers.GLPK(keepFiles=True)
        available = (not glpk.executable() is None) and glpk.available(False)
        return available
    except pyutilib.common.ApplicationError:
        return False

writer_solver = []
if has_python('cplex'):
    writer_solver.append(('python','cplex',True))
else:
    writer_solver.append(('python','cplex',False))

if has_python('gurobipy'):
    writer_solver.append(('python','gurobi',True))
else:
    writer_solver.append(('python','gurobi',False))

if has_cplex_lp():
    writer_solver.append(('lp','cplex',True))
else:
    writer_solver.append(('lp','cplex',False))

if has_gurobi_lp():
    writer_solver.append(('lp','gurobi',True))
else:
    writer_solver.append(('lp','gurobi',False))
    
if has_cplex_nl():
    writer_solver.append(('nl','cplexamp',True))
else:
    writer_solver.append(('nl','cplexamp',False))
    
if has_gurobi_nl():
    writer_solver.append(('nl','gurobi_ampl',True))
else:
    writer_solver.append(('nl','gurobi_ampl',False))
    
# Does not support sos
"""
if has_python('glpk'):
    writer_solver.append(('python','glpk',True))
else:
    writer_solver.append(('python','glpk',False))
"""
# Does not support sos
"""
if has_glpk_lp():
    writer_solver.append(('lp','glpk',True))
else:
    writer_solver.append(('lp','glpk',False))
"""
# Does not support sos 
"""
if has_cbc_lp():
    writer_solver.append(('lp','cbc',True))
else:
    writer_solver.append(('lp','cbc',False))
"""
# Does not support sos since uses glpk
"""
if has_pico_lp():
    writer_solver.append(('lp','pico',True))
else:
    writer_solver.append(('lp','pico',False))
"""

def createTestMethod(pName,problem,solver,writer,do_test):
    
    
    message = solver+"_"+writer+" not available"
    
    @unittest.skipUnless(do_test,message)
    def testMethod(obj):
        # Since we are comparing solutions over different writers to a baseline,
        # we cannot use the .yml solution files as a basis. Therefore we must
        # check that individual variable values are the same. Currently, a 
        # pickled results opbject is used as the baseline solution.

        options = Options()
        options.solver = solver
        options.solver_io = writer
        options.quiet = True
        data = Options(options=options)

        model = obj.m[problem].define_model()
        instance = model.create()

        opt_data = util.apply_optimizer(data, instance=instance)
        
        instance.load(opt_data.results)
        
        baseline_results = obj.b[problem]
        
        for block in instance.all_blocks():
            for variable in block.active_components(Var).itervalues():
                for ndx in variable:
                    var = variable[ndx]
                    bF = baseline_results[var.name]
                    F = var.value
                    if abs(F-bF) > 0.000001:
                        raise IOError, "Difference in baseline solution values and current solution values using:\n" + \
                            "Problem: "+problem+".py\n" + \
                            "Solver: "+solver+"\n" + \
                            "Writer: "+writer+"\n" + \
                            "Variable: "+name+"\n" + \
                            "Solution: "+str(F)+"\n" + \
                            "Baseline: "+str(bF)+"\n"

    return testMethod

def assignTests(cls):
    for PROBLEM in problem_list:
        for writer,solver,do_test in writer_solver:
            attrName = "test_sos_{0}_{1}_{2}".format(PROBLEM,solver,writer)
            setattr(cls,attrName,createTestMethod(attrName,PROBLEM,solver,writer,do_test))

@unittest.skipIf(writer_solver==[], "Can't find a solver.")
class SOSTest(unittest.TestCase):
    
    @classmethod
    def setUpClass(self):
        self.m = {}
        self.b = {}
        for p in problem_list:
            self.m[p] = __import__(p)
            f = open(currdir+'/baselines/'+p+'_baseline_results.pickle','r')
            results = pickle.load(f)
            self.b[p] = results
            f.close()

assignTests(SOSTest)
