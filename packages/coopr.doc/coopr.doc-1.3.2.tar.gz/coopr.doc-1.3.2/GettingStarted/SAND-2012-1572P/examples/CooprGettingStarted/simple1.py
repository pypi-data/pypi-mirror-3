from coopr.pyomo import *

# @body:
model = AbstractModel()
model.I = Set()
model.p = Param(model.I)
# @:body
