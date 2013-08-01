#!/usr/bin/python2.6

#from pulp import *
#import numpy
from instrument import Instrument
from cblock import CBlock
from platform import Platform
   
#from working ilp test. need to generate this      
# numplatforms = 2
# 
# #design pfb, fft, xeng
# # blocktypes = 5
# # numblocks = numpy.array([128,128,128,128,128])
# # blockresourcesonplatform = numpy.array([[0.1,0.5],[0.1,0.5],[0.1,0.5],[0.1,0.5],[0.2,0.25]])
# 
# #design fft, xeng
# # blocktypes = 2
# # numblocks = numpy.array([128,1024])
# # blockresourcesonplatform = numpy.array([[0.1,0.5],[0.2,0.25]])
# 
# #design pfb, fft, xeng
# #blocktypes = 3
# numblocks = numpy.array([16,16,16])
# 
# blockresourcesonplatform = numpy.array([[0.1,0.5],[0.1,0.5],[0.9,0.25]])
# 
# inputfrom = [-1,0,1]
# inputconnection = [0,0,1]
# blockinputbw = [0,6.4,6.4]
# 
# outputto = [1,2,-1]
# outputconnection = [0,1,0]
# blockoutputbw = [6.4,6.4,0]
# 
# platforminputbw = [10,10]
# platformoutputbw = [40,1]
# 
# totalblocks = sum(numblocks)
# numboards = totalblocks
# 
# platformcosts = numpy.array([20,10])
        
class FXCorrelator(Instrument):
    def __init__(self, numchannels, numant, accumulation_length, bandwidth):
        self.blocks = {}
        self.totalblocks = 0
        
        # add the ADC
        self.blocks['ADC'] = CBlock({'ROACH': {'registers': 0, 'slices': 0, 'dsp': 0, 'bram': 0},'GPU': {'time': 1.1}},-1,0,0,'PFB',0,6.4,numant)
        self.totalblocks += numant
        
        # add the PFB
        self.blocks['PFB'] = CBlock({'ROACH': {'registers': 0.2, 'slices': 0.1, 'dsp': 0.1, 'bram': 0.4},'GPU': {'time': 0.56}},'ADC',0,6.4,'FFT',0,6.4,numant)
        self.totalblocks += numant
        #self.blocks.append
        
        # add the FFT
        self.blocks['FFT'] = CBlock({'ROACH': {'registers': 0.2, 'slices': 0.1, 'dsp': 0.1, 'bram':0.4}, 'GPU': {'time': 0.5}},'PFB',0,6.4,'XEng',1,6.4,numant)
        self.totalblocks += numant
        
        # add the XEngines
        self.blocks['XEng'] = CBlock({'ROACH': {'registers': 0.9, 'slices': 0.1, 'dsp': 0.1, 'bram':0.4}, 'GPU': {'time': 0.25}} ,'FFT', 1,6.4,-1,0,0,numchannels)
        self.totalblocks += numchannels
        
        #add the platforms
        self.platforms = {}
        
        self.platforms['ROACH'] = Platform(20,10,40,['registers','slices','dsp','bram'])
        self.platforms['GPU'] = Platform(10,10,1,['time'])
        
        


    
