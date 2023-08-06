g3 1 1 0	# problem unknown
 5 5 1 0 5	# vars, constraints, objectives, general inequalities, equalities
 5 0	# nonlinear constraints, objectives
 0 0	# network constraints: nonlinear, linear
 5 0 0	# nonlinear vars in constraints, objectives, both
 0 0 0 1	# linear network variables; functions; arith, flags
 0 0 0 0 0 	# discrete variables: binary, integer, nonlinear (b,c,o)
 23 0	# nonzeros in Jacobian, obj. gradient
 0 0	# max name lengths: constraints, variables
 0 0 0 0 0	# common exprs: b,c,o,c1,o1
C0	#cons1[None]
o0  #+
o2  #*
n-0.727
o2  #*
v1 #pitchrat
v4 #yawrate
o0  #+
o2  #*
n8.39
o2  #*
v4 #yawrate
v0 #attckang
o0  #+
o2  #*
n-684.4
o2  #*
v0 #attckang
v3 #sslipang
o2  #*
n63.5
o2  #*
v1 #pitchrat
v0 #attckang
C1	#cons2[None]
o0  #+
o2  #*
n0.949
o2  #*
v2 #rollrate
v4 #yawrate
o2  #*
n0.173
o2  #*
v2 #rollrate
v3 #sslipang
C2	#cons3[None]
o0  #+
o2  #*
n-0.716
o2  #*
v2 #rollrate
v1 #pitchrat
o0  #+
o2  #*
n-1.578
o2  #*
v2 #rollrate
v0 #attckang
o2  #*
n1.132
o2  #*
v1 #pitchrat
v0 #attckang
C3	#cons4[None]
o2  #*
n-1
o2  #*
v2 #rollrate
v3 #sslipang
C4	#cons5[None]
o2  #*
v2 #rollrate
v0 #attckang
O0 0	#f[None]
n0.0
x5
0 0.0 # attckang initial
1 0.0 # pitchrat initial
2 0.0 # rollrate initial
3 0.0 # sslipang initial
4 0.0 # yawrate initial
r
4 0.0  # c0  cons1
4 2.837  # c1  cons2
4 0.0  # c2  cons3
4 0.1168  # c3  cons4
4 0.0  # c4  cons5
b
3  # v0  attckang
3  # v1  pitchrat
3  # v2  rollrate
3  # v3  sslipang
3  # v4  yawrate
k4
5
9
14
19
J0 5  #  cons1
0   0
1   0.107
2   -3.933
3   -9.99
4   0.126
J1 5  #  cons2
0   -22.95
1   -0.987
2   0
3   0
4   0
J2 5  #  cons3
0   0
1   0
2   0.002
3   5.67
4   -0.235
J3 4  #  cons4
0   -1.0
1   1.0
2   0
3   0
J4 4  #  cons5
0   0
2   0
3   -0.196
4   -1.0
