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
        
        
        
        


    
