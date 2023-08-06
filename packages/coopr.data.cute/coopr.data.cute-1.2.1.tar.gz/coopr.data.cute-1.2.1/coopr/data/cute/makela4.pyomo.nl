g3 1 1 0	# problem unknown
 6 2 1 0 0	# vars, constraints, objectives, general inequalities, equalities
 2 1	# nonlinear constraints, objectives
 0 0	# network constraints: nonlinear, linear
 6 6 6	# nonlinear vars in constraints, objectives, both
 0 0 0 1	# linear network variables; functions; arith, flags
 0 0 0 0 0 	# discrete variables: binary, integer, nonlinear (b,c,o)
 6 6	# nonzeros in Jacobian, obj. gradient
 0 0	# max name lengths: constraints, variables
 0 0 0 0 0	# common exprs: b,c,o,c1,o1
C0	#cons1[None]
o0  #+
o2  #*
v0 #x11
v2 #x22
o2  #*
n-1
o5  #^
v1 #x12
n2 # numeric constant
C1	#cons2[None]
o0  #+
o2  #*
v3 #y11
v5 #y22
o2  #*
n-1
o5  #^
v4 #y12
n2 # numeric constant
O0 0	#f[None]
o0  #+
o5  #^
o0  #+
v0 #x11
o2  #*
n-1
v3 #y11
n2 # numeric constant
o0  #+
o2  #*
n2
o5  #^
o0  #+
v1 #x12
o2  #*
n-1
v4 #y12
n2 # numeric constant
o5  #^
o0  #+
v2 #x22
o2  #*
n-1
v5 #y22
n2 # numeric constant
x6
0 1 # x11 initial
1 1 # x12 initial
2 1 # x22 initial
3 1 # y11 initial
4 1 # y12 initial
5 1 # y22 initial
r
2 0.0  # c0  cons1
1 0.0  # c1  cons2
b
2 0  # v0  x11
3  # v1  x12
2 0  # v2  x22
1 0  # v3  y11
3  # v4  y12
1 0  # v5  y22
k5
1
2
3
4
5
J0 3  #  cons1
0   0
1   0
2   0
J1 3  #  cons2
3   0
4   0
5   0
G0 6
0   0
1   0
2   0
3   0
4   0
5   0
