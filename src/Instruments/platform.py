from pulp import *
from numpy import *


class Platform(object):
    
    def __init__(self, instrumenttype, cost, inputbw, outputbw, resources):
        self.instrumenttype = instrumenttype
        self.cost = cost
        self.inputbw = inputbw
        self.outputbw = outputbw
        self.resources = resources
        
    def isFPGABoard(self):
        if(self.instrumenttype in ['IBOB','ROACH','ROACH2']):
            return True
        else:
            return False