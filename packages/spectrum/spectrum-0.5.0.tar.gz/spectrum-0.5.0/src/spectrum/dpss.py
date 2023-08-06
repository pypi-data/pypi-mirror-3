import numpy as np
import ctypes as C
import platform
import os



# Import shared mtspec library depending on the platform.
if platform.system() == 'Windows':
    lib_name = 'mtspec.pyd'
elif platform.system() == 'Darwin':
    lib_name = 'mtspec.so'
else:
    lib_name = 'mtspec.so'

# Initialize library
mtspeclib = C.CDLL(os.path.join(os.path.dirname(__file__), '',
                                lib_name))



class _MtspecType(object):
    """
    Simple class that stores type definition for interfacing with
    the fortran code and provides some helper functions.
    """
    struct = {"float32": (C.c_float, mtspeclib.mtspec_pad_),
              "float64": (C.c_double, mtspeclib.mtspec_d_)}

    def __init__(self, dtype):
        """
        Depending on dtype initialize different type structures.

        :param dtype: 'float32' or 'float64'
        """
        if dtype not in self.struct.keys():
            raise ValueError("dtype must be either 'float32' or 'float64'")
        self.float = dtype
        self.complex = 'complex%d' % (2 * float(dtype[-2:]))
        self.c_float = self.struct[dtype][0]
        self.pointer = C.POINTER(self.c_float)
        self.required = ['F_CONTIGUOUS', 'ALIGNED', 'WRITEABLE']
        self.mtspec = self.struct[dtype][1]

    def empty(self, shape, complex=False):
        """
        A wrapper around np.empty which automatically sets the correct type
        and returns an empty array.

        :param shape: The shape of the array in np.empty format
        """
        if complex:
            return np.empty(shape, self.complex, self.required)
        return np.empty(shape, self.float, self.required)

    def p(self, ndarray):
        """
        A wrapper around ctypes.data_as which automatically sets the
        correct type. Returns none if ndarray is None.

        :param ndarray: numpy input array or None
        """
        # short variable name for passing as argument in function calls
        if ndarray is None:
            return None
        return ndarray.ctypes.data_as(self.pointer)



def dpss(N, bw, nev, nmax=None):
    """Discrete prolate spheroidal (Slepian) sequences

    Calculation of the Discrete Prolate Spheroidal Sequences also knows as the
    slepian sequences, and the correspondent eigenvalues. 

    :param int N: window length
    :param float bw: the time-bandwidth product 
    :param nev: the desired number of tapers
    :return: (v, lamb, theta) with v(N,nev) the eigenvectors (tapers)
        lamb the eigenvalues of the v's and theta the 1-lambda (energy
        outside the bandwidth) values.

    .. plot::
        :width: 80%
        :include-source:

        from spectrum import *
        from pylab import *
        N = 1024
        [w, l, theta] = dpss(N, 2.5, 4)
        plot(w)
        title('Slepian Sequences N=%s, NW=2.5' % N)
        axis([0, N, -0.15, 0.15])
        legend(['1st','2nd','3rd','4th'])

    :references: [Percival]
    """
    mt = _MtspecType("float64")
    v = mt.empty((N, nev))
    lamb = mt.empty(nev)
    theta = mt.empty(nev)

    mtspeclib.dpss_(C.byref(C.c_int(N)), C.byref(C.c_double(bw)),
                    C.byref(C.c_int(nev)), mt.p(v), mt.p(lamb),
                    mt.p(theta))

    return (v, lamb, theta)

def _tridib( n, eps1, d, e, e2, lb, ub, m11):
    """In progress
    
    :param int n:the order of the matrix.
    :param float eps1:  On input, an absolute error tolerance for 
        the computed eigenvalues.  
    :param float d: the diagonal elements of the input matrix.
    :param float e: the subdiagonal elements of the input matrix in E(2:N).
        E(1) is arbitrary.
    :param float e2: the squares of the corresponding elements of E.  
        E2(1) is arbitrary.  On output, elements of E2 
        corresponding to elements of E regarded as negligible, have been 
        replaced by zero, causing the matrix to split into a direct sum of 
        submatrices.  E2(1) is also set to zero.
    :param int m11: the lower boundary index for the desired eigenvalues.
    :param int m: the number of eigenvalues desired.  The upper
        boundary index M22 is then obtained as M22 = M11 + M - 1.

    :return:
        * LB, UB, define an interval containing exactly the desired eigenvalues.
        * real W(M), the eigenvalues between indices M11 and M22 in ascending order.
        * IND(M), the submatrix indices associated with the 
            corresponding eigenvalues in W: 1 for eigenvalues belonging to the 
            first submatrix from the top, 2 for those belonging to the second 
           submatrix, and so on.
    """
    
    #m = mt.empty((npts, nev))
    #w = mt.empty(nev)
    #ind = mt.empty(nev)
    #ierr = mt.empty(1) #one value
 
    #mtspeclib.tridib_(C.byref(C.c_int(n)),
    #                  C.byref(C.c_float(eps1))
    #                  
    #                  )
    pass


def _dpsscalc(N,NW,k=None):
    """Calculate slepian sequences.


    :param  n: number of points in data stream
    :param nw: number of output windows 
    :param  k: slepian order, optional. if not provided 2*NW - 1

    [E,V] = dpsscalc(N,NW,k) uses tridieig() to get eigenvalues 1:k if k is 
    a scalar, and k(1):k(2) if k is a matrix, of the sparse tridiagonal matrix.
    It then uses inverse iteration using the exact eigenvalues on a starting 
    vector with approximate shape, to get the eigenvectors required.  It then 
    computes the eigenvalues V of the Toeplitz sinc matrix using a fast 
    autocorrelation technique.

    return E, V
    """
    W = float(NW) / N
    if k == None:
        k = min(round(2*N*W),N)
        k = max(k,1)
    if len(k) == 1:
        k = [1, k]

"""
    # Generate the diagonals
    d = ((N-1.-2*arange(0,N))**2)*.25*cos(2*pi*W)  # diagonal of B
    ee=arange(1,N-1)'.*(N-1:-1:1)'/2;               # super diagonal of B


    #scipy.linalg.eigvals_banded(
    # Get the eigenvalues of B.
    v = tridieig(d,[0; ee],N-k(2)+1,N-k(1)+1);
    v = v(end:-1:1);
    Lv = length(v);

    #%B = spdiags([[ee;0] d [0;ee]],[-1 0 1],N,N);
    #%I = speye(N,N);

    #% Compute the eigenvectors by inverse iteration with
    #% starting vectors of roughly the right shape.
    E = zeros(N,k(2)-k(1)+1);
    t = (0:N-1)'/(N-1)*pi;

    for j = 1:Lv
       e = sin((j+k(1)-1)*t);
       e = tridisolve(ee,d-v(j),e,N);
       e = tridisolve(ee,d-v(j),e/norm(e),N);
       e = tridisolve(ee,d-v(j),e/norm(e),N);
       E(:,j) = e/norm(e);
    

    d=mean(E);
    for i=k(1):k(2):
       if rem(i,2):#  % i is odd
         #% Polarize symmetric dpss
           if d(i-k(1)+1)<0, E(:,i-k(1)+1)=-E(:,i-k(1)+1);
       else:#         % i is even
         #% Polarize anti-symmetric dpss
           if E(2,i-k(1)+1)<0, E(:,i-k(1)+1)=-E(:,i-k(1)+1); 

    #% get eigenvalues of sinc matrix
    #%  Reference: [1] Percival & Walden, Exercise 8.1, p.390
    s = [2*W; 4*W*sinc(2*W*(1:N-1)')];
    q = zeros(size(E));
    blksz = Lv;  % <-- set this to some small number if OUT OF MEMORY!!!
    for i=1:blksz:Lv
        blkind = i:min(i+blksz-1,Lv);
        q(:,blkind) = fftfilt(E(N:-1:1,blkind),E(:,blkind));
    end
    V = q'*flipud(s);

    % return 1 for any eigenvalues greater than 1 due to finite precision errors
    V = min(V,1);
    % return 0 for any eigenvalues less than 0 due to finite precision errors
    V = max(V,0);
"""


"""
 ww=(double)nw/(double)n;
  cs=cos(VIR_2PI*ww);
  /* diagonal element of tridiagonal matrix*/
  for (int  i = 0; i < n; i++)
    d[i] = -cs*((((double)n-1.)/2.-(double)i))*((((double)n-1.)/2.-(double)i));
  for (int  i = 0; i < n; i++)
    {
      e[i] = -(double)i * ((double)n - (double)i) / 2.;
      e2[i] = e[i] * e[i];
    }
  jtridib_(&n,&eps,d,e,e2,&lb,&ub,&m11,&nwin,eigen,ip,&ierr,temp1,temp2);
  jtinvit_(&n, &n, d, e, e2, &nwin, eigen, ip, evecs, &ierr, temp1,temp2,temp3,temp4,temp5);
  /*calculate lambda*/
  dfac = (double) n *VIR_PI * ww;
  drat = (double) 8. *dfac;
  dfac = (double) 4. *sqrt(VIR_PI * dfac) * exp((double) (-2.0) * dfac);
    for (int k = 0; k < nwin; k++) {
    eigen[k] = (double) 1.0 - (double) dfac;
    dfac = dfac * drat / (double) (k + 1);
    /* fails as k -> 2n */
  }
  gamma = log((double) 8. * n * sin((double) 2. * VIR_PI * ww)) + VIR_GAMMA;
  for (int k = 0; k < nwin; k++) {
    bh = -2. * VIR_PI * (n * ww - (double) (k) /
              (double) 2. - (double) .25) / gamma;
    ell[k] = (double) 1. / ((double) 1. + exp(VIR_PI * (double) bh));
  }
  for (int i = 0; i < nwin; i++)
    eigen[i] = max(ell[i], eigen[i]);
  /* normalize */
  int kk;  
  double tapsq,aa;
  for (int k = 0; k < nwin; k++) {
    kk = k * n;
    tapsum[k] = 0.;
    tapsq = 0.;
    for (int i = 0; i < n; i++) {
      aa = evecs[i + kk];
      tapers[i + kk] = aa;
      tapsum[k] = tapsum[k] + aa;
      tapsq = tapsq + aa * aa;
    }
    aa = sqrt(tapsq / (double) n);
    tapsum[k] = tapsum[k] / aa;
    for (int i = 0; i < n; i++) {
      tapers[i + kk] = tapers[i + kk] / aa;
    }
"""





"""%---------------------------------------------------------------------
function [En,V] = dpssint(N, NW, M, int, E,V)
% Syntax: [En,V]=dpssint(N,NW); [En,V]=dpssint(N,NW,M,'spline');
%  Dpssint calculates discrete prolate spheroidal
%  sequences for the parameters N and NW. Note that
%  NW is normally 2, 5/2, 3, 7/2, or 4 - not i/N. The 
%  dpss are interpolated from previously calculated 
%  dpss of order M (128, 256, 512, or 1024). 256 is the 
%  default for M. The interpolation can be 'linear' 
%  or 'spline'. 'Linear' is faster, 'spline' the default.
%  Linear interpolation can only be used for M>N. 
%  Returns:
%              E: matrix of dpss (N by 2NW)
%              V: eigenvalue vector (2NW)
% 
% Errors in the interpolated dpss are very small but should be 
% checked if possible. The differences between interpolated
% values and values from dpsscalc are generally of order
% 10ee-5 or better. Spline interpolation is generally more
% accurate. Fractional errors can be very large near
% the zero-crossings but this does not seriously affect
% windowing calculations. The error can be reduced by using
% values for M which are close to N.
%
% Written by Eric Breitenberger, version date 10/3/95.
% Please send comments and suggestions to eric@gi.alaska.edu
%

W = NW/N;

if     nargin==2,
  M=256; int='spline';
elseif nargin==3,
  if isstr(M), int=M; M=256; 
  else, int='spline';, end
end

if int=='linear' & N>M
  error('Linear interpolation cannot be used for N>Ni. Use splining instead.')
end

if nargin<=4
    [E,V] = dpssload(M,NW);
else
    if size(E,1)~=M
        error('Ni and row size of E don''t match.')
    end
end

k=min(round(2*NW),N); % Return only first k values
k = max(k,1);
E=E(:,1:k);
V=V(1:k);
x=1:M;

% The scaling for the interpolation:
% This is not necessarily optimal, and 
% changing s can improve accuracy.
 
s=M/N;
midm=(M+1)/2;
midn=(N+1)/2;
delta=midm-s*midn;
xi=linspace(1-delta, M+delta, N);

% Interpolate from M values to N
% Spline interpolation is a bit better,
% but takes about twice as long.
% Errors from linear interpolation are 
% usually smaller than errors from scaling.

En=interp1(x,E,xi,['*' int]);

% Re-normalize the eigenvectors
En=En./(ones(N,1)*sqrt(sum(En.*En)));

"""



def DPSS_windows(N, NW, Kmax):
    """Returns the Discrete Prolate Spheroidal Sequences of orders [0,Kmax-1]
    for a given frequency-spacing multiple NW and sequence length N. 

    Paramters

    N : int
        sequence length
    NW : float, unitless
        standardized half bandwidth corresponding to 2NW = BW*f0 = BW*N/dt
        but with dt taken as 1
    Kmax : int
        number of DPSS windows to return is Kmax (orders 0 through Kmax-1)

    Returns

    v,e : tuple,
        v is an array of DPSS windows shaped (Kmax, N)
        e are the eigenvalues 

    Notes

    Tridiagonal form of DPSS calculation from:

    Slepian, D. Prolate spheroidal wave functions, Fourier analysis, and
    uncertainty V: The discrete case. Bell System Technical Journal,
    Volume 57 (1978), 1371430
    """
    # here we want to set up an optimization problem to find a sequence
    # whose energy is maximally concentrated within band [-W,W].
    # Thus, the measure lambda(T,W) is the ratio between the energy within
    # that band, and the total energy. This leads to the eigen-system
    # (A - (l1)I)v = 0, where the eigenvector corresponding to the largest
    # eigenvalue is the sequence with maximally concentrated energy. The
    # collection of eigenvectors of this system are called Slepian sequences,
    # or discrete prolate spheroidal sequences (DPSS). Only the first K,
    # K = 2NW/dt orders of DPSS will exhibit good spectral concentration
    # [see http://en.wikipedia.org/wiki/Spectral_concentration_problem]
    
    # Here I set up an alternative symmetric tri-diagonal eigenvalue problem
    # such that
    # (B - (l2)I)v = 0, and v are our DPSS (but eigenvalues l2 != l1)
    # the main diagonal = ([N-1-2*t]/2)**2 cos(2PIW), t=[0,1,2,...,N-1]
    # and the first off-diangonal = t(N-t)/2, t=[1,2,...,N-1]
    # [see Percival and Walden, 1993]
    from scipy import linalg as la
    Kmax = int(Kmax)
    W = float(NW)/N
    ab = np.zeros((2,N), 'd')
    nidx = np.arange(N)
    ab[0,1:] = nidx[1:]*(N-nidx[1:])/2.
    ab[1] = ((N-1-2*nidx)/2.)**2 * np.cos(2*np.pi*W)
    # only calculate the highest Kmax-1 eigenvectors
    l,v = la.eig_banded(ab, select='i', select_range=(N-Kmax, N-1))
    dpss = v.transpose()[::-1]

    # By convention (Percival and Walden, 1993 pg 379)
    # * symmetric tapers (k=0,2,4,...) should have a positive average.
    # * antisymmetric tapers should begin with a positive lobe
    fix_symmetric = (dpss[0::2].sum(axis=1) < 0)
    for i, f in enumerate(fix_symmetric):
        if f:
            dpss[2*i] *= -1
    fix_skew = (dpss[1::2,1] < 0)
    for i, f in enumerate(fix_skew):
        if f:
            dpss[2*i+1] *= -1

    # Now find the eigenvalues of the original 
    # Use the autocovariance sequence technique from Percival and Walden, 1993
    # pg 390
    # XXX : why debias false? it's all messed up o.w., even with means
    # on the order of 1e-2
    acvs = autocov(dpss, debias=False) * N
    r = 4*W*np.sinc(2*W*nidx)
    r[0] = 2*W
    eigvals = np.dot(acvs, r)
    
    return dpss, eigvals


def autocov(s, **kwargs):
    """Returns the autocovariance of signal s at all lags.

    Notes

    
    Adheres to the definition
    sxx[k] = E{S[n]S[n+k]} = cov{S[n],S[n+k]}
    where E{} is the expectation operator, and S is a zero mean process
    """
    # only remove the mean once, if needed
    debias = kwargs.pop('debias', True)
    axis = kwargs.get('axis', -1)
    if debias:
        s = remove_bias(s, axis)
    kwargs['debias'] = False
    return crosscov(s, s, **kwargs)


def autocov2(s, **kwargs):
    """Returns the autocovariance of signal s at all lags.

    Notes

    
    Adheres to the definition
    sxx[k] = E{S[n]S[n+k]} = cov{S[n],S[n+k]}
    where E{} is the expectation operator, and S is a zero mean process
    """
    # only remove the mean once, if needed
    debias = kwargs.pop('debias', True)
    axis = kwargs.get('axis', -1)
    if debias:
        s = remove_bias(s, axis)
    kwargs['debias'] = False
    return crosscov(s, s, **kwargs)

def crosscov(x, y, axis=-1, all_lags=False, debias=True):
    """Returns the crosscovariance sequence between two ndarrays.
    This is performed by calling fftconvolve on x, y[::-1]

    Parameters


    x: ndarray
    y: ndarray
    axis: time axis
    all_lags: {True/False}
       whether to return all nonzero lags, or to clip the length of s_xy
       to be the length of x and y. If False, then the zero lag covariance
       is at index 0. Otherwise, it is found at (len(x) + len(y) - 1)/2
    debias: {True/False}
       Always removes an estimate of the mean along the axis, unless
       told not to.

    Notes


    cross covariance is defined as
    sxy[k] := E{X[t]*Y[t+k]}, where X,Y are zero mean random processes
    """
    if x.shape[axis] != y.shape[axis]:
        raise ValueError(
            'crosscov() only works on same-length sequences for now'
            )
    if debias:
        x = remove_bias(x, axis)
        y = remove_bias(y, axis)
    slicing = [slice(d) for d in x.shape]
    slicing[axis] = slice(None,None,-1)
    sxy = fftconvolve(x, y[tuple(slicing)], axis=axis, mode='full')
    N = x.shape[axis]
    sxy /= N
    if all_lags:
        return sxy
    slicing[axis] = slice(N-1,2*N-1)
    return sxy[tuple(slicing)]
    
def crosscorr(x, y, **kwargs):
    """
    Returns the crosscorrelation sequence between two ndarrays.
    This is performed by calling fftconvolve on x, y[::-1]

    Parameters


    x: ndarray
    y: ndarray
    axis: time axis
    all_lags: {True/False}
       whether to return all nonzero lags, or to clip the length of r_xy
       to be the length of x and y. If False, then the zero lag correlation
       is at index 0. Otherwise, it is found at (len(x) + len(y) - 1)/2

    Notes


    cross correlation is defined as
    rxy[k] := E{X[t]*Y[t+k]}/(E{X*X}E{Y*Y})**.5,
    where X,Y are zero mean random processes. It is the noramlized cross
    covariance.
    """
    sxy = crosscov(x, y, **kwargs)
    # estimate sigma_x, sigma_y to normalize
    sx = np.std(x)
    sy = np.std(y)
    return sxy/(sx*sy)

def remove_bias(x, axis):
    "Subtracts an estimate of the mean from signal x at axis"
    padded_slice = [slice(d) for d in x.shape]
    padded_slice[axis] = np.newaxis
    mn = np.mean(x, axis=axis)
    return x - mn[tuple(padded_slice)]

def fftconvolve(in1, in2, mode="full", axis=None):
    """ Convolve two N-dimensional arrays using FFT. See convolve.

    This is a fix of scipy.signal.fftconvolve, adding an axis argument and
    importing locally the stuff only needed for this function
    
    """
    #Locally import stuff only required for this:
    from scipy.fftpack import fftn, fft, ifftn, ifft
    from scipy.signal.signaltools import _centered
    from numpy import array, product


    s1 = array(in1.shape)
    s2 = array(in2.shape)
    complex_result = (np.issubdtype(in1.dtype, np.complex) or
                      np.issubdtype(in2.dtype, np.complex))

    if axis is None:
        size = s1+s2-1
        fslice = tuple([slice(0, int(sz)) for sz in size])
    else:
        equal_shapes = s1==s2
        # allow equal_shapes[axis] to be False
        equal_shapes[axis] = True
        assert equal_shapes.all(), 'Shape mismatch on non-convolving axes'
        size = s1[axis]+s2[axis]-1
        fslice = [slice(l) for l in s1]
        fslice[axis] = slice(0, int(size))
        fslice = tuple(fslice)

    # Always use 2**n-sized FFT
    fsize = 2**np.ceil(np.log2(size))
    if axis is None:
        IN1 = fftn(in1,fsize)
        IN1 *= fftn(in2,fsize)
        ret = ifftn(IN1)[fslice].copy()
    else:
        IN1 = fft(in1,fsize,axis=axis)
        IN1 *= fft(in2,fsize,axis=axis)
        ret = ifft(IN1,axis=axis)[fslice].copy()
    if not complex_result:
        del IN1
        ret = ret.real
    if mode == "full":
        return ret
    elif mode == "same":
        if product(s1,axis=0) > product(s2,axis=0):
            osize = s1
        else:
            osize = s2
        return _centered(ret,osize)
    elif mode == "valid":
        return _centered(ret,abs(s2-s1)+1)
