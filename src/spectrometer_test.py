#!/usr/bin/python

# Copyright (c) 2012, Terry Filiba
# All rights reserved.
# 
# This file is part of Foobar.
# 
# Foobar is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Foobar is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.



from Instruments import *

def place_spectrometer(numchannels,accumulation_length,bandwidth):
    #create the instrument
    myspectrometer = Spectrometer(10,10,10)
    #fill in instrument.blocks
    #fill in instrument.platforms
    #run the ilp by passing it the instrument
    #generateILP(myspectrometer)
    myspectrometer.runILP()
    
    
place_spectrometer(10,10,10)
