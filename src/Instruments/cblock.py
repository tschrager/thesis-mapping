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
    def __init__(self, algname, resourcearray, inputfrom, inputconnection, inputbw, outputto, outputconnection, outputbw, numblocks, maximumblocks = None):
        self.algname = algname
        self.resources = resourcearray
        self.inputfrom = inputfrom
        self.inputconnection = inputconnection
        self.inputbw = inputbw
        self.outputto = outputto
        self.outputconnection = outputconnection
        self.outputbw = outputbw
        self.numblocks = numblocks
        self.maximumblocks = maximumblocks
    
    # reads in data from map file
    @staticmethod
    def get_fpga_utilization(filename):
        if not os.path.isfile(filename):
            return {'registers':1.1, 'luts': 1.1, 'bram':1.1, 'dsp':1.1}
        benchmarkfile = open(filename,'r')
        benchmarktext = benchmarkfile.read()
        benchmarkfile.close()

        # remove commas in numbers
        benchmarktext = benchmarktext.replace(",","")

        # find numbers in map file
        # use the input file and assume it will work on any technology
        result = {}
        result['registers'] = float(re.findall("Number of Slice Registers:\s*(\d+)\s*out of\s*\d+\s*\d+\%",benchmarktext)[0])
        result['luts']  = float(re.findall("Number of Slice LUTs:\s*(\d+)\s*out of\s*\d+\s*\d+\%",benchmarktext)[0])
        result['bram']  = float(re.findall("Number of BlockRAM/FIFO:\s*(\d+)\s*out of\s*\d+\s*\d+\%",benchmarktext)[0])
        result['dsp']  = float(re.findall("Number of DSP48Es:\s*(\d+)\s*out of\s*\d+\s*\d+\%",benchmarktext)[0])

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
    def getADCMaximums(platforms, multiplier):
        maximums = {}
        for platform in platforms:
            # ADCs take no resources on an FPGA board
            if platforms[platform].isFPGABoard():
                maximums[platform] = 32/multiplier
            # ADCs cannot be implemented on a differnt board type
            else:
                maximums[platform] = 0
        return maximums
    
    @staticmethod    
    def getPFBWModel(platforms, bandwidth, input_bitwidth, numchannels):
        model = {}
        for platform in platforms:
            if platforms[platform].isFPGABoard():
                bench = CBlock.get_fpga_utilization(benchmark_dir+'fpga/pfb/results/v5sx95t/pfb_%02d_4_2_08_18_cw_map.map'%math.log(numchannels,2))
                model[platform] = platforms[platform].calcPercentUtilization(bench)
            if platforms[platform].platformtype == 'IBOB':
                model[platform] = {'resources':1.1}
            if platforms[platform].platformtype == 'GTX580':
                bench = CBlock.get_gpu_benchmarks(benchmark_dir+'gpu/pfb/results/pfb_4_gtx580_100x',numchannels)
                #print bench['time']
                #Take time required and divide by time allowed
                # 1/bandwidth GHz * number of channels * 10^-6 = time allowed in ms
                bench['time'] = bench['time']/(1/bandwidth*numchannels*math.pow(10,-6))
                model[platform] = bench
        #print model        
        return model
        
    @staticmethod
    #model for 4x fir filters    
    def getPFBModel(platforms, bandwidth, input_bitwidth, numchannels):
        model = {}
        fpga_utlilzation = {'registers': 427., 'luts': 324., 'dsp': 20., 'bram':17.}
        for platform in platforms:
            if platforms[platform].isFPGABoard():
                #benchmark creates 2 parallel firs, multiply by 2 to get resources for 4
                model[platform] = platforms[platform].calcPercentUtilization(fpga_utlilzation)
            if platforms[platform].platformtype == 'GTX580':
                bench = CBlock.get_gpu_benchmarks(benchmark_dir+'gpu/pfb/results/pfb_4_gtx580_100x',numchannels)
                #print bench['time']
                #Take time required and divide by time allowed
                # 1/bandwidth GHz * number of channels * 10^-6 = time allowed in ms
                bench['time'] = 4*bench['time']/(1/bandwidth*numchannels*math.pow(10,-6))
                model[platform] = bench
            if platforms[platform].platformtype == 'DualGTX690':
                bench = CBlock.get_gpu_benchmarks(benchmark_dir+'gpu/pfb/results/pfb_4_gtx580_100x',numchannels)
                #print bench['time']
                #Take time required and divide by time allowed
                # 1/bandwidth GHz * number of channels * 10^-6 = time allowed in ms
                # This platform has 2 boards with 2 chips each so it should take a quarter of the time
                bench['time'] = (4*bench['time']/(1/bandwidth*numchannels*math.pow(10,-6)))/4
                model[platform] = bench
        #print model        
        return model

    @staticmethod    
    def getFFTWModel(platforms, bandwidth, numchannels):
        model = {}
        for platform in platforms:
            if platforms[platform].isFPGABoard():
                bench = CBlock.get_fpga_utilization(benchmark_dir+'fpga/fft/results/v5sx95t/fftw_%02d_2_18_18_cw_map.map'%math.log(numchannels,2))
                model[platform] = platforms[platform].calcPercentUtilization(bench)
            elif platforms[platform].platformtype == 'IBOB':
                model[platform] = {'resources':1.1}
            elif platforms[platform].platformtype == 'GTX580':
                bench = CBlock.get_gpu_benchmarks(benchmark_dir+'gpu/fft/results/c2c_gtx580_100x',numchannels)
                #print bench['time']
                #Take time required and divide by time allowed
                # 1/bandwidth GHz * number of channels * 10^-6 = time allowed in ms
                bench['time'] = bench['time']/(1/bandwidth*numchannels*math.pow(10,-6))
                model[platform] = bench
            elif platforms[platform].platformtype == 'DualGTX690':
                bench = CBlock.get_gpu_benchmarks(benchmark_dir+'gpu/fft/results/c2c_gtx580_100x',numchannels)
                #print bench['time']
                #Take time required and divide by time allowed
                # 1/bandwidth GHz * number of channels * 10^-6 = time allowed in ms
                # This platform has 2 boards with 2 chips each so it should take a quarter of the time
                bench['time'] = (bench['time']/(1/bandwidth*numchannels*math.pow(10,-6)))/4
                model[platform] = bench
        #print model        
        return model
        
    @staticmethod  
    #model for 4x ffts    
    def getFFTModel(platforms, bandwidth, numchannels):
        model = {}
        for platform in platforms:
            if platforms[platform].isFPGABoard():
                bench = CBlock.get_fpga_utilization(benchmark_dir+'fpga/fft/results/v5sx95t/fft_%02d_2_18_18_cw_map.map'%math.log(numchannels,2))
                model[platform] = platforms[platform].calcPercentUtilization(bench)
            elif platforms[platform].platformtype == 'GTX580':
                bench = CBlock.get_gpu_benchmarks(benchmark_dir+'gpu/fft/results/c2c_gtx580_100x',numchannels)
                #print bench['time']
                #Take time required and divide by time allowed
                # 1/bandwidth GHz * number of channels * 10^-6 = time allowed in ms
                bench['time'] = 4*bench['time']/(1/bandwidth*numchannels*math.pow(10,-6))
                model[platform] = bench
        #print model        
        return model
        
    @staticmethod  
    #model for 4x real ffts    
    def getFFTRealModel(platforms, bandwidth, numchannels):
        model = {}
        fpga_utlilzation = {'registers': 6842., 'luts': 5681., 'dsp': 56., 'bram':28.}
        for platform in platforms:
            if platforms[platform].isFPGABoard():
                bench = platforms[platform].calcPercentUtilization(fpga_utlilzation)
                model[platform] = bench
            elif platforms[platform].platformtype == 'GTX580':
                bench = CBlock.get_gpu_benchmarks(benchmark_dir+'gpu/fft/results/r2c_gtx580_100x',numchannels)
                #print bench['time']
                #Take time required and divide by time allowed
                # 1/bandwidth GHz * number of channels * 10^-6 = time allowed in ms
                bench['time'] = 4*bench['time']/(1/bandwidth*numchannels*math.pow(10,-6))
                model[platform] = bench
            elif platforms[platform].platformtype == 'DualGTX690':
                bench = CBlock.get_gpu_benchmarks(benchmark_dir+'gpu/fft/results/r2c_gtx580_100x',numchannels)
                #print bench['time']
                #Take time required and divide by time allowed
                # 1/bandwidth GHz * number of channels * 10^-6 = time allowed in ms
                # This platform has 2 boards with 2 chips each so it should take a quarter of the time
                bench['time'] = (4*bench['time']/(1/bandwidth*numchannels*math.pow(10,-6)))/4
                model[platform] = bench
        #print model        
        return model

    @staticmethod
    def getTransposeModel(platforms,bandwidth, inputdim, outputdim):
        model = {}
        for platform in platforms:
            if platforms[platform].isFPGABoard():
                model[platform] = {'registers': 0.1, 'luts': 0.1, 'dsp': 0, 'bram':0.1}
            elif platforms[platform].isGPUBoard():
                model[platform] = {'time': 1.1}
        return model
        #return {'ROACH': {'registers': 0, 'luts': 0, 'dsp': 0, 'bram':0}, 'GTX580': {'time': 1.1}}

    
    @staticmethod
    def getXEngModel(platforms, subband, nantpol):
        #fpga space model
        #time to process a window is nantpol/bandwidth
        #original benchmark is relative to number of dual pol antennas, need to multiply keys by 2 for accuracy
        fpga_space = {16:{'registers': 2963, 'luts': 2434, 'dsp': 144, 'bram':9}, \
            32:{'registers': 5352, 'luts': 4068, 'dsp': 144, 'bram':12}, \
            64:{'registers': 13300, 'luts': 13231, 'dsp': 272, 'bram':560},
            128:{'registers': 26227, 'luts': 28785, 'dsp': 528, 'bram':2192},
            256:{'registers': 50912, 'luts': 59326, 'dsp': 1040, 'bram':4624}}
        #gtx580_timing_in_s = {16:.15, 32:0.39, 48:0.71, 64:1.17, 96:2.4, 128:4.12, 256:13.11, 512:480.3}
        gtx580_max_bw = {32:0.06914, 64:0.03095, 96:0.01748, 128:0.01069, 192:0.00536, 256:0.00318, 512:0.00087, 1024:0.00023}
        gtx690_max_bw = {32:2*0.07152, 64:2*0.03421, 96:2*0.01982, 128:2*0.01235, 192:2*0.00600, 256:2*0.00365, 512:2*0.00100, 1024:2*0.00027}
        model = {}
        for platform in platforms:
            if platforms[platform].isFPGABoard():
                if nantpol in fpga_space:
                    model[platform] = platforms[platform].calcPercentUtilization(fpga_space[nantpol])
                else:
                    model[platform] = {'registers':1.1, 'luts': 1.1, 'bram':1.1, 'dsp':1.1}
            elif platforms[platform].platformtype == 'GTX580':
                model[platform] = {'time': subband/gtx580_max_bw[nantpol]}
            elif platforms[platform].platformtype == 'DualGTX690':
                # This platform has 2 boards 2x as much bandwidth
                model[platform] = {'time': subband/(2*gtx690_max_bw[nantpol])}
        #print model
        return model

    @staticmethod
    def getVAccModel(platforms, bandwidth, fft_out_bitwidth, accumulation_length):
        return {'ROACH': {'registers': 0.2, 'luts': 0.1, 'dsp': 0.1, 'bram':0}, 'GTX580': {'time': 0.1}, 'IBOB' : {'resources':1.1}}