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
        self.maxdesigns = 1
        self.singleimplementation = 0
        self.windowsize = 1024
        cost = 'dollars'
        
        #add the platforms
        self.platforms = {}
        self.platforms['ROACH'] = Platform.createRoach(cost)
        self.platforms['GPU'] = Platform.createGTX580Server(cost)
        
        # add the ADC
        adc_bw = skybandwidth*2*input_bitwidth
        self.blocks['ADC'] = CBlock('ADC',CBlock.getADCModel(self.platforms, skybandwidth, input_bitwidth),-1,0,0,'PFB',0,4*adc_bw,numantpol/4)
        self.totalblocks += numantpol/4
        
        # add the PFB
        #self.blocks['FIR'] = CBlock('FIR',CBlock.getPFBModel(self.platforms, skybandwidth, input_bitwidth, numchannels),'ADC',0,adc_bw,'FFT',0,adc_bw,numantpol)
        #self.totalblocks += numantpol
        #self.blocks.append
        
        # add the FFT
        #fft_out_bandwidth = skybandwidth * 2 * fft_out_bitwidth
        #self.blocks['FFT'] = CBlock('FFT',CBlock.getFFTModel(self.platforms, skybandwidth, numchannels),'FIR',0,adc_bw,'Transpose',0,fft_out_bandwidth,numantpol)
        #self.totalblocks += numantpol
        
        #use pfb to process 4 channels at a time
        fft_out_bandwidth = skybandwidth * 2 * fft_out_bitwidth
        pfb_model = CBlock.getPFBModel(self.platforms, skybandwidth, input_bitwidth, numchannels)
        fft_model = CBlock.getFFTModel(self.platforms, skybandwidth, numchannels)
        self.blocks['PFB'] = CBlock('PFB',CBlock.combineModels(pfb_model, fft_model),'ADC',0,4*adc_bw,'Transpose',0,4*fft_out_bandwidth,numantpol/4)
        self.totalblocks += numantpol/4
        #print CBlock.combineModels(pfb_model, fft_model)
        
        # add the Transpose
        self.blocks['Transpose'] = CBlock('Transpose',CBlock.getTransposeModel(self.platforms, skybandwidth, numchannels, self.windowsize),'PFB',0,4*fft_out_bandwidth,'XEng',1,4*fft_out_bandwidth,numantpol/4)
        self.totalblocks += numantpol/4
        
        # add the XEngines
        gtx580_max_bw = {32:0.06914, 64:0.03095, 96:0.01748, 128:0.01069, 192:0.00536, 256:0.00318, 512:0.00087, 1024:0.00023}
        minxengines = int(numpy.power(2,numpy.ceil(numpy.log2(skybandwidth/gtx580_max_bw[numantpol]))))
        numxengines = minxengines*4
        xengine_sky_bandwidth = skybandwidth/numxengines
        #print xengine_sky_bandwidth
        xengine_in_bandwidth = numantpol*fft_out_bandwidth/numxengines
        self.blocks['XEng'] = CBlock('XEng',CBlock.getXEngModel(self.platforms, xengine_sky_bandwidth, numantpol) ,'Transpose', 1,xengine_in_bandwidth,-1,0,0,numxengines)
        self.totalblocks += numxengines
        
        # add the VAcc
        #self.blocks['XEng'] = CBlock('XEng',CBlock.getXEngModel(self.platforms) ,'Transpose', 1,xengine_in_bandwidth,-1,0,0,numchannels)
        #self.totalblocks += numchannels
        
        
        
        


    
