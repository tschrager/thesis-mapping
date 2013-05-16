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
        
        # add the ADC
        self.blocks['ADC'] = CBlock({'ROACH': {'registers': 0, 'slices': 0, 'something': 0, 'bram': 0},'GPU': {'time': 1.1}},-1,0,0,'PFB',0,6.4,1)
        self.totalblocks += 1
        
        # add the PFB
        self.blocks['PFB'] = CBlock({'ROACH': {'registers': 0.2, 'slices': 0.1, 'something': 0.5, 'bram': 0.4},'GPU': {'time': 0.56}},'ADC',0,6.4,'FFT_coarse',0,6.4,1)
        self.totalblocks += 1
        
        # add the FFT
        self.blocks['FFT_coarse'] = CBlock({'ROACH': {'registers': 0.2, 'slices': 0.1, 'something': 0.1, 'bram':0.4}, 'GPU': {'time': 0.5}},'PFB',0,6.4,'FFT_fine',0,6.4,1)
        self.totalblocks += 1
        
        self.blocks['FFT_fine'] = CBlock({'ROACH': {'registers': 0.2, 'slices': 0.1, 'something': 0.1, 'bram':0.4}, 'GPU': {'time': 0.1}},'FFT_coarse',0,6.4/16,-1,0,0,16)
        self.totalblocks += 16
        
        # add the accumulator
        #self.blocks['VAcc'] = CBlock({'ROACH': 0.1, 'GPU': 0.5},'FFT',0,6.4,-1,0,0,1)
        #self.totalblocks += 1
        
        #add the platforms
        self.platforms = {}
        
        # add platforms: cost, inputbw, outputbw, resources
        #self.platforms['ADC'] = Platform(0,10,6.4,['empty'])
        self.platforms['ROACH'] = Platform(6700,40,40,['registers','slices','something','bram'])
        self.platforms['GPU'] = Platform(3500,10,1,['time'])
        
        


    
    