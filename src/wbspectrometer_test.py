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
    
table_file = open('Tables/wbspec_table.tex', 'w+')
table_file.write('\\begin{tabular}{| c | c | c | c | c | c |} \n\hline \n\diaghead{\\theadfont Diag ColumnmnHead II}{\\textbf{Antennas}}{\\textbf{Dimensions}} & 256 by 524,288  & 512 by 262,144  & 1024 by 131,072  &2048 by 65,536  & 4096 by 32,768\\\\ \n \\hline \n')


#for antennas in {1,3,5,7}:
#for antennas in {1,2}:
for antennas in range(1,8)
    #numcoarsechannels = 256
    numcoarsechannels = 1024
    numfinechannels = totalchannels/numcoarsechannels
    table_file.write('%d'%(antennas))
    while numcoarsechannels <= 4096:
        #create the instrument
        #sys.stdout = open('Mappings/wbspec_'+`numcoarsechannels`+'_'+`numfinechannels`+'_'+`antennas`, 'w')
        mywbspectrometer = WBSpectrometer(numcoarsechannels, numfinechannels, accumulation_length, bandwidth, input_bitwidth, fft_coarse_out_bitwidth, antennas)
        tablestr = mywbspectrometer.runILP()
        table_file.write(' & ')
        table_file.write(tablestr)
        numcoarsechannels = numcoarsechannels*2
        numfinechannels = numfinechannels/2
    table_file.write('\\\\ \n \hline \n')

table_file.write('\end{tabular}\n')
