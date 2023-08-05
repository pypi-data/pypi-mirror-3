from coopr.pyomo import *

model = AbstractModel()

model.a = Param(initialize=2)

model.x = Var(within=NonNegativeReals)
model.y = Var(within=NonNegativeReals)
model.z = Var(within=NonNegativeReals,bounds=(7,None))

def obj_rule(model):
    return model.z + model.x*model.x + model.y
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

