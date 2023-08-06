g3 1 1 0	# problem unknown
 3 2 1 1 0	# vars, constraints, objectives, general inequalities, equalities
 1 1	# nonlinear constraints, objectives
 0 0	# network constraints: nonlinear, linear
 3 1 1	# nonlinear vars in constraints, objectives, both
 0 0 0 1	# linear network variables; functions; arith, flags
 0 0 0 0 0 	# discrete variables: binary, integer, nonlinear (b,c,o)
 4 3	# nonzeros in Jacobian, obj. gradient
 0 0	# max name lengths: constraints, variables
 0 0 0 0 0	# common exprs: b,c,o,c1,o1
C0	#cons1[None]
o0  #+
o5  #^
v0 #x[1]
n2 # numeric constant
o0  #+
o5  #^
v1 #x[2]
n2 # numeric constant
o5  #^
v2 #x[3]
n2 # numeric constant
C1	#cons2[None]
n0
O0 0	#f[None]
o0  #+
o5  #^
v0 #x[1]
n3 # numeric constant
o2  #*
n-6
o5  #^
v0 #x[1]
n2 # numeric constant
x3
0 xinit[1,] # x[1] initial
1 xinit[2,] # x[2] initial
2 xinit[3,] # x[3] initial
r
0 4.0 10.0  # c0  cons1
1 5.0  # c1  cons2
b
2 0  # v0  x[1]
2 0  # v1  x[2]
2 0  # v2  x[3]
k2
1
2
J0 3  #  cons1
0   0
1   0
2   0
J1 1  #  cons2
2   1.0
G0 3
0   11.0
1   1.0
2   1.0
