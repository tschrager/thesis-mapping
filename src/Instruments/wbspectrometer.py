#!/usr/bin/python2.6

#from pulp import *
#import numpy
from instrument import Instrument
from cblock import CBlock
from platform import Platform
        
        
class WBSpectrometer(Instrument):
    def __init__(self, numcoarsechannels, numfinechannels, accumulation_length, bandwidth, input_bitwidth, fft_coarse_out_bitwidth):
        self.blocks = {}
        self.totalblocks = 0
        
        #add the platform array
        self.platforms = {}
        
        # add platforms: cost, inputbw, outputbw, resources
        self.platforms['ROACH'] = Platform('ROACH',6700,40,40,['registers','slices','dsp','bram'])
        self.platforms['GPU'] = Platform('GPU',3500,10,1,['time'])
        
        # add the ADC
        adc_bw = bandwidth*input_bitwidth
        self.blocks['ADC'] = CBlock({'ROACH': {'registers': 0, 'slices': 0, 'dsp': 0, 'bram': 0},'GPU': {'time': 1.1}},-1,0,0,'PFB',0,adc_bw,1)
        self.totalblocks += 1
        
        # add the PFB
        self.blocks['PFB'] = CBlock({'ROACH': {'registers': 0.2, 'slices': 0.1, 'dsp': 0.1, 'bram': 0.4},'GPU': {'time': 0.56}},'ADC',0,adc_bw,'FFT_coarse',0,adc_bw,1)
        self.totalblocks += 1
        
        # add the FFT
        fft_coarse_out_bandwidth = bandwidth* fft_coarse_out_bitwidth
        self.blocks['FFT_coarse'] = CBlock({'ROACH': {'registers': 0.2, 'slices': 0.1, 'dsp': 0.1, 'bram':0.4}, 'GPU': {'time': 0.5}},'PFB',0,adc_bw,'FFT_fine',0,fft_coarse_out_bandwidth,1)
        self.totalblocks += 1
        
        fft_fine_in_bandwidth = fft_coarse_out_bandwidth/numcoarsechannels
        self.blocks['FFT_fine'] = CBlock({'ROACH': {'registers': 0.2, 'slices': 0.1, 'dsp': 0.1, 'bram':0.4}, 'GPU': {'time': 0.1}},'FFT_coarse',0,fft_fine_in_bandwidth,'VAcc',0,fft_fine_in_bandwidth,numcoarsechannels)
        self.totalblocks += numcoarsechannels
        
        self.blocks['VAcc'] = CBlock({'ROACH': {'registers': 0.2, 'slices': 0.1, 'dsp': 0.1, 'bram':0.4}, 'GPU': {'time': 0.1}},'FFT_fine',0,fft_fine_in_bandwidth,-1,0,0,numcoarsechannels)
        self.totalblocks += numcoarsechannels
        
        
        


    
    