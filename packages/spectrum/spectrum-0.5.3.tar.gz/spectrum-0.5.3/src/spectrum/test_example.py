import numpy

#TOEPLITZ
#example marple app 3.A
A_cholesky = numpy.matrix([[2+0.j, .5-0.5j,-.2+.1j],[.5+.5j,1,.3-0.2j],[-.2-.1j,.3+.2j,.5]], dtype=complex)
a_cholesky = numpy.array([2+0.j, .5-0.5j, 1., -.2+.1j,.3-0.2j,.5], dtype=complex)
B_cholesky = numpy.array([1+3j,2-1j,.5+.8j], dtype=complex)
#should return 
sol_cholesky = numpy.array([ 0.95945946+5.25675676j, 4.41891892-7.04054054j, -5.13513514+6.35135135j])


#LEVINSON
T0_levinson = 3
T_levinson = numpy.array([-2+0.5j, .7-1j])
P_levinson = 1.3221
A_levinson = numpy.array([.86316+0.31158j, .34737+0.21053j])

