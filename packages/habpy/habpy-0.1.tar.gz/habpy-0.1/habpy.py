#!/usr/bin/python

#Copyright (C) 2011-2012
#Author: Mehmet BERKIL
#Author communication address: b.mehmet.89@gmail.com
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY. See the
# GNU General Public License for more details.
#
# 

import numpy
import scipy
import scipy.signal as sgnl
import scipy.fftpack as fpck

def chelp(funame):
	"""
chelp(function_name) -> function definition

Prints the definition of the function given in the parameter.

	Example:

	chelp(digisec)

	Output:

digisec(length) -> value

Returns a random digital array. "length" is the length of the array and must be integer and greater than 2.

	Usage:

	number=10
	x=digisec(number)

	or

	x=digisec(10)
	
	Output:
	
	array([1, 0, 1, 1, 0, 1, 1, 0, 0, 0])
	"""
	
	print funame.__doc__



def digisec(length):
	"""
digisec(length) -> value

Returns a random digital array. "length" is the length of the array and must be integer and greater than 2.

	Usage:

	number=10
	x=digisec(number)

	or

	x=digisec(10)
	
	Output:
	
	array([1, 0, 1, 1, 0, 1, 1, 0, 0, 0])
	"""
	x = []
	x = numpy.random.randint(2,size=length)
	y = numpy.asarray(x)
	return y

	

def wgn(m,p,power_type,imp=1):
	"""
wgn(m,p,power_type,imp) -> generate white gaussian noise

This function generates white gaussian noise. M is the length of the noie array and must be greater than 1,
p is the power of the noise, power_type specifies the units of p and can be "dbw", "dbm" or "linear".
Linear power is in watts. Imp specifies the load impedance in ohms and default value is 1.
	
	Usage:
	
	to generate a 1024-lengthed array with power of 5 dbm across a 50 ohm load:
	y = wgn(1024,5,"dbm",50)

	to generate a 512-lengthed array with power of 2 dbw:
	y = wgn(512,2,"bdw")
	(default impedance value is 1 ohm)

	to generate a 10-lengthed array with power of 3 watts across a 75 ohm load:
	y = wgn(10,3,"linear",75)
	"""

	row = numpy.size(m)

	if power_type=="linear":
		noisepower = p

	if power_type=="dbw":
		noisepower = 10**((p*1.0)/10)
	
	if power_type=="dbm":
		noisepower = 10**(((p-30)*1.0)/10)

	y = (numpy.sqrt(imp*(noisepower*1.0)))*numpy.random.randn(m)

	return y



def awgn_(x,power_type):
	"""
awgn_(x,power_type) -> generate white gaussian noise

This function generates white gaussian noise. X is the signal that will be added gaussian noise,
power_type specifies the units of p and can be "dbw", "dbm" or "linear".
Linear power is in watts.

Function generates a white noise (which has the same length as x) with power of 1 across a 1 ohm load
and packs them together.

	Usage:
	
	to generate noisy signal with power of dbm, dbw or linear:
	y = awgn_(x,"dbm")
	y = awgn_(x,"dbw")
	y = awgn_(x,"linear")
	"""

	m = numpy.size(x)
	row = numpy.size(m)
	p = 1
	imp = 1

	if power_type=="linear":
		noisepower = p

	if power_type=="dbw":
		noisepower = 10**((p*1.0)/10)
	
	if power_type=="dbm":
		noisepower = 10**(((p-30)*1.0)/10)

	y = (numpy.sqrt(imp*(noisepower*1.0)))*numpy.random.randn(m)

	z = x+y

	return z



def ammod(x,fc,fs):
	"""
ammod(x,fc,fs) -> amplitude modulated signal

Returns the amplitude modulated signal wave. X is the signal, will be modulated ,fc is the carrier
frequency (Hz) and fs is the sampling frequency (Hz). Fs must satisfy fs> 2*(fc+bw), where bw is the bandwith
of the message signal x.

	Usage:

	t=arange(0,end_value,step_value)

	x=sin(2*pi*t)
	fc=some variable
	fs=some variable

	y=ammod(x,fc,fs)
	"""

	l = numpy.size(x)
	step_v=1.0/fs
	end_v=(l*1.0)/fs
	t=numpy.arange(0,end_v,step_v)
	mod1 = x*numpy.cos(2*(numpy.pi)*fc*t)
	modd = mod1.copy()
	return modd



def amdemod(s,fc,fs):
	"""
amdemod(s,fc,fs) -> amplitude demodulated signal

Returns the amplitude demodulated signal wave. S is the amplitude modulated signal, fc is the carrier
frequency (Hz) and fs is the sampling frequency (Hz). Fs must satisfy fs> 2*(fc+bw), where bw is the bandwidth of the s.
	
	Usage:

	Assume that we have modulated signal s
	
	fc=carrier frequency, used in modulation
	fs=sampling frequency, used in modulation

	y=amdemod(s,fc,fs)
	"""
	modd = numpy.array([])
	demodd = numpy.array([])
	o_filter = numpy.array([])
	l = numpy.size(s)
	step_v=1.0/fs
	end_v=((l)*1.0)/fs
	fc2 = fc*2.0/fs
	t = numpy.arange(0,end_v,step_v)
	modd = s*numpy.cos(2*(numpy.pi)*fc*t)
	o_filter = sgnl.butter(5, fc2)
	demodd = sgnl.filtfilt(o_filter[0], o_filter[1], modd)*2
	return demodd
	


def fmmod(x,fc,fs,freqdev):
	"""
fmmod(x,fc,fs,freqdev) -> frequency modulated signal

Returns the frequency modulated signal wave. X is the signal, will be modulated, fc is the carrier
frequency (Hz), fs is the sampling frequency (Hz) and freqdev is the frequency deviation and must be
a positive integer. Fs must satisfy fs> 2*(fc+bw), where bw is the bandwith of the message signal x.

	Usage:

	t=arange(0,end_value,step_value)

	x=sin(2*pi*t)
	fc=some variable
	fs=some variable

	freqdev = 25

	y=fmmod(x,fc,fs,freqdev)
	"""
	l = numpy.size(x)
	step_v=1.0/fs
	end_v=(l*1.0)/fs
	t=numpy.arange(0,end_v,step_v)
	
	int_x = numpy.cumsum(x)*1.0/fs
	y = numpy.cos(2*numpy.pi*fc*t+2*numpy.pi*freqdev*int_x)
	
	return y



def fmdemod(s,fc,fs,freqdev):
	"""
fmdemod(s,fc,fs,freqdev) -> frequency demodulated signal

Returns the frequency demodulated signal wave. S is the frequency modulated signal, fc is the carrier
frequency (Hz), fs is the sampling frequency (Hz) and freqdev is the frequency deviation and must be
a positive integer. Fs must satisfy fs> 2*(fc+bw), where bw is the bandwith of the message signal x.

	Usage:

	Assume that we have modulated signal s
	
	fc=carrier frequency, used in modulation
	fs=sampling frequency, used in modulation

	freqdev = frequency deviation, used in modulation

	y=fmdemod(s,fc,fs,freqdev)
	"""
	
	ds = numpy.diff(s)

	l = numpy.size(ds)
	step_v=1.0/fs
	end_v=(l*1.0)/fs
	t=numpy.arange(0,end_v,step_v)

	modd = numpy.array([])
	demodd = numpy.array([])
	o_filter = numpy.array([])

	
	fc2 = fc*2.0/fs
	
	modd = ds*numpy.cos(2*(numpy.pi)*fc*t)
	o_filter = sgnl.butter(5, fc2)
	demodd = sgnl.filtfilt(o_filter[0], o_filter[1], modd)*2
	return demodd



def pmmod(x,fc,fs,phasedev):
	"""
pmmod(x,fc,fs,phasedev) -> phase modulated signal

Returns the pahse modulated signal wave. X is the signal, will be modulated, fc is the carrier
frequency (Hz), fs is the sampling frequency (Hz) and phasedev is the phase deviation and must be
in radians. Fs must satisfy fs> 2*(fc+bw), where bw is the bandwith of the message signal x.

	Usage:

	t=arange(0,end_value,step_value)

	x=sin(2*pi*t)
	fc=some variable
	fs=some variable

	phasedev = pi/2

	y=fmmod(x,fc,fs,phasedev)
	"""
	
	l = numpy.size(x)
	step_v=1.0/fs
	end_v=(l*1.0)/fs
	t=numpy.arange(0,end_v,step_v)

	y = numpy.cos(2*numpy.pi*fc*t+phasedev*x)

	return y



def pmdemod(s,fc,fs,phasedev):
	"""
pmdemod(s,fc,fs,phasedev) -> phase demodulated signal

Returns the phase demodulated signal wave. S is the phase modulated signal, fc is the carrier
frequency (Hz), fs is the sampling frequency (Hz) and phasedev is the phase deviation and must be
in radian. Fs must satisfy fs> 2*(fc+bw), where bw is the bandwith of the message signal x.

	Usage:

	Assume that we have modulated signal s
	
	fc=carrier frequency, is used in modulation
	fs=sampling frequency, is used in modulation

	phasedev = phase deviation, is used in modulation

	y=pmdemod(s,fc,fs,freqdev)
	"""

	l = numpy.size(s)
	step_v=1.0/fs
	end_v=(l*1.0)/fs
	t=numpy.arange(0,end_v,step_v)

	#ya = fpck.hilbert(s)*numpy.exp(complex(0,-1)*2*numpy.pi*fc*t-j*2*numpy.pi)
	#ya = fpck.hilbert(s)*numpy.exp(complex(0,-1)*2*numpy.pi*fc*t-complex(0,1)*2*numpy.pi)
	
	ya = fpck.hilbert(s)*numpy.exp(complex(0,-1)*2*numpy.pi*fc*t)	

	#demod = (1.0/phasedev)*numpy.angle(ya)
	#carpa belki tum elemanlar carpilazm cunki malabde * ile carpmis nokta degil
	demod = (1.0/phasedev)*numpy.angle(ya)
	#demod = numpy.multiply((1.0/phasedev),numpy.angle(ya))
	return demod



def ssbmod(x,fc,fs,btype):
	"""
ssbmod(x,fc,fs,btype) -> single sideband amplitude modulated signal

Returns the amplitude modulated signal wave. X is the signal, will be modulated ,fc is the carrier
frequency (Hz) and fs is the sampling frequency (Hz). Fs must satisfy fs> 2*(fc+bw), where bw is the bandwith
of the message signal x. Btype is the band type and "up" or "ups" uses upper sideband, "lower" or "lsb" uses lower sideand.

	Usage:

	t=arange(0,end_value,step_value)

	x=sin(2*pi*t)
	fc=some variable
	fs=some variable

	for upper sideband:

	y=ssbmod(x,fc,fs,"up")
	or
	y=ssbmod(x,fc,fs,"ups")

	for lower sideband:

	y=ssbmod(x,fc,fs,"lower")
	or
	y=ssbmod(x,fc,fs,"lsb")
	"""

	l = numpy.size(x)
	step_v=1.0/fs
	end_v=(l*1.0)/fs

	t=numpy.arange(0,end_v,step_v)

	x_hilbert = fpck.hilbert(x)
	
	#upper band
	if btype=="up" or "ups":
		y = x*numpy.cos(2*numpy.pi*fc*t)-numpy.imag(x_hilbert)*numpy.sin(2*numpy.pi*fc*t)
	
	#lower band
	if btype=="lower" or "lsb":
		y = x*numpy.cos(2*numpy.pi*fc*t)+numpy.imag(x_hilbert)*numpy.sin(2*numpy.pi*fc*t)
	
	return y



def ssbdemod(x,fc,fs):
	"""
ssbdemod(x,fc,fs,btype) -> single sideband amplitude demodulated signal

Returns the single sideband amplitude demodulated signal wave. S is the signal, will be demodulated, 
fc is the carrier frequency (Hz) and fs is the sampling frequency (Hz). Fs must satisfy fs> 2*(fc+bw),
where bw is the bandwith of the message signal x.

	Usage:

	Assume that we have modulated signal s
	
	fc=carrier frequency, used in modulation
	fs=sampling frequency, used in modulation

	y=ssbdemod(s,fc,fs)
	"""

	modd = numpy.array([])
	demodd = numpy.array([])

	o_filter = numpy.array([])

	l = numpy.size(x)
	step_v=1.0/fs
	end_v=((l)*1.0)/fs
	fc2 = fc*2.0/fs

	t = numpy.arange(0,end_v,step_v)

	modd = x*numpy.cos(2*(numpy.pi)*fc*t)

	o_filter = sgnl.butter(5, fc2)
	demodd = sgnl.filtfilt(o_filter[0], o_filter[1], modd)
	return demodd


