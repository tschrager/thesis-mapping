#!/usr/bin/python

from Instruments import *

numchannels = 10
numant = 572*2
accumulation_length = 10
bandwidth = 10

mycorrelator = FXCorrelator(numchannels, numant, accumulation_length, bandwidth)
mycorrelator.runILP()
