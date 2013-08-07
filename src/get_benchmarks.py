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
    allbenchmarks = re.findall(`size`+"\s+(\d+)\s+\d+\.\d*\s+(\d+\.\d*)\s+\d+\.\d*\s+(\d+\.\d*)\s+\d+\.\d*\s+(\d+)",benchmarktext)
    lastbenchmark = len(allbenchmarks)-1
    print allbenchmarks[lastbenchmark][2]
    result['runtime'] = float(allbenchmarks[lastbenchmark][2])/(100*int(allbenchmarks[lastbenchmark][0]))
    #print allbenchmarks
    return result  
    
def plot_gpu_fft_benchmarks():
    max_n = 20
    runtime = numpy.zeros(max_n)
    for i in range(8,max_n):
        results = get_gpu_benchmarks(benchmark_dir+'gpu/fft/results/c2c_gtx580_100x',2**i)
        #print results
        runtime[i] = results['runtime']
    print runtime
    ind = numpy.arange(max_n)
    
    plt.clf()
    plt.plot(ind,runtime)
    plt.xlim((7,max_n))
    #plt.legend(('registers','luts','bram','dsp'), loc='upper left')
    plt.title('FFT Benchmark on GTX580')
    plt.xlabel('log$_2$(FFT length)')
    plt.ylabel('Runtime (ms)')
    plt.savefig('Figures/fft_gpu_bench.png')
    #plt.show()
    
def plot_gpu_pfb_benchmarks():
    max_n = 20
    runtime = numpy.zeros(max_n)
    for i in range(8,max_n):
        results = get_gpu_benchmarks(benchmark_dir+'gpu/pfb/results/pfb_4_gtx580_100x',2**i)
        #print results
        runtime[i] = results['runtime']
    print runtime
    ind = numpy.arange(max_n)

    plt.clf()
    plt.plot(ind,runtime)
    plt.xlim((7,max_n))
    #plt.legend(('registers','luts','bram','dsp'), loc='upper left')
    plt.title('PFB FIR Benchmark on GTX580')
    plt.xlabel('log$_2$(FFT length)')
    plt.ylabel('Runtime (ms)')
    plt.savefig('Figures/pfb_gpu_bench.png')
    #plt.show()
    #plt.yscale('log')
    #plt.ylabel('Runtime (ms) log scale')
    #plt.savefig('Figures/pfb_gpu_log_bench.png')

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
    plt.title('800 MHz FFT Resource Utilization on Virtex 5 sx95t')
    plt.xlabel('log$_2$(FFT length)')
    plt.ylabel('Utilization (%)')
    plt.savefig('Figures/fft_bench.png')
    
    #plt.yscale('log')
    #plt.bar(ind-2*width,registers/58880,width,color='red')
    #plt.bar(ind-width,luts/58880,width,color='orange')
    #plt.bar(ind,bram/244,width,color='green')
    #plt.bar(ind+width,dsp/640,width,color='blue')
    #plt.ylabel('Utilization (%) log scale')
    #plt.savefig('Figures/pfb_log_bench.png')
    
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
    
    #plt.yscale('log')
    #plt.bar(ind-2*width,registers/58880,width,color='red')
    #plt.bar(ind-width,luts/58880,width,color='orange')
    #plt.bar(ind,bram/244,width,color='green')
    #plt.bar(ind+width,dsp/640,width,color='blue')
    #plt.ylabel('Utilization (%) log scale')
    #plt.savefig('Figures/pfb_log_bench.png')
    #plt.show()
    
    
def autolabel(rects):
    for rect in rects:
        height = rect.get_height()
        plt.text(rect.get_x()+rect.get_width()/2., 1.05*height, '%d'%int(height), \
                ha='center', va='bottom')
 
# plot fft benchmark data
def plot_fft_comparison_benchmarks():
    v5 = numpy.zeros(5)
    v6 = numpy.zeros(5)
    v7 = numpy.zeros(5)
    
    #results = get_fpga_benchmarks(benchmark_dir+'fpga/fft/results/v5sx95t/fftw_15_2_18_18_cw_map.map')
    v5[0] = 10881
    v5[1] = 11358
    v5[2] = 100
    v5[3] = 30
    v5[4] = 60
    
    #results = get_fpga_benchmarks(benchmark_dir+'fpga/fft/results/v6sx475t/fftw_15_2_18_18_cw_map.map')
    v6[0] = 10789
    v6[1] = 9632
    v6[2] = 100
    v6[3] = 30
    v6[4] = 60
    
    #results = get_fpga_benchmarks(benchmark_dir+'fpga/fft/results/v7vx980t/fftw_15_2_18_18_cw_map.map')
    v7[0] = 10788
    v7[1] = 9773 
    v7[2] = 100
    v7[3] = 30
    v7[4] = 60

    width = 0.2 
    ind = numpy.arange(5)
    plt.clf()
    rects1 = plt.bar(ind-2*width,v5,width,color='red')
    #autolabel(rects1)
    plt.bar(ind-width,v6,width,color='orange')
    plt.bar(ind,v7,width,color='green')
    
    strings = ['Registers','LUTs','36k BlockRAM', '18k BlockRAM', 'DSPs']
    plt.xticks(range(5), strings, size='small')

    plt.legend(('Virtex5sx95t','v6','v7'), loc='upper right')
    plt.title('800 MHz FFT Resource Utilization on Virtex 5 sx95t')
    #plt.xlabel('log$_2$(FFT length)')
    plt.ylabel('Usage')
    plt.savefig('Figures/fft_tech_bench.png')   

#get_fpga_benchmarks(benchmark_dir+'fpga/fft/results/v5sx95t/fftw_12_2_18_18_cw_map.map')
#get_gpu_benchmarks(benchmark_dir+'gpu/fft/results/c2c_gtx580_100x',256)
#plot_fft_benchmarks()
#plot_pfb_benchmarks()
#plot_gpu_fft_benchmarks()
#plot_gpu_pfb_benchmarks()
plot_fft_comparison_benchmarks()


