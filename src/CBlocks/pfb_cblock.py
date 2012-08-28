import abc
from cblock_base import CBlock_Base

class PFB_CBlock(CBlock_Base):
    
    def __init__(self,adc_bits,bandwidth):
        inputbw = adc_bits*bandwidth
        outputbw = inputbw
        return
        
    def generateConstraints(self):
        return