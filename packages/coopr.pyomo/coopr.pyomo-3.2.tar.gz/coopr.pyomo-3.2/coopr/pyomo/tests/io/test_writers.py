import pyutilib.th as unittest
from coopr.opt import *
from model import model
import coopr
from coopr.pyomo.base import Var

try:
    cplex = coopr.plugins.solvers.CPLEX(keepFiles=True)
    cplex_available = (not cplex.executable() is None) and cplex.available(False)
    asl = coopr.plugins.solvers.ASL(keepFiles=True, options={'solver':'cplexamp'})
    cplexamp_available = cplex_available and (not asl.executable() is None) and asl.available(False)
    try:
        import cplex
        cplexpy_available = True
    except ImportError:
        cplexpy_available = False
except pyutilib.common.ApplicationError:
    cplexamp_available=False

try:
    gurobi = coopr.plugins.solvers.GUROBI(keepFiles=True)
    gurobi_available = (not gurobi.executable() is None) and gurobi.available(False)
    asl = coopr.plugins.solvers.ASL(keepFiles=True, options={'solver':'gurobi_ampl'})
    gurobi_ampl_available = gurobi_available and (not asl.executable() is None) and asl.available(False)
    try:
        import gurobipy
        gurobi_py_available = True
    except ImportError:
        gurobi_py_available = False
except pyutilib.common.ApplicationError:
    gurobi_ampl_available=False

class WriterTests(unittest.TestCase):

    @unittest.skipIf(not (cplex_available and cplexamp_available),"The 'cplex' executable is not available")
    def testCPLEXnl(self):
        self.instancelp=model.create()
        self.instancenl=model.create()

        self.optlp=SolverFactory("cplex",solver_io="lp")
        self.optnl=SolverFactory("cplex",solver_io="nl")

        self.resultslp=self.optlp.solve(self.instancelp)
        self.resultsnl=self.optnl.solve(self.instancenl)

        self.instancelp.load(self.resultslp)
        self.instancenl.load(self.resultsnl)
        
        self.assertAlmostEqual(self.instancelp.obj(),self.instancenl.obj())
        for i, val in self.instancelp.active_components(Var).iteritems():
            self.assertAlmostEqual( val(),
                              self.instancenl.active_components(Var)[i]() )

    @unittest.skipIf(not (cplex_available and cplexpy_available),"The 'cplex' python interface is not available")
    def testCPLEXpy(self):
        self.instancelp=model.create()
        self.instancepy=model.create()

        self.optlp=SolverFactory("cplex",solver_io="lp")
        self.optpy=SolverFactory("cplex",solver_io="python")

        self.resultslp=self.optlp.solve(self.instancelp)
        self.resultspy=self.optpy.solve(self.instancepy)

        self.instancelp.load(self.resultslp)
        self.instancepy.load(self.resultspy)
        
        self.assertAlmostEqual(self.instancelp.obj(),self.instancepy.obj(), delta=1e-3)
        for i, val in self.instancelp.active_components(Var).iteritems():
            self.assertAlmostEqual( val(),
                              self.instancepy.active_components(Var)[i](), delta=1e-3 )

    @unittest.skipIf(not (gurobi_available and gurobi_ampl_available),"The 'gurobi executable is not available") 
    def testGUROBInl(self):
        self.instancelp=model.create()
        self.instancenl=model.create()

        #Deactivate quadratic constraints -- gurobi currently doesn't support those
        self.instancelp.constr.active = False
        self.instancelp.preprocess()
        self.instancenl.constr.active = False
        self.instancenl.preprocess()

        self.optlp=SolverFactory("gurobi",solver_io="lp")
        self.optnl=SolverFactory("gurobi_ampl",solver_io="nl")

        self.resultslp=self.optlp.solve(self.instancelp)
        self.resultsnl=self.optnl.solve(self.instancenl)

        self.instancelp.load(self.resultslp)
        self.instancenl.load(self.resultsnl)
        
        self.assertAlmostEqual(self.instancelp.obj(),self.instancenl.obj())
        for i, val in self.instancelp.active_components(Var).iteritems():
            self.assertAlmostEqual( val(),
                              self.instancenl.active_components(Var)[i]() )

    @unittest.skipIf(not (gurobi_available and gurobi_py_available),"The 'gurobi python interface is not available") 
    def testGUROBIpy(self):
        self.instancelp=model.create()
        self.instancepy=model.create()

        #Deactivate quadratic constraints -- gurobi currently doesn't support those
        self.instancelp.constr.active = False
        self.instancelp.preprocess()
        self.instancepy.constr.active = False
        self.instancepy.preprocess()

        self.optlp=SolverFactory("gurobi",solver_io="lp")
        self.optpy=SolverFactory("gurobi",solver_io="python")

        self.resultslp=self.optlp.solve(self.instancelp)
        self.resultspy=self.optpy.solve(self.instancepy)

        self.instancelp.load(self.resultslp)
        self.instancepy.load(self.resultspy)
        
        self.assertAlmostEqual(self.instancelp.obj(),self.instancepy.obj())
        for i, val in self.instancelp.active_components(Var).iteritems():
            self.assertAlmostEqual( val(),
                              self.instancepy.active_components(Var)[i]() )


if __name__ == "__main__":
    unittest.main()
