from coopr.pyomo import *

model = AbstractModel()

model.a = Param(initialize=2)

model.x = Var(within=NonNegativeReals)
model.y = Var(within=NonNegativeReals)
model.z = Var(within=NonNegativeReals,bounds=(7,None))
model.v = Var(within=NonNegativeReals)

def obj_rule(model):
    return 1.0*model.z + 2.0*model.x*model.x + 3.0*model.y + 4.0*model.v**2 - model.x*model.z + 1.5*(model.x+model.z)**2
model.obj = Objective(rule=obj_rule,sense=minimize)

def constr_rule(model):
    return (model.a,model.y*model.y,None)
model.constr = Constraint(rule=constr_rule)

def constr2_rule(model):
    return model.x/model.a >= model.y
model.constr2 = Constraint(rule=constr2_rule)

def constr3_rule(model):
    return model.z <= model.y + model.a
model.constr3 = Constraint(rule=constr3_rule)

def constr4_rule(model):
    return model.v**2 >= 1
model.constr4 = Constraint(rule=constr4_rule)

