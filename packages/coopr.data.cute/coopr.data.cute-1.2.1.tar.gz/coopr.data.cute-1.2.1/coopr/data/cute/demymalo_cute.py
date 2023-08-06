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
#   V.F. Demynanov and V.N. Malozemov
#   "Introduction to Minimax"
#   Wiley, 1974

#   SIF input: Ph. Toint, Nov 1993.

#   classification  LQR2-AN-3-3

from coopr.pyomo import *
model = AbstractModel()

model.S = RangeSet(1,2)
model.xinit = Param(model.S)
def xit(model, i):
    return value(model.xinit[i])
model.x = Var(model.S,initialize=xit)
model.u = Var()

def f(model):
    return model.u
model.f = Objective(rule=f,sense=minimize)

def cons1(model):
    return -model.u+5*model.x[1]+model.x[2] <= 0
model.cons1 = Constraint(rule=cons1)
def cons2(model):
    return -model.u-5*model.x[1]+model.x[2] <= 0
model.cons2 = Constraint(rule=cons2)
def cons3(model):
    return -model.u+4*model.x[2]+model.x[1]**2+model.x[2]**2 <= 0
model.cons3 = Constraint(rule=cons3)
