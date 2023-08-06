"""Linear prediction tools

:References: [Kay]_
"""

from levinson import LEVINSON, rlevinson
import numpy

__all__ = ['ac2poly', 'poly2ac', 'ac2rc', 'rc2poly', 'rc2ac', 'is2rc', 'rc2is', 'rc2lar', 'lar2rc', 'poly2rc']

"""
lpc Linear prediction filter coefficients
lsf2poly    Convert line spectral frequencies to prediction filter coefficients
poly2lsf    Convert prediction filter coefficients to line spectral frequencies
schurrc Compute reflection coefficients from autocorrelation sequence
"""


def ac2poly(data):
    """Convert autocorrelation sequence to prediction polynomial

    :param array data:    input data (list or numpy.array)
    :return: 
        * AR parameters
        * noise variance

    This is an alias to::

        a, e, c = LEVINSON(data)

    :Example:

    .. doctest::

        >>> r = [5, -2, 1]
        >>> ar, e = ac2poly(r)
        >>> ar
        array([ 1. ,  0. , -0.2])
        >>> e
        4.7999999999999998

    """
    a, e, _c = LEVINSON(data)
    a = numpy.insert(a, 0, 1) 
    return a, e


def ac2rc(data):
    """Convert autocorrelation sequence to reflection coefficients

    :param data: an autorrelation vector
    :return: the reflection coefficient and data[0]

    This is an alias to::

        a, e, c = LEVINSON(data)
        c, data[0]

    """
    a, e, _c = LEVINSON(data)
    return a, data[0]
    
    
def poly2ac(poly, efinal):
    """ Convert prediction filter polynomial to autocorrelation sequence

    :param array poly: the AR parameters
    :param efinal: an estimate of the final error
    :return: the autocorrelation  sequence

    .. doctest::

        >>> ar = [ 1. ,  0. , -0.2]
        >>> efinal = 4.8
        >>> r = poly2ac(ar, efinal)

    """
    results = rlevinson(poly, efinal)
    return results[0] 
    
def ar2rc(ar):
    """ Convert autoregressive parameters into reflection coefficients """
    raise NotImplementedError
    
    
def poly2rc(a, efinal):
    """Convert prediction filter polynomial to reflection coefficients

    :param a: AR parameters
    :param efinal: 
    """
    results = rlevinson(a, efinal)
    return results[2]
    
def rc2poly(kr, r0=None):
    """convert reflection coefficients to prediction filter polynomial

    :param k: reflection coefficients




    """
    # Initialize the recursion
    from levinson import levup
    p = len(kr)              #% p is the order of the prediction polynomial.
    a = numpy.array([1, kr[0]])           #% a is a true polynomial.
    e = numpy.zeros(5)

    if r0 == None:
        e0 = 0
    else:
        e0 = r0

    e[0] = e0 * (1. - numpy.conj(numpy.conjugate(kr[0])*kr[0]))

    # Continue the recursion for k=2,3,...,p, where p is the order of the 
    # prediction polynomial.

    for k in range(1, p):
        [a, e[k]] = levup(a, kr[k], e[k-1])

    efinal = e[-1]
    return a, efinal


def rc2ac(k,R0):
    """Convert reflection coefficients to autocorrelation sequence.

    :param k: reflection coefficients
    :param R0: zero-lag autocorrelation
    :returns: the autocorrelation sequence

    .. seealso:: :func:`ac2rc`, :func:`poly2rc`, :func:`ac2poly`, :func:`poly2rc`, :func:`rc2poly`.

    """
    [a,efinal] = rc2poly(k, R0)
    R, u, kr, e = rlevinson(a, efinal)
    return R


def is2rc(inv_sin):
    """Convert inverse sine parameters to reflection coefficients.

    :param inv_sin: inverse sine parameters
    :return: reflection coefficients
    
    .. seealso::  :func:`rc2is`, :func:`poly2rc`, :func:`ac2rc`, :func:`lar2rc`.

    :Reference: J.R. Deller, J.G. Proakis, J.H.L. Hansen, "Discrete-Time Processing of Speech Signals", Prentice Hall, Section 7.4.5.

    """
    return numpy.sin(numpy.array(inv_sin)*numpy.pi/2);



def  rc2is(k):
    """Convert reflection coefficients to inverse sine parameters.

    :param k: reflection coefficients
    :return: inverse sine parameters

    .. seealso:: :func:`is2rc`, :func:`rc2poly`, :func:`rc2acC`, :func:`rc2lar`.

    Reference: J.R. Deller, J.G. Proakis, J.H.L. Hansen, "Discrete-Time 
       Processing of Speech Signals", Prentice Hall, Section 7.4.5.

    """
    assert numpy.isrealobj(k), 'Inverse sine parameters not defined for complex reflection coefficients.'
    if max(numpy.abs(k)) >= 1:
        raise ValueError('All reflection coefficients should have magnitude less than unity.')

    return (2/numpy.pi)*numpy.arcsin(k)

def rc2lar(k):
    """Convert reflection coefficients to log area ratios.

    :param k: reflection coefficients
    :return: inverse sine parameters

    The log area ratio is defined by G = log((1+k)/(1-k)) , where the K is the reflection coefficient.

    .. seealso:: :func:`lar2rc`, :func:`rc2poly`, :func:`rc2ac`, :func:`rc2ic`.

    :References:
       [1] J. Makhoul, "Linear Prediction: A Tutorial Review," Proc. IEEE, Vol.63, No.4, pp.561-580, Apr 1975.

    """
    assert numpy.isrealobj(k), 'Log area ratios not defined for complex reflection coefficients.'
    if max(numpy.abs(k)) >= 1:
        raise ValueError('All reflection coefficients should have magnitude less than unity.')

    # Use the relation, atanh(x) = (1/2)*log((1+k)/(1-k))
    return -2 * numpy.arctanh(-numpy.array(k))



def lar2rc(g):
    """Convert log area ratios to reflection coefficients.

    :param g:  log area ratios
    :returns: the reflection coefficients

    .. seealso: :func:`rc2lar`, :func:`poly2rc`, :func:`ac2rc`, :func:`is2rc`.

    :References:
       [1] J. Makhoul, "Linear Prediction: A Tutorial Review," Proc. IEEE,  Vol.63, No.4, pp.561-580, Apr 1975.

    """
    assert numpy.isrealobj(g), 'Log area ratios not defined for complex reflection coefficients.'
    # Use the relation, tanh(x) = (1-exp(2x))/(1+exp(2x))
    return -numpy.tanh(-numpy.array(g)/2)



def lsf2poly():
    raise NotImplementedError

def poly2lsf():
    raise NotImplementedError
def schurrc():
    raise NotImplementedError
