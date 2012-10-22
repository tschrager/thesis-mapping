#!/usr/bin/python2.6

from pulp import *
import numpy

class CBlock:
    def __init__(self, numplatforms, ):
        self.resources = np.array
        
class Platform:
    def __init__(self, type):
        return
        
        
class Spectrometer(Instrument):
    def __init__(self, numchannels, accumulation_length, bandwidth):
        self.blocks = []
        
        # add the PFB
        #self.blocks.append
        
        # add the FFT
        
        # add the accumulator
        self.platforms = []
        
        

def place_spectrometer(numchannels,accumulation_length,bandwidth):
    #create the instrument
    myspectrometer = Spectrometer()
    #fill in instrument.blocks
    #fill in instrument.platforms
    #run the ilp by passing it the instrument
    generateILP(myspectrometer)
    
    
place_spectrometer(10,10,10)
    
    