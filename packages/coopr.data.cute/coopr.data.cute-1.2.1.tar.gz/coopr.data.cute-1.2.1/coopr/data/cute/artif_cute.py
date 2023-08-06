#  _________________________________________________________________________                                                                                \
#                                                                                                                                                           \
#  Coopr: A COmmon Optimization Python Repository                                                                                                           \
#  Copyright (c) 2010 Sandia Corporation.                                                                                                                   \
#  This software is distributed under the BSD License.                                                                                                      \
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,                                                                                   \
#  the U.S. Government retains certain rights in this software.                                                                                             \
#  For more information, see the Coopr README.txt file.                                                                                                     \
#  _________________________________________________________________________                                                                                \

# Formulated in Pyomo by Carl D. Laird, Daniel P. Word, and Brandon C. Barrera
# Taken from:

# AMPL Model by Hande Y. Benson
#
# Copyright (C) 2001 Princeton University
# All Rights Reserved
#
# Permission to use, copy, modify, and distribute this software and
# its documentation for any purpose and without fee is hereby
# granted, provided that the above copyright notice appear in all
# copies and that the copyright notice and this
# permission notice appear in all supporting documentation.

#   Source:
#   K.M. Irani, M.P. Kamat, C.J. Ribbens, H.F.Walker and L.T. Watson,
#   "Experiments with conjugate gradient algoritms for homotopy curve
#    tracking" ,
#   SIAM Journal on Optimization, May 1991, pp. 222-251, 1991.

#   SIF input: Ph. Toint, May 1990.

#   classification NOR2-AN-V-V

from coopr.pyomo import *
model = AbstractModel()

model.N = Param(initialize=5000)

model.S = RangeSet(0,model.N+1)
model.SS = RangeSet(1,model.N)


model.x = Var(model.S, initialize=1.0)
def fix1(model, i):
    if i == value(model.N)+1 or i == 0:
        model.x[i] = 0
        model.x[i].fixed=True
    return Constraint.Skip
model.fix1 = Constraint(model.S,rule=fix1)

def f(model):
    return 0
model.f = Objective(rule=f,sense=minimize)

def cons(model, i):
    expr = (-0.05*(model.x[i] + model.x[i+1] + model.x[i-1]) + atan( sin( (i%100)*model.x[i] ) ))
    return (0,expr)
model.cons = Constraint(model.SS, rule=cons)
