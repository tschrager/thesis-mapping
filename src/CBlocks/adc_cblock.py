import abc
from cblock_base import CBlock_Base

class ADC_CBlock(CBlock_Base):
    
    def __init__(self,adc_bits,bandwidth):
        inputbw = 0
        outputbw = adc_bits*bandwidth
        return
        
    def generateConstraints(self):
        return