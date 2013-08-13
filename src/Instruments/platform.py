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
    
    def __init__(self, platformtype, cost, inputbw, outputbw, resources, availableresources):
        self.platformtype = platformtype
        self.cost = cost
        self.inputbw = inputbw
        self.outputbw = outputbw
        self.resources = resources
        self.availableresources = availableresources
     
    @classmethod   
    def createRoach(cls, costtype):
        if costtype == 'dollars':
            cost = 6700
        elif costtype == 'power':
            cost = 75
        availableresources= {'registers': 58880.,'luts': 58880., 'dsp': 640.,'bram': 244.}
        return cls('ROACH',cost,40,40,['registers','luts','dsp','bram'], availableresources)
    
    @classmethod   
    def createRoach2(cls, costtype):
        if costtype == 'dollars':
            cost = 10,500
        elif costtype == 'power':
            cost = 85
        availableresources = {'registers': 595200.,'luts': 297600., 'dsp': 2016.,'bram': 1064.}
        return cls('ROACH2',cost,40,40,['registers','luts','dsp','bram'], availableresources)
    
    @classmethod    
    def createGTX580Server(cls, costtype):
        if costtype == 'dollars':
            cost = 3500
        elif costtype == 'power':
            cost = 475
        availableresources = {'time':1}
        return cls('GTX580',cost,20,1,['time'], availableresources)
        
    def isFPGABoard(self):
        if(self.platformtype in ['IBOB','ROACH','ROACH2']):
            return True
        else:
            return False
            
    def calcPercentUtilization(self, usedresources):
        utilization = {}
        for resource in self.availableresources:
            utilization[resource] = usedresources[resource]/self.availableresources[resource]
        return utilization
