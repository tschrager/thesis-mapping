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
        self.singleimplementation = 1
        self.windowsize = 1024
        cost = 'dollars'
        #cost = 'power'
        
        #add the platforms
        self.platforms = {}
        self.platforms['GTX580'] = Platform.createGTX580Server(cost)
        self.platforms['ROACH'] = Platform.createRoach(cost)
        #self.platforms['DualGTX690'] = Platform.createDualGTX690Server(cost)
        #self.platforms['ROACH2'] = Platform.createRoach2(cost)
        
        
        # add the ADC
        adc_bw = skybandwidth*2*input_bitwidth
        #self.blocks['ADC'] = CBlock('ADC',CBlock.getADCModel(self.platforms, skybandwidth, input_bitwidth),-1,0,0,'FIR',0,4*adc_bw,numantpol/4)
        # we are using a 16 input adc board
        # multiplier needs to be a multiple of 4 because the benchmarks do 4 parallel firs and ffts
        adcmultiplier = 4   # process 4 streams at a time
        self.blocks['ADC'] = CBlock('ADC',CBlock.getADCModel(self.platforms, skybandwidth, input_bitwidth), -1,0,0,'PFB',0,adcmultiplier*adc_bw,numantpol/adcmultiplier, CBlock.getADCMaximums(self.platforms, adcmultiplier))
        self.totalblocks += numantpol/adcmultiplier
        

        #use pfb to process 4 channels at a time
        fft_out_bandwidth = skybandwidth * 2 * fft_out_bitwidth
        pfb_model = CBlock.getPFBModel(self.platforms, skybandwidth, input_bitwidth, numchannels)
        fft_model = CBlock.getFFTRealModel(self.platforms, skybandwidth, numchannels)
        firfftmodel = CBlock.combineModels(pfb_model, fft_model)
        #print firfftmodel
        #firfft2xmodel = CBlock.combineModels(firfftmodel, firfftmodel)
        #print firfft2xmodel
        self.blocks['PFB'] = CBlock('PFB',firfftmodel,'ADC',0,adcmultiplier*adc_bw,'Transpose',0,adcmultiplier*fft_out_bandwidth,numantpol/adcmultiplier)
        self.totalblocks += numantpol/adcmultiplier
        
        transposemodel = CBlock.getTransposeModel(self.platforms, skybandwidth, numchannels, self.windowsize)
        self.blocks['Transpose'] = CBlock('Transpose',transposemodel,'PFB',0,adcmultiplier*fft_out_bandwidth,'XEng',0,adcmultiplier*fft_out_bandwidth,numantpol/adcmultiplier)
        self.totalblocks += numantpol/adcmultiplier

        
        # add the PFBTranspose
        #fft_out_bandwidth = skybandwidth * 2 * fft_out_bitwidth
        #firmodel = CBlock.getPFBModel(self.platforms, skybandwidth, input_bitwidth, numchannels)
        #fftmodel = CBlock.getFFTRealModel(self.platforms, skybandwidth, numchannels)
        #transposemodel = CBlock.getTransposeModel(self.platforms, skybandwidth, numchannels, self.windowsize)
        #combinedmodel = CBlock.combineModels(firmodel, CBlock.combineModels(fftmodel, transposemodel))
        #we need 4 of these for our 16 input adc
        #self.blocks['PFBTranspose'] = CBlock('PFBTranspose',combinedmodel,'ADC',0,adcmultiplier*adc_bw,'XEng',1,adcmultiplier * fft_out_bandwidth,numantpol/adcmultiplier)
        #self.totalblocks += numantpol/adcmultiplier
        
        
        
        # add the XEngines
        gtx580_max_bw = {32:0.06914, 64:0.03095, 96:0.01748, 128:0.01069, 192:0.00536, 256:0.00318, 512:0.00087, 1024:0.00023}
        # the minimum number of xengines we need
        # if we use any fewer, they will not fit on the gpu
        mingpuxengines = int(numpy.power(2,numpy.ceil(numpy.log2(skybandwidth/gtx580_max_bw[numantpol]))))
        
        # assume xengine is running at 200MHz, takes nantpol clock cycles to get the data out for a single frequency channel
        # maximum bandwidth it can process is 200MHz/nantpol
        maxfpgaxengbw = .2/numantpol
        
        #the maximum amount of bandwidth we can process in an xengine and still support our platforms
        maxxenginebw = min(maxfpgaxengbw,gtx580_max_bw[numantpol])
        
        # we need to create this many xengines to meet the spec
        minxengines = int(skybandwidth/maxxenginebw)
        
        #note: this needs to be a power of 2
        numxengines = 8*minxengines
        
        #numxengines = 4*mingpuxengines
        #print 'Num xengines is: ' + `numxengines`
        #numxengines = mingpuxengines*4
        xengine_sky_bandwidth = skybandwidth/numxengines
        #print 'Sky bw is: ' + `xengine_sky_bandwidth`
        #print xengine_sky_bandwidth
        xengine_in_bandwidth = numantpol*fft_out_bandwidth/numxengines
        #print CBlock.getXEngModel(self.platforms, xengine_sky_bandwidth, numantpol)
        self.blocks['XEng'] = CBlock('XEng',CBlock.getXEngModel(self.platforms, xengine_sky_bandwidth, numantpol) ,'Transpose', 1,xengine_in_bandwidth,-1,0,0,numxengines)
        self.totalblocks += numxengines
        
        # add the VAcc
        #self.blocks['XEng'] = CBlock('XEng',CBlock.getXEngModel(self.platforms) ,'Transpose', 1,xengine_in_bandwidth,-1,0,0,numchannels)
        #self.totalblocks += numchannels
        
        
        
        


    
