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

from pulp import *
from numpy import *


class Platform(object):
    
    def __init__(self, instrumenttype, cost, inputbw, outputbw, resources):
        self.instrumenttype = instrumenttype
        self.cost = cost
        self.inputbw = inputbw
        self.outputbw = outputbw
        self.resources = resources
     
    @classmethod   
    def createRoach(cls, costtype):
        if costtype == 'dollars':
            cost = 6700
        elif costtype == 'power':
            cost = 75
        return cls('ROACH',cost,40,40,['registers','luts','dsp','bram'])
    
    @classmethod    
    def createGTX580Server(cls, costtype):
        if costtype == 'dollars':
            cost = 3500
        elif costtype == 'power':
            cost = 475
        return cls('GPU',cost,10,1,['time'])
        
    def isFPGABoard(self):
        if(self.instrumenttype in ['IBOB','ROACH','ROACH2']):
            return True
        else:
            return False