import pickle
from coopr.pyomo import *
from pyutilib.misc import Options
options = Options()
options.solver = "gurobi"
options.solver_io = "lp"
options.keepfiles = True
#options.tee = True
options.debug = True

kwds = {'pw_constr_type':'EQ','pw_repn':'SOS2','sense':maximize,'force_pw':True}

#problem_name = "piecewise_multi_vararray"
#problem_name = "concave_multi_vararray1"
#problem_name = "concave_multi_vararray2"
#problem_name = "convex_multi_vararray1"
#problem_name = "convex_multi_vararray2"
#problem_name = "convex_vararray"
#problem_name = "concave_vararray"
problem_name = "convex_var"
#problem_name = "concave_var"
#problem_name = "piecewise_var"
#problem_name = "piecewise_vararray"

p = __import__(problem_name)

model = p.define_model(**kwds)
inst = model.create()

inst.pprint()

data = Options(options=options)
opt_data = scripting.util.apply_optimizer(data,instance=inst)

results = opt_data.results

inst.load(results)

res = dict([(v[idx].name,v[idx].value) for (n,v) in inst.active_components(Var).iteritems() for idx in v if (n[:2] == 'Fx') or (n[:1] == 'x')])
print res

f = open(problem_name+'_baseline_results.pickle','w')
pickle.dump(res,f)
f.close()
