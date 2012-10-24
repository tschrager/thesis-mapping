#!/usr/bin/python2.6

from pulp import *
import numpy
from instrument import Instrument
from cblock import CBlock
from platform import Platform
        
        
class Spectrometer(Instrument):
    def __init__(self, numchannels, accumulation_length, bandwidth):
        self.blocks = []
        
        # add the PFB
        #self.blocks.append
        
        # add the FFT
        
        # add the accumulator
        self.platforms = []
        
        


    
    