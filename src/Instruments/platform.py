from pulp import *
from numpy import *


class Platform(object):
    
    def __init__(self, cost, inputbw, outputbw):
        self.cost = cost
        self.inputbw = inputbw
        self.outputbw = outputbw