# Identical to example1.py except using linearizations
# at user given tangent points
#
#          / -X+2 , -5 <= X <= 1
#  Z(X) >= |
#          \  X ,  1 <= X <= 5

from coopr.pyomo import *

# Define the function
# Just like in Pyomo constraint rules, a Pyomo model object
# must be the first argument for the function rule
def f(model,x):
    return abs(x-1) + 1.0

# Define the derivative
def df(model,x):
    if x < 1:
        return -1
    else:
        return 1

model = ConcreteModel()

# Unlike example1.py, bounds on model.X are needed since
# linearizations don't provide outer bounds. In this 
# case the solution is at X=1 so the bounds aren't 
# really needed.
model.X = Var(bounds=(-5,5))
model.Z = Var()

# See documentation on Piecewise component by typing
# help(Piecewise) in a python terminal after importing coopr.pyomo
model.con = Piecewise(model.Z,model.X, # range and domain variables
                      tan_pts=[-5,5],
                      tan_constr_type='LB',
                      f_rule=f,
                      d_f_rule=df)

model.obj = Objective(expr=model.Z, sense=minimize)

