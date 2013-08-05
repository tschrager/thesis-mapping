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
    def __init__(self, numchannels, numant, accumulation_length, bandwidth, input_bitwidth, fft_out_bitwidth):
        self.blocks = {}
        self.totalblocks = 0
        self.maxdesigns = 1
        
        #add the platforms
        self.platforms = {}
        
        self.platforms['ROACH'] = Platform('ROACH',20,10,40,['registers','luts','dsp','bram'])
        self.platforms['GPU'] = Platform('GPU',10,10,1,['time'])
        
        # add the ADC
        adc_bw = bandwidth*input_bitwidth
        self.blocks['ADC'] = CBlock({'ROACH': {'registers': 0, 'luts': 0, 'dsp': 0, 'bram': 0},'GPU': {'time': 1.1}},-1,0,0,'PFB',0,adc_bw,numant)
        self.totalblocks += numant
        
        # add the PFB
        self.blocks['PFB'] = CBlock({'ROACH': {'registers': 0.2, 'luts': 0.1, 'dsp': 0.1, 'bram': 0.4},'GPU': {'time': 0.56}},'ADC',0,adc_bw,'FFT',0,adc_bw,numant)
        self.totalblocks += numant
        #self.blocks.append
        
        # add the FFT
        fft_out_bandwidth = bandwidth* fft_out_bitwidth
        self.blocks['FFT'] = CBlock({'ROACH': {'registers': 0.2, 'luts': 0.1, 'dsp': 0.1, 'bram':0.4}, 'GPU': {'time': 0.5}},'PFB',0,adc_bw,'XEng',1,fft_out_bandwidth,numant)
        self.totalblocks += numant
        
        # add the XEngines
        xengine_in_bandwidth = fft_out_bandwidth*numant/numchannels
        self.blocks['XEng'] = CBlock(CBlock.getXEngModel(self.platforms) ,'FFT', 1,xengine_in_bandwidth,-1,0,0,numchannels)
        self.totalblocks += numchannels
        
        
        
        


    
