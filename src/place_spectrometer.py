#!/usr/bin/python2.6

from pulp import *
import numpy

def place_spectrometer(numchannels,accumulation_length,bandwidth):
    #create the instrument
    myspectrometer = Instrument('spectrometer')
    #fill in instrument.blocks
    #fill in instrument.platforms
    #run the ilp by passing it the instrument
    