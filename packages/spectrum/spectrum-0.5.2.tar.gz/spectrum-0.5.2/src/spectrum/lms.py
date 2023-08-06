import numpy


def LMS (x, U, ar):
    """ LMS sequential adaptive algorithm

    :param X: Complex array of contents of input data shift register
    :param U: Real scalar representing the adaptive step size

    :return:
        * A  - Complex array of AR parameters (adaptive weights)

    .. note::
        *  External array X must be dimensioned >= IP+1
        * array A must be dimensioned >= IP

    .. todo:: test, validation, examples
    """
    IP = len(ar)
    newar = numpy.zeros(IP)

    for i in range(0, IP):
        newar[i] = ar[i]

    ef = x[0]
    for k in range(0, IP):
        ef = ef + ar[k] * x[k+1]           #! Eq. (9.3)

    for k in range(0, IP):
        newar[k] = newar[k]-2.*U* ef * x[k+1]    #! Eq. (9.8)


    return newar
