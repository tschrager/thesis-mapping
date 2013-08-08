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
import numpy
        
class FXCorrelator(Instrument):
    def __init__(self, numchannels, numant, accumulation_length, bandwidth, input_bitwidth, fft_out_bitwidth):
        self.blocks = {}
        self.totalblocks = 0
        self.maxdesigns = 1
        self.singleimplementation = 1
        self.windowsize = 1024
        cost = 'dollars'
        
        #add the platforms
        self.platforms = {}
        self.platforms['ROACH'] = Platform.createRoach(cost)
        self.platforms['GPU'] = Platform.createGTX580Server(cost)
        
        # add the ADC
        adc_bw = bandwidth*input_bitwidth
        self.blocks['ADC'] = CBlock('ADC',CBlock.getADCModel(self.platforms, bandwidth, input_bitwidth),-1,0,0,'FIR',0,adc_bw,numant)
        self.totalblocks += numant
        
        # add the PFB
        self.blocks['FIR'] = CBlock('FIR',CBlock.getPFBModel(self.platforms, bandwidth, input_bitwidth, numchannels),'ADC',0,adc_bw,'FFT',0,adc_bw,numant)
        self.totalblocks += numant
        #self.blocks.append
        
        # add the FFT
        fft_out_bandwidth = bandwidth* fft_out_bitwidth
        self.blocks['FFT'] = CBlock('FFT',CBlock.getFFTModel(self.platforms, bandwidth, numchannels),'FIR',0,adc_bw,'Transpose',0,fft_out_bandwidth,numant)
        self.totalblocks += numant
        
        # add the Transpose
        self.blocks['Transpose'] = CBlock('Transpose',CBlock.getTransposeModel(self.platforms, bandwidth, numchannels, self.windowsize),'FFT',0,fft_out_bandwidth,'XEng',1,fft_out_bandwidth,numant)
        self.totalblocks += numant
        
        # add the XEngines
        gtx580_max_bw = {16:0.06914, 32:0.03095, 48:0.01748, 64:0.01069, 96:0.00536, 128:0.00318, 256:0.00087, 512:0.00023}
        minxenginebw = bandwidth/numchannels
        multiplier = numpy.power(2,int(numpy.log2(gtx580_max_bw[numant]/minxenginebw)))
        
        numxengines = int(numchannels/multiplier)
        #print numxengines
        xengine_in_bandwidth = fft_out_bandwidth*numant/numxengines
        xengine_sky_bandwidth = bandwidth/numxengines
        self.blocks['XEng'] = CBlock('XEng',CBlock.getXEngModel(self.platforms, xengine_sky_bandwidth, numant, numchannels) ,'Transpose', 1,xengine_in_bandwidth,-1,0,0,numxengines)
        self.totalblocks += numxengines
        
        # add the VAcc
        #self.blocks['XEng'] = CBlock('XEng',CBlock.getXEngModel(self.platforms) ,'Transpose', 1,xengine_in_bandwidth,-1,0,0,numchannels)
        #self.totalblocks += numchannels
        
        
        
        


    
