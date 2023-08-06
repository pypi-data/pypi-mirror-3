g3 1 1 0	# problem unknown
 3 3 1 0 0	# vars, constraints, objectives, general inequalities, equalities
 3 0	# nonlinear constraints, objectives
 0 0	# network constraints: nonlinear, linear
 2 0 0	# nonlinear vars in constraints, objectives, both
 0 0 0 1	# linear network variables; functions; arith, flags
 0 0 0 0 0 	# discrete variables: binary, integer, nonlinear (b,c,o)
 9 1	# nonzeros in Jacobian, obj. gradient
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
o0  #+
o5  #^
v1 #x[1]
n2 # numeric constant
o5  #^
v2 #x[2]
n2 # numeric constant
C2	#cons3[None]
o0  #+
o5  #^
v1 #x[1]
n2 # numeric constant
o5  #^
v2 #x[2]
n2 # numeric constant
O0 0	#f[None]
n0
x2
1 xinit[1,] # x[1] initial
2 xinit[2,] # x[2] initial
r
1 0.0  # c0  cons1
1 -40.0  # c1  cons2
1 -60.0  # c2  cons3
b
3  # v0  u
3  # v1  x[1]
3  # v2  x[2]
k2
3
6
J0 3  #  cons1
0   -1.0
1   0
2   0
J1 3  #  cons2
0   -1.0
1   -40.0
2   -10.0
J2 3  #  cons3
0   -1.0
1   -10.0
2   -20.0
G0 1
0   1.0
