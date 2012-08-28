import abc
from cblock_base import CBlock_Base

class VAcc_CBlock(CBlock_Base):
    
    def __init__(self,adc_bits,bandwidth,acc_len):
        inputbw = adc_bits*bandwidth
        outputbw = inputbw/acc_len
        return
        
    def generateConstraints(self):
        return