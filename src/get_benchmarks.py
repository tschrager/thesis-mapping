import re
import os
import numpy
from matplotlib import pyplot as plt

gitrepo_dir =os.environ.get('GIT_REPOS')
benchmark_dir = gitrepo_dir+'/thesis-benchmarks/'

# reads in data from map file
def get_fpga_benchmarks(filename):
    benchmarkfile = open(filename,'r')
    benchmarktext = benchmarkfile.read()
    benchmarkfile.close()
    
    # remove commas in numbers
    benchmarktext = benchmarktext.replace(",","")
    
    # find numbers in map file
    result = {}
    result['registers'] = re.findall("Number of Slice Registers:\s*(\d+)\s*out of\s*\d+\s*\d+\%",benchmarktext)[0]
    result['luts']  = re.findall("Number of Slice LUTs:\s*(\d+)\s*out of\s*\d+\s*\d+\%",benchmarktext)[0]
    result['bram']  = re.findall("Number of BlockRAM/FIFO:\s*(\d+)\s*out of\s*\d+\s*\d+\%",benchmarktext)[0]
    result['dsp']  = re.findall("Number of DSP48Es:\s*(\d+)\s*out of\s*\d+\s*\d+\%",benchmarktext)[0]
    
    
    return result
    
# reads in data from gpu results file
def get_gpu_benchmarks(filename,size):
    benchmarkfile = open(filename,'r')
    benchmarktext = benchmarkfile.read()
    benchmarkfile.close()
    
    result = {}
    #check the regex...
    result['runtime'] = re.findall(`size`+"\s*(\d+(\.\d*)?)",benchmarktext)
    print result   

# plot fft benchmark data
def plot_fft_benchmarks():
    max_n = 16
    registers = numpy.zeros(max_n)
    luts = numpy.zeros(max_n)
    bram = numpy.zeros(max_n)
    dsp = numpy.zeros(max_n)
    for i in range(5,max_n):
        results = get_fpga_benchmarks(benchmark_dir+'fpga/fft/results/v5sx95t/fftw_%02d_2_18_18_cw_map.map'%i)
        registers[i] = results['registers']
        luts[i] = results['luts']
        bram[i] = results['bram']
        dsp[i] = results['dsp']
    
    width = 0.2 
    ind = numpy.arange(max_n)
    plt.clf()
    plt.bar(ind-2*width,registers/58880,width,color='red')
    plt.bar(ind-width,luts/58880,width,color='orange')
    plt.bar(ind,bram/244,width,color='green')
    plt.bar(ind+width,dsp/640,width,color='blue')
    
    plt.legend(('registers','luts','bram','dsp'), loc='upper left')
    plt.title('')
    plt.xlabel('log$_2$(FFT length)')
    plt.ylabel('Utilization (%)')
    plt.savefig('Figures/fft_bench.png')
    
    #plt.show()
    
#plot pfb benchmark data
def plot_pfb_benchmarks():
    max_n = 16
    registers = numpy.zeros(max_n)
    luts = numpy.zeros(max_n)
    bram = numpy.zeros(max_n)
    dsp = numpy.zeros(max_n)
    for i in range(6,max_n):
        results = get_fpga_benchmarks(benchmark_dir+'fpga/pfb/results/v5sx95t/pfb_%02d_4_2_08_18_cw_map.map'%i)
        registers[i] = results['registers']
        luts[i] = results['luts']
        bram[i] = results['bram']
        dsp[i] = results['dsp']
    
    width = 0.2 
    ind = numpy.arange(max_n)
    plt.clf()
    plt.bar(ind-2*width,registers/58880,width,color='red')
    plt.bar(ind-width,luts/58880,width,color='orange')
    plt.bar(ind,bram/244,width,color='green')
    plt.bar(ind+width,dsp/640,width,color='blue')
    
    plt.legend(('registers','luts','bram','dsp'), loc='upper left')
    plt.title('')
    plt.xlabel('log$_2$(FFT length)')
    plt.ylabel('Utilization (%)')
    
    plt.savefig('Figures/pfb_bench.png')
    #plt.show()
    

#get_fpga_benchmarks(benchmark_dir+'fpga/fft/results/v5sx95t/fftw_12_2_18_18_cw_map.map')
#get_gpu_benchmarks(benchmark_dir+'gpu/fft/results/c2c_gtx580_100x',256)
plot_fft_benchmarks()
plot_pfb_benchmarks()


