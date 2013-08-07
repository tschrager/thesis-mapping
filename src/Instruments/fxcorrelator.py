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
        self.windowsize = 1024
        cost = 'power'
        
        #add the platforms
        self.platforms = {}
        self.platforms['ROACH'] = Platform.createRoach(cost)
        self.platforms['GPU'] = Platform.createGTX580Server(cost)
        
        # add the ADC
        adc_bw = bandwidth*input_bitwidth
        self.blocks['ADC'] = CBlock('ADC',CBlock.getADCModel(self.platforms, bandwidth, input_bitwidth),-1,0,0,'PFB',0,adc_bw,numant)
        self.totalblocks += numant
        
        # add the PFB
        self.blocks['PFB'] = CBlock('PFB',CBlock.getPFBModel(self.platforms, bandwidth, input_bitwidth, numchannels),'ADC',0,adc_bw,'FFT',0,adc_bw,numant)
        self.totalblocks += numant
        #self.blocks.append
        
        # add the FFT
        fft_out_bandwidth = bandwidth* fft_out_bitwidth
        self.blocks['FFT'] = CBlock('FFT',CBlock.getFFTModel(self.platforms, bandwidth, numchannels),'PFB',0,adc_bw,'Transpose',0,fft_out_bandwidth,numant)
        self.totalblocks += numant
        
        # add the Transpose
        self.blocks['Transpose'] = CBlock('Transpose',CBlock.getTransposeModel(self.platforms, bandwidth, numchannels, self.windowsize),'FFT',0,fft_out_bandwidth,'XEng',1,fft_out_bandwidth,numant)
        self.totalblocks += numant
        
        # add the XEngines
        xengine_in_bandwidth = fft_out_bandwidth*numant/numchannels
        self.blocks['XEng'] = CBlock('XEng',CBlock.getXEngModel(self.platforms) ,'Transpose', 1,xengine_in_bandwidth,-1,0,0,numchannels)
        self.totalblocks += numchannels
        
        
        
        


    
