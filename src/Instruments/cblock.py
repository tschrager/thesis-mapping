import re
import os
import math


gitrepo_dir = os.environ.get('GIT_REPOS')
benchmark_dir = gitrepo_dir+'/thesis-benchmarks/'

class CBlock:
    def __init__(self, resourcearray, inputfrom, inputconnection, inputbw, outputto, outputconnection, outputbw, numblocks):
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
            if platforms[platform].instrumenttype == 'GPU':
                bench = CBlock.get_gpu_benchmarks(benchmark_dir+'gpu/fft/results/c2c_gtx580_100x',numchannels)
                #print bench['time']
                #Take time required and divide by time allowed
                # 1/bandwidth GHz * number of channels * 10^-6 = time allowed in ms
                bench['time'] = bench['time']/(1/bandwidth*numchannels*math.pow(10,-6))
                model[platform] = bench
        #print model        
        return model

    @staticmethod
    def getXEngModel(platforms):
        return {'ROACH': {'registers': 0.9, 'luts': 0.1, 'dsp': 0.1, 'bram':0.4}, 'GPU': {'time': 0.25}}

    @staticmethod
    def getVAccModel(platforms, bandwidth, fft_out_bitwidth, accumulation_length):
        return {'ROACH': {'registers': 0.2, 'luts': 0.1, 'dsp': 0.1, 'bram':0}, 'GPU': {'time': 0.1}}