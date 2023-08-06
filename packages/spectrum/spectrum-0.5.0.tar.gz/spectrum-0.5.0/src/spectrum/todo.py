def xcov():
    raise NotImplementedError
def cov2cor():
    raise NotImplementedError

def pmtm():
    raise NotImplementedError
def pwelch():
    raise NotImplementedError
def spectrogram():
    raise NotImplementedError
def tfestimate():
    raise NotImplementedError
def mscohere():
    raise NotImplementedError
def cpsd():
    raise NotImplementedError

def invfreqs():
    raise NotImplementedError
def invfreqz():
    raise NotImplementedError
def prony():
    raise NotImplementedError
def stmcb():
    raise NotImplementedError

""" 
invfreqs    Identify continuous-time filter parameters from frequency response data
invfreqz    Identify discrete-time filter parameters from frequency response data
prony   Prony method for filter design
stmcb   Compute linear model using Steiglitz-McBride iteration
downsample  Decrease sampling rate by integer factor
interp  Interpolation - increase sampling rate by integer factor
resample    Change sampling rate by rational factor
upfirdn Upsample, apply FIR filter, and downsample
upsample    Increase sampling rate by integer factor

Waveform Generation
diric   Dirichlet or periodic sinc function
gauspuls    Gaussian-modulated sinusoidal pulse
gmonopuls   Gaussian monopulse
pulstran    Pulse train
rectpuls    Sampled aperiodic rectangle
sawtooth    Sawtooth or triangle wave
sinc    Sinc
tripuls Sampled aperiodic triangle
vco Voltage controlled oscillator

Specialized Operations
buffer  Buffer signal vector into matrix of data frames
cell2sos    Convert second-order sections cell array to matrix
demod   Demodulation for communications simulation
eqtflength  Equalize lengths of transfer function's numerator and denominator
marcumq Generalized Marcum Q function
modulate    Modulation for communications simulation
seqperiod   Compute period of sequence
sos2cell    Convert second-order sections matrix to cell array
strips  Strip plot
udecode Decode 2n-level quantized integer inputs to floating-point outputs
uencode Quantize and encode floating-point inputs to integer outputs

sptool  Open interactive digital signal processing tool
ss2sos  Convert digital filter state-space parameters to second-order sections form
ss2tf   Convert state-space filter parameters to transfer function form
stepz   Step response of digital filter
stmcb   Compute linear model using Steiglitz-McBride iteration
strips  Strip plot
tf2latc Convert transfer function filter parameters to lattice filter form
tf2sos  Convert digital filter transfer function data to second-order sections form
tf2ss   Convert transfer function filter parameters to state-space form
tfestimate  Transfer function estimate
triang  Triangular window
tripuls Sampled aperiodic triangle
udecode Decode 2n-level quantized integer inputs to floating-point outputs
uencode Quantize and encode floating-point inputs to integer outputs
upfirdn Upsample, apply FIR filter, and downsample
upsample    Increase sampling rate by integer factor
validstructures Structures for specification object with design method
vco Voltage controlled oscillator
wvtool  Open Window Visualization Tool
xcorr2  2-D cross-correlation
xcov    Cross-covariance

zerophase   Zero-phase response of digital filter
zp2sos  Convert zero-pole-gain filter parameters to second-order sections form
zplane  Zero-pole plot
    
"""
def marcumq(a, b, m):
    """Generalized Marcum Q function"""
    raise NotImplementedError
