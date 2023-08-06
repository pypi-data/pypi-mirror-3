#This script loads the sunspot data (wolfer number versus year)
# we compute the main frequencies contained in the data thanks to 
# a simple periodogram (single fft). Then, we plot the frequency on a
# nyquist scale, and a period scale showing the 11 year main frequency.

from pylab import *
import numpy

#get the data from sunspot
data = numpy.loadtxt('sunspot.dat')
year = data[:,0]
wolfer = data[:,1]

#compute the fft and frequency sampling
Y = fft(wolfer)
n = len(Y)

filename = 'sunspot_versus_year.png'
print 'Creating plot of wolfer number versus time (%s)' % filename
figure(1)
plot(year, wolfer)
xlabel('year')
ylabel('Wolfer number')
savefig(filename)

print 'Compute fft'
#note that we do not take the first element in power
power = abs(Y[1:n/2])**2
pmax = max(power)
nyquist = 0.5
freq = arange(n/2) / (n/2.0) * nyquist
freq = freq + 0.0001
period = 1./freq

print 'plotting fft versus frequency'
#note that we skip the first element in period as we did previously for power variable.
figure(1)
clf()
plot(freq[1:], 10*log10(power/pmax))
grid(True)
xlabel('frequency')
ylabel('|FFT|**2')
title('simple periodogram of sunspot data')
savefig('sunspot_frequency_simple_psd.png')


print 'plotting fft versus period'
#just change x axis from freq to period
figure(2)
plot(period[1:], 10*log10(power/pmax))
grid(True)
xlabel('Period (year)')
ylabel('|FFT|**2')
xlim(0,40)
title('simple periodogram of sunspot data')
savefig('sunspot_period_simple_psd.png')
