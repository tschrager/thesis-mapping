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
from math import *
        
        
class WBSpectrometer(Instrument):
    def __init__(self, numcoarsechannels, numfinechannels, accumulation_length, bandwidth, input_bitwidth, fft_coarse_out_bitwidth, antennas=1):
        self.maxdesigns=0
        self.blocks = {}
        self.blockalgs = {}
        self.totalblocks = 0
        
        #add the platform array
        self.platforms = {}
        
        # add platforms: cost, inputbw, outputbw, resources
        self.platforms['ROACH'] = Platform('ROACH',6700,40,40,['registers','luts','dsp','bram'])
        self.platforms['GPU'] = Platform('GPU',3500,10,1,['time'])
        
        
        
        for i in range(0,antennas):
            # add the ADC
            adc_bw = bandwidth*input_bitwidth
            self.blocks['ADC'+`i`] = CBlock('ADC', CBlock.getADCModel(self.platforms, bandwidth, input_bitwidth),-1,0,0,'PFB'+`i`,0,adc_bw,1)
            self.totalblocks += 1
        
            # add the PFB
            pfb_bw = bandwidth*32
            self.blocks['PFB'+`i`] = CBlock('PFB',CBlock.getPFBModel(self.platforms, bandwidth, pfb_bw, numcoarsechannels),'ADC'+`i`,0,adc_bw,'FFT_coarse'+`i`,0,adc_bw,1)
            self.totalblocks += 1
        
            # add the FFT
            #print CBlock.getFFTModel(self.platforms, bandwidth, input_bitwidth, numchannels)
            fft_coarse_out_bandwidth = bandwidth* fft_coarse_out_bitwidth*2
            self.blocks['FFT_coarse'+`i`] = CBlock('FFT_coarse',CBlock.getFFTModel(self.platforms, bandwidth, numcoarsechannels),'PFB'+`i`,0,pfb_bw,'Transpose'+`i`,0,fft_coarse_out_bandwidth,1)
            self.totalblocks += 1
            
            fft_fine_in_bandwidth = fft_coarse_out_bandwidth/numcoarsechannels
            finemodel = CBlock.getFFTModel(self.platforms, fft_fine_in_bandwidth, numfinechannels)
            if(finemodel['GPU']['time']<0.1):
                multiplier = pow(2,int(log(0.1/finemodel['GPU']['time'],2)))
            else:
                multiplier = 1
            finemodel['GPU']['time'] = finemodel['GPU']['time']*multiplier
            fine_blocks = int(numcoarsechannels/multiplier)
            fine_block_bandwidth = fft_coarse_out_bandwidth/fine_blocks
            
            self.blocks['Transpose'+`i`] = CBlock('Transpose', CBlock.getTransposeModel(self.platforms, bandwidth, numcoarsechannels, numfinechannels), 'FFT_coarse'+`i`,0,fft_coarse_out_bandwidth,'FFT_fine'+`i`,1,fft_coarse_out_bandwidth,1)
            self.totalblocks += 1
        
            self.blocks['FFT_fine'+`i`] = CBlock('FFT_fine',finemodel,'Transpose'+`i`,0,fine_block_bandwidth,'VAcc'+`i`,0,fft_fine_in_bandwidth,fine_blocks)
            self.totalblocks += fine_blocks
        
            self.blocks['VAcc'+`i`] = CBlock('VAcc',{'ROACH': {'registers': 0.2, 'luts': 0.1, 'dsp': 0, 'bram':0.4}, 'GPU': {'time': 0.001}},'FFT_fine'+`i`,0,fine_block_bandwidth,-1,0,0,fine_blocks)
            self.totalblocks += fine_blocks
        
        


    
    