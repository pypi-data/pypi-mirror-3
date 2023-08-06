g3 1 1 0	# problem unknown
 3 2 1 0 0	# vars, constraints, objectives, general inequalities, equalities
 1 0	# nonlinear constraints, objectives
 0 0	# network constraints: nonlinear, linear
 2 0 0	# nonlinear vars in constraints, objectives, both
 0 0 0 1	# linear network variables; functions; arith, flags
 0 0 0 0 0 	# discrete variables: binary, integer, nonlinear (b,c,o)
 5 1	# nonzeros in Jacobian, obj. gradient
 0 0	# max name lengths: constraints, variables
 0 0 0 0 0	# common exprs: b,c,o,c1,o1
C0	#cons1[None]
o0  #+
o5  #^
v1 #x[1]
n2 # numeric constant
o5  #^
v2 #x[2]
n2 # numeric constant
C1	#cons2[None]
n0
O0 0	#f[None]
n0
x2
1 xinit[1,] # x[1] initial
2 xinit[2,] # x[2] initial
r
1 1.0  # c0  cons1
1 0.0  # c1  cons2
b
3  # v0  u
3  # v1  x[1]
3  # v2  x[2]
k2
2
4
J0 3  #  cons1
0   -1.0
1   -1.0
2   0
J1 2  #  cons2
0   -1.0
1   -1.0
G0 1
0   1.0
