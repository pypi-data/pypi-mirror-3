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
#   P.N. Brown and Y. Saad,
#   "Hybrid Krylov Methods for Nonlinear Systems of Equations",
#   SIAM J. Sci. Stat. Comput. 11, pp. 450-481, 1990.
#   The boundary conditions have been set according to
#   I.E. Kaporin and O. Axelsson,
#   "On a class of nonlinear equation solvers based on the residual norm
#   reduction over a sequence of affine subspaces",
#   SIAM J, Sci. Comput. 16(1), 1995.

#   SIF input: Ph. Toint, Jan 1995.

#   classification NQR2-MY-V-V

from coopr.pyomo import *
model = AbstractModel()
M = 100
model.M = Param(initialize=M)
model.H = Param(initialize=1.0/(M+2.0))
model.RE = Param(initialize=4500.0)

model.S1 = RangeSet(-1,M+2)
model.S2 = RangeSet(1,M)

model.y = Var(model.S1,model.S1,initialize=0.0)

def f(model):
    return 0
model.f = Objective(rule=f,sense=minimize)

def cons(model, i, j):
    return (20*model.y[i,j]-8*model.y[i-1,j]-8*model.y[i+1,j]\
    -8*model.y[i,j-1]-8*model.y[i,j+1]+2*model.y[i-1,j+1]+2*model.y[i+1,j-1]+2*model.y[i-1,j-1]+2*model.y[i+1,j+1] +\
    model.y[i-2,j] + model.y[i+2,j] + model.y[i,j-2] + model.y[i,j+2] + (value(model.RE)/4.0)*(model.y[i,j+1]-model.y[i,j-1])\
    *(model.y[i-2,j]+model.y[i-1,j-1]+model.y[i-1,j+1]-4*model.y[i-1,j]-4*model.y[i+1,j]-model.y[i+1,j-1] \
    -model.y[i+1,j+1] - model.y[i+2,j]) - (value(model.RE)/4.0)*(model.y[i+1,j]-model.y[i-1,j])*\
    (model.y[i,j-2]+model.y[i-1,j-1]+model.y[i+1,j-1]-4*model.y[i,j-1]-4*model.y[i,j+1]-model.y[i-1,j+1]-model.y[i+1,j+1] - model.y[i,j+2])) == 0
model.cons = Constraint(model.S2,model.S2,rule=cons)

def fix1(model, j):
    return model.y[-1,j] == 0.0
model.fix1 = Constraint(model.S1,rule=fix1)
                #model.y[-1,j].fixed=True
def fix2(model, j):
    return model.y[0,j] == 0.0
model.fix2 = Constraint(model.S1,rule=fix2)
                #model.y[0,j].fixed=True
def fix3(model, j):
    return model.y[value(model.M)+1,j] == -value(model.H)/2.0
model.fix3 = Constraint(model.S1,rule=fix3)
def fix4(model, j):
    return model.y[value(model.M)+2,j] == value(model.H)/2.0
model.fix4 = Constraint(model.S1,rule=fix4)

def fix5(model, i):
    return model.y[i,-1] == 0.0
model.fix5 = Constraint(model.S2,rule=fix5)
                #model.y[i,-1].fixed=True
def fix6(model, i):
    return model.y[i,0] == 0.0
model.fix6 = Constraint(model.S2,rule=fix6)
                #model.y[i,0].fixed=True
def fix7(model, i):
    return model.y[i,value(model.M)+1] == 0.0
model.fix7 = Constraint(model.S2,rule=fix7)
def fix8(model, i):
    return model.y[i,value(model.M)+2] == 0.0
model.fix8 = Constraint(model.S2,rule=fix8)
