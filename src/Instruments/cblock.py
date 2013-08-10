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

import re
import os
import math


gitrepo_dir = os.environ.get('GIT_REPOS')
benchmark_dir = gitrepo_dir+'/thesis-benchmarks/'

class CBlock:
    def __init__(self, algname, resourcearray, inputfrom, inputconnection, inputbw, outputto, outputconnection, outputbw, numblocks):
        self.algname = algname
        self.resources = resourcearray
        self.inputfrom = inputfrom
        self.inputconnection = inputconnection
        self.inputbw = inputbw
        self.outputto = outputto
        self.outputconnection = outputconnection
        self.outputbw = outputbw
        self.numblocks = numblocks
    
    # reads in data from map file
    @staticmethod
    def get_fpga_benchmarks(filename):
        if not os.path.isfile(filename):
            return {'registers':1.1, 'luts': 1.1, 'bram':1.1, 'dsp':1.1}
        benchmarkfile = open(filename,'r')
        benchmarktext = benchmarkfile.read()
        benchmarkfile.close()

        # remove commas in numbers
        benchmarktext = benchmarktext.replace(",","")

        # find numbers in map file
        result = {}
        result['registers'] = float(re.findall("Number of Slice Registers:\s*(\d+)\s*out of\s*\d+\s*\d+\%",benchmarktext)[0])\
            /int(re.findall("Number of Slice Registers:\s*\d+\s*out of\s*(\d+)\s*\d+\%",benchmarktext)[0])
        result['luts']  = float(re.findall("Number of Slice LUTs:\s*(\d+)\s*out of\s*\d+\s*\d+\%",benchmarktext)[0])\
            /int(re.findall("Number of Slice LUTs:\s*\d+\s*out of\s*(\d+)\s*\d+\%",benchmarktext)[0])
        result['bram']  = float(re.findall("Number of BlockRAM/FIFO:\s*(\d+)\s*out of\s*\d+\s*\d+\%",benchmarktext)[0])\
            /int(re.findall("Number of BlockRAM/FIFO:\s*\d+\s*out of\s*(\d+)\s*\d+\%",benchmarktext)[0])
        result['dsp']  = float(re.findall("Number of DSP48Es:\s*(\d+)\s*out of\s*\d+\s*\d+\%",benchmarktext)[0])\
            /int(re.findall("Number of DSP48Es:\s*\d+\s*out of\s*(\d+)\s*\d+\%",benchmarktext)[0])

        return result
        
    @staticmethod
    # reads in data from gpu results file
    def get_gpu_benchmarks(filename,size):
        benchmarkfile = open(filename,'r')
        benchmarktext = benchmarkfile.read()
        benchmarkfile.close()

        result = {}
        #check the regex...
        allbenchmarks = re.findall(`size`+"\s+(\d+)\s+\d+\.\d*\s+(\d+\.\d*)\s+\d+\.\d*\s+(\d+\.\d*)\s+\d+\.\d*\s+(\d+)",benchmarktext)
        #print allbenchmarks
        lastbenchmark = len(allbenchmarks)-1
        result['time'] = float(allbenchmarks[lastbenchmark][2])/(100*int(allbenchmarks[lastbenchmark][0]))
        return result
    
    @staticmethod
    def combineModels(model1, model2):
        newmodel = {}
        for platform in model1:
            newmodel[platform] = {}
            for resource in model1[platform]:
                newmodel[platform][resource] = model1[platform][resource] + model2[platform][resource] 
        return newmodel
    
    @staticmethod
    def getADCModel(platforms, bandwidth, input_bitwidth):
        model = {}
        for platform in platforms:
            model[platform] = {}
            # ADCs take no resources on an FPGA board
            if platforms[platform].isFPGABoard():
                for resource in platforms[platform].resources:
                    model[platform][resource] = 0
            # ADCs cannot be implemented on a differnt board type
            else:
                for resource in platforms[platform].resources:
                    model[platform][resource] = 1.1
        return model
    
    @staticmethod    
    def getPFBModel(platforms, bandwidth, input_bitwidth, numchannels):
        model = {}
        for platform in platforms:
            if platforms[platform].instrumenttype == 'ROACH':
                bench = CBlock.get_fpga_benchmarks(benchmark_dir+'fpga/pfb/results/v5sx95t/pfb_%02d_4_2_08_18_cw_map.map'%math.log(numchannels,2))
                model[platform] = bench
            if platforms[platform].instrumenttype == 'IBOB':
                model[platform] = {'resources':1.1}
            if platforms[platform].instrumenttype == 'GPU':
                bench = CBlock.get_gpu_benchmarks(benchmark_dir+'gpu/pfb/results/pfb_4_gtx580_100x',numchannels)
                #print bench['time']
                #Take time required and divide by time allowed
                # 1/bandwidth GHz * number of channels * 10^-6 = time allowed in ms
                bench['time'] = bench['time']/(1/bandwidth*numchannels*math.pow(10,-6))
                model[platform] = bench
        #print model        
        return model

    @staticmethod    
    def getFFTModel(platforms, bandwidth, numchannels):
        model = {}
        for platform in platforms:
            if platforms[platform].instrumenttype == 'ROACH':
                bench = CBlock.get_fpga_benchmarks(benchmark_dir+'fpga/fft/results/v5sx95t/fftw_%02d_2_18_18_cw_map.map'%math.log(numchannels,2))
                model[platform] = bench
            elif platforms[platform].instrumenttype == 'IBOB':
                model[platform] = {'resources':1.1}
            elif platforms[platform].instrumenttype == 'GPU':
                bench = CBlock.get_gpu_benchmarks(benchmark_dir+'gpu/fft/results/c2c_gtx580_100x',numchannels)
                #print bench['time']
                #Take time required and divide by time allowed
                # 1/bandwidth GHz * number of channels * 10^-6 = time allowed in ms
                bench['time'] = bench['time']/(1/bandwidth*numchannels*math.pow(10,-6))
                model[platform] = bench
        #print model        
        return model

    @staticmethod
    def getTransposeModel(platforms,bandwidth, inputdim, outputdim):
        return {'ROACH': {'registers': 0.1, 'luts': 0.1, 'dsp': 0.1, 'bram':0.1}, 'GPU': {'time': 1.1}}

    #process channels in groups of 
    @staticmethod
    def getXEngModel(platforms, subband, nantpol, numchannels):
        fpga_space = {8:{'registers': 2963, 'luts': 2434, 'dsp': 144, 'bram':9}, \
            16:{'registers': 5352, 'luts': 4068, 'dsp': 144, 'bram':12}}
        #gtx580_timing_in_s = {16:.15, 32:0.39, 48:0.71, 64:1.17, 96:2.4, 128:4.12, 256:13.11, 512:480.3}
        gtx580_max_bw = {32:0.06914, 64:0.03095, 96:0.01748, 128:0.01069, 192:0.00536, 256:0.00318, 512:0.00087, 1024:0.00023}
        model = {}
        for platform in platforms:
            if platforms[platform].isFPGABoard():
                if nantpol in fpga_space:
                    if platforms[platform].instrumenttype == 'ROACH':
                        model[platform] = {'registers':fpga_space[nantpol]['registers']/58880., 'luts':fpga_space[nantpol]['luts']/58880., \
                         'dsp':fpga_space[nantpol]['dsp']/640., 'bram':fpga_space[nantpol]['bram']/244.}
                else:
                    model[platform] = {'registers':1.1, 'luts': 1.1, 'bram':1.1, 'dsp':1.1}
            else:
                model[platform] = {'time': subband/gtx580_max_bw[nantpol]}
            
        print model
        return model

    @staticmethod
    def getVAccModel(platforms, bandwidth, fft_out_bitwidth, accumulation_length):
        return {'ROACH': {'registers': 0.2, 'luts': 0.1, 'dsp': 0.1, 'bram':0}, 'GPU': {'time': 0.1}, 'IBOB' : {'resources':1.1}}