#import cPickle
import pickle
from coopr.pyomo import *
from pyutilib.misc import Options
options = Options()
options.solver = "cplex"
options.solver_io = "lp"
options.keepfiles = True
options.tee = True
options.debug = True

kwds = {'pw_constr_type':'LB','pw_repn':'SOS2','sense':minimize}

#import piecewise_multi_vararray as p
#import concave_multi_vararray1 as p
import convex_var as p
#import concave_var as p
#import piecewise_var as p
#import piecewise_vararray as p

model = p.define_model(**kwds)
inst = model.create()

#inst.pprint()
#print inst.piecewise.index

results,opt = scripting.util.apply_optimizer(options,inst)

f = open('out','w')
pickle.dump(results,f)
f.close()

inst.load(results)
#display(inst.piecewise_y_BIGM_SOS1
#display(inst.Fx)
#display(inst.Fx1)
#display(inst.Fx2)
#display(inst.Fx3)
#display(inst.Fx4)
#display(inst.Fx5)
#display(inst.Fx6)
#ydisplay(inst.Fx7)

#f = open('out','w')
#cPickle.dump(results,f)
#f.close()
