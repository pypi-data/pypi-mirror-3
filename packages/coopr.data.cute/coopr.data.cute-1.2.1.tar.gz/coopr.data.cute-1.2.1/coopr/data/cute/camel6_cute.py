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

#   Source: Six hump camel in
#   L. C. W. Dixon and G. P. Szego (Eds.)
#   Towards Global Optimization
#   North Holland, 1975.

#   SIF input: A.R. Conn May 1995

#   classification OBR2-AN-2-0

from coopr.pyomo import *
model = AbstractModel()

model.S = RangeSet(1,2)
model.x = Var(model.S, initialize=1.1)

def f(model):
    return 4*model.x[1]**2-2.1*model.x[1]**4+model.x[1]**6/3+model.x[1]*model.x[2]-4*model.x[2]**2+4*model.x[2]**4
model.f = Objective(rule=f,sense=minimize)

def cons1(model):
    return (-3,model.x[1],3)
model.cons1 = Constraint(rule=cons1)

def cons2(model):
    return (-1.5,model.x[2],1.5)
model.cons2 = Constraint(rule=cons2)
