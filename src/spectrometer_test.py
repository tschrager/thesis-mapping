#!/usr/bin/python2.6

from Instruments import *

def place_spectrometer(numchannels,accumulation_length,bandwidth):
    #create the instrument
    myspectrometer = Spectrometer(10,10,10)
    #fill in instrument.blocks
    #fill in instrument.platforms
    #run the ilp by passing it the instrument
    #generateILP(myspectrometer)
    myspectrometer.runILP()
    
    
place_spectrometer(10,10,10)