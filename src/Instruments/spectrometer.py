#!/usr/bin/python2.6

#from pulp import *
#import numpy
from instrument import Instrument
from cblock import CBlock
from platform import Platform
        
        
class Spectrometer(Instrument):
    def __init__(self, numchannels, accumulation_length, bandwidth):
        self.blocks = {}
        self.totalblocks = 0
        
        # add the PFB
        self.blocks['PFB'] = CBlock({'ROACH': 0.1,'GPU': 0.56},-1,0,0,'FFT',0,6.4,2)
        self.totalblocks += 2
        
        # add the FFT
        #self.blocks['FFT'] = CBlock({'ROACH': 0.1, 'GPU': 0.5},'PFB',0,6.4,'VAcc',0,6.4,1)
        self.blocks['FFT'] = CBlock({'ROACH': 0.1, 'GPU': 0.5},'PFB',0,6.4,-1,0,0,2)
        self.totalblocks += 2
        
        # add the accumulator
        #self.blocks['VAcc'] = CBlock({'ROACH': 0.1, 'GPU': 0.5},'FFT',0,6.4,-1,0,0,1)
        #self.totalblocks += 1
        
        #add the platforms
        self.platforms = {}
        
        self.platforms['ROACH'] = Platform(20,10,40)
        self.platforms['GPU'] = Platform(10,10,1)
        
        


    
    