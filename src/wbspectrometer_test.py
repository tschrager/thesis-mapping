#!/usr/bin/python

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



from Instruments import *
import sys

totalchannels = 4096*32768

accumulation_length  = 10
bandwidth = 0.3
input_bitwidth = 8
fft_coarse_out_bitwidth = 8
antennas = 3
    
#for antennas in {1,3,5,7}:
for antennas in {7}:
    #numcoarsechannels = 256
    numcoarsechannels = 1024
    numfinechannels = totalchannels/numcoarsechannels
    while numcoarsechannels <= 4096:
        #create the instrument
        sys.stdout = open('Mappings/wbspec_'+`numcoarsechannels`+'_'+`numfinechannels`+'_'+`antennas`, 'w')
        mywbspectrometer = WBSpectrometer(numcoarsechannels, numfinechannels, accumulation_length, bandwidth, input_bitwidth, fft_coarse_out_bitwidth, antennas)
        mywbspectrometer.runILP()
        numcoarsechannels = numcoarsechannels*2
        numfinechannels = numfinechannels/2

