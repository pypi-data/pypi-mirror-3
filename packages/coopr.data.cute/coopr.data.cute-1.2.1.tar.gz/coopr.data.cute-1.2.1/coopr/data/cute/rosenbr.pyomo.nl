g3 1 1 0	# problem unknown
 2 0 1 0 0	# vars, constraints, objectives, general inequalities, equalities
 0 1	# nonlinear constraints, objectives
 0 0	# network constraints: nonlinear, linear
 0 2 0	# nonlinear vars in constraints, objectives, both
 0 0 0 1	# linear network variables; functions; arith, flags
 0 0 0 0 0 	# discrete variables: binary, integer, nonlinear (b,c,o)
 0 2	# nonzeros in Jacobian, obj. gradient
 0 0	# max name lengths: constraints, variables
 0 0 0 0 0	# common exprs: b,c,o,c1,o1
O0 0	#f[None]
o0  #+
o2  #*
n100.0
o5  #^
o0  #+
v1 #x[2]
o2  #*
n-1
o5  #^
v0 #x[1]
n2 # numeric constant
n2 # numeric constant
o5  #^
o0  #+
n-1
v0 #x[1]
n2 # numeric constant
x2
0 xinit[1,] # x[1] initial
1 xinit[2,] # x[2] initial
r
b
3  # v0  x[1]
3  # v1  x[2]
k1
0
G0 2
0   0
1   0
