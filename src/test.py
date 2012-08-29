from pulp import *
import numpy


prob = LpProblem("Simple test Problem",LpMinimize)

# maxf=128
# maxx=1024
maxf=128
maxx=1024
totalblocks=maxf+maxx

fpgacost=20
gpucost=10

fongpu=0.50
xongpu=0.25

fonfpga=0.1
xonfpga=0.2

numtech=2
#numfpga=36
#numgpu=40
numfpga=maxf+maxx
numgpu=maxf+maxx
#numdesignsperplatform=2

fpga_lex_order = numpy.zeros(numfpga,dtype=object)
fpga_f=range(numfpga)
fpga_x=range(numfpga)
fpgaisused=range(numfpga)
for i in range(numfpga):
    fpga_f[i]=LpVariable('numf_on_fpga_'+`i`,0,maxf,LpInteger)
    fpga_x[i]=LpVariable('numx_on_fpga_'+`i`,0,maxx,LpInteger)
    fpgaisused[i]=LpVariable('fpga_is_used_'+`i`,0,1,LpInteger)
    # dont use all the resources
    prob+=fpga_f[i]*fonfpga+fpga_x[i]*xonfpga<=1
    # determine if this fpga is used
    prob+=fpgaisused[i]*totalblocks - fpga_f[i] - fpga_x[i] >= 0
    fpga_lex_order[i]=LpVariable('fpga_lex_order'+`i`,0,(maxf+1)*(maxx+1),LpInteger)
    prob+=fpga_lex_order[i] == fpga_x[i]*(maxf+1) + fpga_f[i]
    if(i!=0):
        prob+=fpgaisused[i-1]>=fpgaisused[i]
        prob+=fpga_lex_order[i-1]>=fpga_lex_order[i]
    
gpu_lex_order = numpy.zeros(numgpu,dtype=object)
gpu_f=range(numgpu)
gpu_x=range(numgpu)
gpuisused=range(numgpu)
for i in range(numgpu):
    gpu_f[i]=LpVariable('numf_on_gpu_'+`i`,0,maxf,LpInteger)
    gpu_x[i]=LpVariable('numx_on_gpu_'+`i`,0,maxx,LpInteger)
    gpuisused[i]=LpVariable('gpu_is_used_'+`i`,0,1,LpInteger)
    #dont use all the resources
    prob+=gpu_f[i]*fongpu+gpu_x[i]*xongpu<=1
    #determine if this gpu is used
    prob+=gpuisused[i]*totalblocks - gpu_f[i] - gpu_x[i] >= 0
    gpu_lex_order[i]=LpVariable('gpu_lex_order'+`i`,0,(maxf+1)*(maxx+1),LpInteger)
    #prob+=gpu_lex_order[i] == gpu_x[i]*(maxf+1) + gpu_f[i]
    prob+=gpu_lex_order[i] == gpu_x[i] + gpu_f[i]*(maxx+1)
    if(i!=0):
        prob+=gpuisused[i-1]>=gpuisused[i]
        #prob+=gpu_x[i-1]>=gpu_x[i]
        prob+=gpu_lex_order[i-1]>=gpu_lex_order[i]

cost=LpVariable('cost',0,None,LpInteger)
prob+=lpSum(fpga_f[i] for i in range(numfpga)) + lpSum(gpu_f[i] for i in range(numgpu)) == maxf
prob+=lpSum(fpga_x[i] for i in range(numfpga)) + lpSum(gpu_x[i] for i in range(numgpu)) == maxx
prob+=lpSum([fpgaisused[i]*fpgacost for i in range(numfpga)]) + lpSum([gpuisused[i]*gpucost for i in range(numgpu)]) == cost
boards_used=LpVariable('boards_used',0,None,LpInteger)
prob+=lpSum([fpgaisused[i] for i in range(numfpga)]) + lpSum([gpuisused[i] for i in range(numgpu)]) == boards_used
prob+=cost

prob.writeLP('test_test.txt')

#status = prob.solve(GLPK(msg = 0))
#status = prob.solve(CPLEX(msg = 0))
#status = prob.solve(GUROBI(dict(symmetry=2),msg = 0))
status = prob.solve(GUROBI(msg = 0))
print LpStatus[status]

for v in prob.variables():
    if(v.varValue != 0):
        print v.name, "=", v.varValue
