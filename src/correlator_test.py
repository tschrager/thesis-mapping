#!/usr/bin/python

from Instruments import *

numchannels = 16
numant = 16
accumulation_length = 10
bandwidth = 0.8
input_bitwidth = 8
fft_out_bitwidth = 4

mycorrelator = FXCorrelator(numchannels, numant, accumulation_length, bandwidth, input_bitwidth, fft_out_bitwidth)
mycorrelator.runILP()