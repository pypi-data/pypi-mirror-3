from pylab import *
import numpy

#input data is made of lines. Each lines is made of 12 datum representing a month
data = loadtxt('sunspot_monthly_1841_1984.dat')
#data is a mtrix with dimensions made of month times year
data = data.reshape(data.size)

#figure 5.11 of marple chap5, where data is made of monthly sunspot as explained in chap 5.
#1728 monthly sunspot with 24 year segment (288 samples) and overlap of 12 years (144 samples)
#Fs=12 that is 12 months per year
p, f = psd(data, NFFT=288, noverlap=144, window=numpy.hamming(288), Fs=12)
clf()
plot(f, 10*log10(p/max(p)))
title('Welch periodogram N=288, noverlap=144 hamming window')
xlabel('cycles per year')
ylabel('relative PSD (dB)')
grid()
savefig('psd_test.png')

xlim(0,1)
savefig('psd_test_zoom.png')
