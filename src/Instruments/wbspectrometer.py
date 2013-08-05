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

from instrument import Instrument
from cblock import CBlock
from platform import Platform
        
        
class WBSpectrometer(Instrument):
    def __init__(self, numcoarsechannels, numfinechannels, accumulation_length, bandwidth, input_bitwidth, fft_coarse_out_bitwidth):
        self.maxdesigns=0
        self.blocks = {}
        self.totalblocks = 0
        
        #add the platform array
        self.platforms = {}
        
        # add platforms: cost, inputbw, outputbw, resources
        self.platforms['ROACH'] = Platform('ROACH',6700,40,40,['registers','luts','dsp','bram'])
        self.platforms['GPU'] = Platform('GPU',3500,10,1,['time'])
        
        # add the ADC
        adc_bw = bandwidth*input_bitwidth
        self.blocks['ADC'] = CBlock(CBlock.getADCModel(self.platforms, bandwidth, input_bitwidth),-1,0,0,'PFB',0,adc_bw,1)
        self.totalblocks += 1
        
        # add the PFB
        self.blocks['PFB'] = CBlock(CBlock.getPFBModel(self.platforms, bandwidth, input_bitwidth, numcoarsechannels),'ADC',0,adc_bw,'FFT_coarse',0,adc_bw,1)
        self.totalblocks += 1
        
        # add the FFT
        #print CBlock.getFFTModel(self.platforms, bandwidth, input_bitwidth, numchannels)
        fft_coarse_out_bandwidth = bandwidth* fft_coarse_out_bitwidth
        self.blocks['FFT_coarse'] = CBlock(CBlock.getFFTModel(self.platforms, bandwidth, numcoarsechannels),'PFB',0,adc_bw,'FFT_fine',0,fft_coarse_out_bandwidth,1)
        self.totalblocks += 1
        
        
        #fft_fine_in_bandwidth = fft_coarse_out_bandwidth/numcoarsechannels
        #print fft_fine_in_bandwidth
        #print CBlock.getFFTModel(self.platforms, fft_fine_in_bandwidth, numfinechannels)
        self.blocks['FFT_fine'] = CBlock({'ROACH': {'registers': 0.2, 'luts': 0.1, 'dsp': 0.1, 'bram':0.4}, 'GPU': {'time': 0.1}},'FFT_coarse',0,fft_fine_in_bandwidth,'VAcc',0,fft_fine_in_bandwidth,numcoarsechannels)
        self.totalblocks += numcoarsechannels
        
        self.blocks['VAcc'] = CBlock({'ROACH': {'registers': 0.2, 'luts': 0.1, 'dsp': 0.1, 'bram':0.4}, 'GPU': {'time': 0.1}},'FFT_fine',0,fft_fine_in_bandwidth,-1,0,0,numcoarsechannels)
        self.totalblocks += numcoarsechannels
        
        
        


    
    