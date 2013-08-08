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

numchannels = 1024
numant = 128
accumulation_length = 10
bandwidth = 0.1
input_bitwidth = 8
fft_out_bitwidth = 4

mycorrelator = FXCorrelator(numchannels, numant, accumulation_length, bandwidth, input_bitwidth, fft_out_bitwidth)
mycorrelator.runILP()