# Nonlinear version of example4.
# Must have a nonlinear solver
# to run this example.
from coopr.pyomo import *
from example4 import model,f

# Reuse the rule from example4 to define the 
# nonlinear constraint
def nonlinear_con_rule(model,i,j,k):
    return model.Z[i,j,k] == f(model,i,j,k,model.X[i,j,k])
model.nonlinear_constraint = Constraint(model.INDEX1,model.INDEX2,rule=nonlinear_con_rule)

# deactivate all constraints representing the piecewise-linear
# version of the model
model.linearized_constraint.deactivate()

# initialize the nonlinear variables to 'good' starting points
for idx in model.X.index():
    model.X[idx] = 1.7
    model.Z[idx] = 1.25
