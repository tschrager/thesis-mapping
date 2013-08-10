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
    def __init__(self, numchannels, numantpol, accumulation_length, skybandwidth, input_bitwidth, fft_out_bitwidth):
        self.blocks = {}
        self.totalblocks = 0
        self.maxdesigns = 0
        self.singleimplementation = 0
        self.windowsize = 1024
        cost = 'dollars'
        
        #add the platforms
        self.platforms = {}
        self.platforms['ROACH'] = Platform.createRoach(cost)
        self.platforms['GPU'] = Platform.createGTX580Server(cost)
        
        # add the ADC
        adc_bw = skybandwidth*2*input_bitwidth
        self.blocks['ADC'] = CBlock('ADC',CBlock.getADCModel(self.platforms, skybandwidth, input_bitwidth),-1,0,0,'FIR',0,adc_bw,numantpol)
        self.totalblocks += numantpol
        
        # add the PFB
        #self.blocks['FIR'] = CBlock('FIR',CBlock.getPFBModel(self.platforms, skybandwidth, input_bitwidth, numchannels),'ADC',0,adc_bw,'FFT',0,adc_bw,numantpol)
        #self.totalblocks += numantpol
        #self.blocks.append
        
        # add the FFT
        #fft_out_bandwidth = skybandwidth * 2 * fft_out_bitwidth
        #self.blocks['FFT'] = CBlock('FFT',CBlock.getFFTModel(self.platforms, skybandwidth, numchannels),'FIR',0,adc_bw,'Transpose',0,fft_out_bandwidth,numantpol)
        #self.totalblocks += numantpol
        
        fft_out_bandwidth = skybandwidth * 2 * fft_out_bitwidth
        pfb_model = CBlock.getPFBModel(self.platforms, skybandwidth, input_bitwidth, numchannels)
        self.blocks['FIR-FFT'] = CBlock('FIR',CBlock.getPFBModel(self.platforms, skybandwidth, input_bitwidth, numchannels),'ADC',0,adc_bw,'Transpose',0,fft_out_bandwidth,numantpol)
        
        # add the Transpose
        self.blocks['Transpose'] = CBlock('Transpose',CBlock.getTransposeModel(self.platforms, skybandwidth, numchannels, self.windowsize),'FFT',0,fft_out_bandwidth,'XEng',1,fft_out_bandwidth,numantpol)
        self.totalblocks += numantpol
        
        # add the XEngines
        gtx580_max_bw = {32:0.06914, 64:0.03095, 96:0.01748, 128:0.01069, 192:0.00536, 256:0.00318, 512:0.00087, 1024:0.00023}
        minxenginebw = skybandwidth/numchannels
        multiplier = numpy.power(2,int(numpy.log2(gtx580_max_bw[numantpol]/minxenginebw)))/8
        
        numxengines = int(numchannels/multiplier)
        #print numxengines
        xengine_in_bandwidth = fft_out_bandwidth*numantpol/numxengines
        xengine_sky_bandwidth = skybandwidth/numxengines
        print multiplier
        print numxengines
        print xengine_sky_bandwidth
        self.blocks['XEng'] = CBlock('XEng',CBlock.getXEngModel(self.platforms, xengine_sky_bandwidth, numantpol, numchannels) ,'Transpose', 1,xengine_in_bandwidth,-1,0,0,numxengines)
        self.totalblocks += numxengines
        
        # add the VAcc
        #self.blocks['XEng'] = CBlock('XEng',CBlock.getXEngModel(self.platforms) ,'Transpose', 1,xengine_in_bandwidth,-1,0,0,numchannels)
        #self.totalblocks += numchannels
        
        
        
        


    
