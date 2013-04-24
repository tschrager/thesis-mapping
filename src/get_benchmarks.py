import re
import os

gitrepo_dir =os.environ.get('GIT_REPOS')
benchmark_dir = gitrepo_dir+'/thesis-benchmarks/'

def get_fpga_benchmarks(filename):
    benchmarkfile = open(filename,'r')
    benchmarktext = benchmarkfile.read()
    benchmarkfile.close()
    result = {}
    benchmarktext = benchmarktext.replace(",","")
    result['registers'] = re.findall("Number of Slice Registers:\s*(\d+)\s*out of\s*\d+\s*\d+\%",benchmarktext)
    result['luts']  = re.findall("Number of Slice LUTs:\s*(\d+)\s*out of\s*\d+\s*\d+\%",benchmarktext)
    result['bram']  = re.findall("Number of BlockRAM/FIFO:\s*(\d+)\s*out of\s*\d+\s*\d+\%",benchmarktext)
    result['dsp']  = re.findall("Number of DSP48Es:\s*(\d+)\s*out of\s*\d+\s*\d+\%",benchmarktext)
    print result



get_fpga_benchmarks(benchmark_dir+'fpga/fft/results/v5sx95t/fftw_12_2_18_18_cw_map.map')


