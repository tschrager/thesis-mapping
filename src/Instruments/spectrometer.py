#!/usr/bin/python2.6


# Copyright (c) 2012, Terry Filiba
# All rights reserved.
# 
# This file is part of ORCAS.
# 
# ORCAS is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# ORCAS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with ORCAS.  If not, see <http://www.gnu.org/licenses/>.

#from pulp import *
#import numpy
from instrument import Instrument
from cblock import CBlock
from platform import Platform
        
        
class Spectrometer(Instrument):
    def __init__(self, numchannels, accumulation_length, bandwidth, input_bitwidth, fft_out_bitwidth):
        self.blocks = {}
        self.totalblocks = 0
        
        #add the platform array
        self.platforms = {}
        
        # add platforms: cost, inputbw, outputbw, resources
        self.platforms['ROACH'] = Platform('ROACH',6700,40,40,['registers','slices','dsp','bram'])
        self.platforms['GPU'] = Platform('GPU',3500,10,1,['time'])
        
        # add the ADC
        adc_bw = bandwidth*input_bitwidth
        self.blocks['ADC'] = CBlock(CBlock.getADCModel(self.platforms),-1,0,0,'PFB',0,adc_bw,1)
        self.totalblocks += 1
        
        # add the PFB
        self.blocks['PFB'] = CBlock({'ROACH': {'registers': 0.2, 'slices': 0.1, 'dsp': 0.1, 'bram': 0.4},'GPU': {'time': 0.56}},'ADC',0,adc_bw,'FFT',0,adc_bw,1)
        self.totalblocks += 1
        
        # add the FFT
        fft_out_bandwidth = bandwidth* fft_out_bitwidth
        self.blocks['FFT'] = CBlock({'ROACH': {'registers': 0.2, 'slices': 0.1, 'dsp': 0.1, 'bram':0.4}, 'GPU': {'time': 0.5}},'PFB',0,adc_bw,'VAcc',0,fft_out_bandwidth,1)
        self.totalblocks += 1
        
        #add the Vacc
        self.blocks['VAcc'] = CBlock({'ROACH': {'registers': 0.2, 'slices': 0.1, 'dsp': 0.1, 'bram':0}, 'GPU': {'time': 0.1}},'FFT',0,fft_out_bandwidth,-1,0,0,1)
        self.totalblocks += 1
        
        
        
        
        


    
    