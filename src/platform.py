from pulp import *
from numpy import *


class Platform(object):
    
    def __init__(self,resources):
        self.resources = resources