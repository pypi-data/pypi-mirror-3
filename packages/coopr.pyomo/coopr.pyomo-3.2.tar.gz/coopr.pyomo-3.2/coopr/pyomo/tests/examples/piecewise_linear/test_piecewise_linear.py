import os
import pyutilib.th as unittest
from pyutilib.misc.pyyaml_util import *
import coopr.pyomo.scripting.util as util
from coopr.pyomo.base import Var
import coopr.plugins
from coopr.pyomo.base.objective import minimize, maximize
import cPickle

currdir = os.path.dirname(os.path.abspath(__file__))

smoke_problems = ['convex_var']

nightly_problems = ['convex_vararray', 'concave_vararray', \
                'concave_var','piecewise_var', 'piecewise_vararray']

expensive_problems = ['piecewise_multi_vararray', \
                'convex_multi_vararray1','concave_multi_vararray1', \
                'convex_multi_vararray2','concave_multi_vararray2']


def module_available(module):
    try:
        __import__(module)
        return True
    except ImportError:
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

def has_gurobi_python():
    if module_available('gurobipy'):
        return True
    return False

def has_cplex_lp():
    try:
        cplex = coopr.plugins.solvers.CPLEX(keepFiles=True)
        available = (not cplex.executable() is None) and cplex.available(False)
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

def has_cplex_python():
    if module_available('cplex'):
        return True
    return False

def has_glpk_python():
    if module_available('glpk'):
        return True
    return False

def has_glpk_lp():
    try:
        glpk = coopr.plugins.solvers.GLPK(keepFiles=True)
        available = (not glpk.executable() is None) and glpk.available(False)
        return available
    except pyutilib.common.ApplicationError:
        return False

writer_solver = []
#if has_cplex_python():
#    writer_solver.append(('python','cplex'))
#if has_gurobi_python():
#    writer_solver.append(('python','gurobi'))
if has_cplex_lp():
    writer_solver.append(('lp','cplex'))
#if has_gurobi_lp():
#    writer_solver.append(('lp','gurobi'))
#if has_cplex_nl():
#    writer_solver.append(('nl','cplexamp'))
#if has_gurobi_nl():
#    writer_solver.append(('nl','gurobi_ampl'))
#if has_glpk_lp():
#    writer_solver.append(('lp','glpk'))
#if has_glpk_python():
#    writer_solver.append(('python','glpk'))


def createTestMethod(pName,problem,solver,writer,kwds):
    
    def testMethod(obj):

        from pyutilib.misc import Options
        os.sys.path.append(currdir+'/problems')
        m = __import__(problem)
        os.sys.path.pop()
        options = Options()
        options.solver = solver
        options.solver_io = writer
        options.quiet = True
        options.debug = True
        data = Options(options=options)
        
        model = m.define_model(**kwds)
        model.reset()
        instance = model.create()

        opt_data = util.apply_optimizer(data, instance=instance)
        
        instance.load(opt_data.results)
        
        new_results = ( (v[idx].name,v[idx].value) for (n,v) in instance.active_components(Var).iteritems() \
                                                 for idx in v \
                                                 if (n[:2] == 'Fx') \
                                                 or (n[:1] == 'x') )
        baseline_results = getattr(obj,problem+'_results')
        
        for name, value in new_results:
            if abs(baseline_results[name]-value) > 0.00001:
                raise IOError, "Difference in baseline solution values and current solution values using:\n" + \
                "Solver: "+solver+"\n" + \
                "Writer: "+writer+"\n" + \
                "Variable: "+name+"\n" + \
                "Solution: "+str(value)+"\n" + \
                "Baseline: "+str(baseline_results[name])+"\n"

    return testMethod


def assignTests(cls, problem_list):
    for writer,solver in writer_solver:
        for PROBLEM in problem_list:
            aux_list = ['','force_pw']
            for AUX in aux_list:
                for REPN in ['SOS2','BIGM_SOS1','BIGM_BIN','DCC','DLOG','CC','LOG','MC','INC']:
                    for BOUND_TYPE in ['UB','LB','EQ']:
                        for SENSE in [maximize,minimize]:
                            if not(((BOUND_TYPE == 'LB') and (SENSE == maximize)) or \
                                   ((BOUND_TYPE == 'UB') and (SENSE == minimize))):
                                kwds = {}
                                kwds['sense'] = SENSE
                                kwds['pw_repn'] = REPN
                                kwds['pw_constr_type'] = BOUND_TYPE
                                if SENSE == maximize:
                                    attrName = "test_{0}_{1}_{2}_{3}_{4}_{5}".format(PROBLEM,REPN,BOUND_TYPE,'maximize',solver,writer)
                                elif SENSE == minimize:
                                    attrName = "test_{0}_{1}_{2}_{3}_{4}_{5}".format(PROBLEM,REPN,BOUND_TYPE,'minimize',solver,writer)
                                if AUX != '':
                                    kwds[AUX] = True 
                                    attrName += '_'+AUX
                                setattr(cls,attrName,createTestMethod(attrName,PROBLEM,solver,writer,kwds))


@unittest.category('nightly', 'expensive')
@unittest.skipIf(writer_solver==[], "Can't find a solver.")
class PiecewiseLinearTest_Nightly(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        for p in nightly_problems:
            f = open(currdir+'/baselines/'+p+'_baseline_results.pickle','r')
            baseline_results = cPickle.load(f)
            setattr(self,p+'_results',baseline_results)
            f.close()
    
assignTests(PiecewiseLinearTest_Nightly, nightly_problems)


@unittest.category('smoke', 'nightly', 'expensive')
@unittest.skipIf(writer_solver==[], "Can't find a solver.")
class PiecewiseLinearTest_Smoke(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        for p in smoke_problems:
            f = open(currdir+'/baselines/'+p+'_baseline_results.pickle','r')
            baseline_results = cPickle.load(f)
            setattr(self,p+'_results',baseline_results)
            f.close()
        
assignTests(PiecewiseLinearTest_Smoke, smoke_problems)


@unittest.category('expensive')
@unittest.skipIf(writer_solver==[], "Can't find a solver.")
class PiecewiseLinearTest_Expensive(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        for p in expensive_problems:
            f = open(currdir+'/baselines/'+p+'_baseline_results.pickle','r')
            baseline_results = cPickle.load(f)
            setattr(self,p+'_results',baseline_results)
            f.close()
    
assignTests(PiecewiseLinearTest_Expensive, expensive_problems)

