import abc
from instrument_base import Instrument_Base
from CBlocks import *
from Platforms import *

#defaults
adc_bits = 8

class Spectrometer(Instrument_Base):
    
    def __init__(self,bandwidth,channels,acc_len):
        self.bandwidth=bandwidth
        self.channels=channels
        self.acc_len=acc_len
        self.adc_bits=adc_bits
        
    def generateILP(self):
        maxhardware = numblocks
        #loop over all possible platforms and blocks
        for platorm in Platforms:
            for currentblock in numblocks:
                
        return
        
    def generateDataflow(self):
        self.dataflow = []
        self.dataflow.append(ADC_CBlock(self.adc_bits,self.bandwidth))
        self.dataflow.append(PFB_CBlock(self.adc_bits,self.bandwidth))
        self.dataflow.append(FFT_CBlock(self.adc_bits,self.bandwidth))
        self.dataflow.append(VAcc_CBlock(self.adc_bits,self.bandwidth,self.acc_len))
        numblocks = 3
        return