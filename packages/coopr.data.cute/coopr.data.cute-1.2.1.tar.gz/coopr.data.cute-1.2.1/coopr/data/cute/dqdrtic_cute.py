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

#   Source: problem 22 in
#   Ph. L. Toint,
#   "Test problems for partially separable optimization and results
#   for the routine PSPMIN",
#   Report 83/4, Department of Mathematics, FUNDP (Namur, B), 1983.

#   SIF input: Ph. Toint, Dec 1989.

#   classification QUR2-AN-V-0

from coopr.pyomo import *
model = AbstractModel()

model.N = Param(initialize=5000)
model.S = RangeSet(1,model.N)
model.x = Var(model.S, initialize=3.0)

model.SS = RangeSet(1,model.N-2)
def f(model):
    return sum ([(100*model.x[i+1]**2+100*model.x[i+2]**2+model.x[i]**2) for i in model.SS])
model.f = Objective(rule=f,sense=minimize)
