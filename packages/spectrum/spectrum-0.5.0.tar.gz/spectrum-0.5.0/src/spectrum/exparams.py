import numpy
from math import atan2, log
from numpy import abs 

def EXPARAMS(IP,T, H, Z):
    """C
   Routine that produces the real amplitude, damping, frequency, and
   phase from the complex amplitude and exponential parameter arrays.

   Input Parameters:

     IP    - Order of exponential model (integer)
     T     - Real variable representing the sample interval (sec.)
     H     - Array of complex amplitude parameters, H(1) to H(IP)
     Z     - Array of complex exponential parameters, Z(1) to Z(IP)

   Output Parameters:

     AMP   - Array of real amplitudes (arbitrary units)
     DAMP  - Array of real damping factors (1/sec)
     FREQ  - Array of real frequencies (Hz)
     PHASE - Array of real phase (radians)

   Notes:

     External arrays H,Z,AMP,DAMP,FREQ,PHASE must be dimensioned
     .GE. IP in the calling program.    If the original data was
     data was real, the phase reported represents that of a
     cosine waveform.


    .. todo:: test and validation 
    """

    FREQ = numpy.zeros(IP)
    AMP = numpy.zeros(IP)
    DAMP = numpy.zeros(IP)
    PHASE = numpy.zeros(IP)

    twopi = 2. * numpy.pi

    for K in range(0, IP):
        FREQ[K]  = atan2(Z[K].imag,Z[K].real)/(twopi*T)
        DAMP[K]  = log(abs(Z[K])) / T
        AMP[K]   = abs(H[K])
        PHASE[K] = atan2( H[K].imag, H[K].real)

    return AMP, DAMP, FREQ, PHASE    
