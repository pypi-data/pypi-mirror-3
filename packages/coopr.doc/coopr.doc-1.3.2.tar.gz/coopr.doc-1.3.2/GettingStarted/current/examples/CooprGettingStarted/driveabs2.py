# driveabs2.py
from coopr.pyomo import *
from coopr.opt import SolverFactory

# Create a solver
opt = SolverFactory('cplex')

# get the model from another file
from abstract2 import model

# Create a model instance and optimize
instance = model.create('abstract2.dat')
results = opt.solve(instance, suffixes=['dual'])

# get the results back into the instance for easy access
instance.load(results)

# display all duals
print "Duals"
from coopr.pyomo import Constraint
for c in instance.active_components(Constraint):
    print "   Constraint",c
    cobject = getattr(instance, c)
    for index in cobject:
        print "      ", index, cobject[index].dual

# access (display, this case) one dual
print "Dual for Film=", instance.AxbConstraint['Film'].dual


