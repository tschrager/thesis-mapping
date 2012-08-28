from pulp import *
import numpy


prob = LpProblem("Simple test Problem",LpMinimize)

#maxf=128
#maxx=1024
numblocks=2
maxblocks=[128,1024]
maxf=128
maxx=1024
totalblocks=numpy.sum(maxblocks)

platformcost = [20,10]
# fpgacost=20
# gpucost=10

resourcesonplatform=[[0.1,0.5],[0.2,0.25]]
fonplatform =[0.1,0.5]
# fonfpga=0.1
# fongpu=0.50

xonplatform=[0.2,0.25]
# xonfpga=0.2
# xongpu=0.25

numtech=2
numboards=maxf+maxx
#numfpga=36
#numgpu=40
#numfpga=maxf+maxx
#numgpu=maxf+maxx
numdesignsperplatform=2

board_f = numpy.zeros([numtech,numdesignsperplatform,numboards],dtype=object)
board_x = numpy.zeros([numtech,numdesignsperplatform,numboards],dtype=object)
board_isused = numpy.zeros([numtech,numdesignsperplatform,numboards],dtype=object)

design_f = numpy.zeros([numtech,numdesignsperplatform],dtype=object)
design_x = numpy.zeros([numtech,numdesignsperplatform],dtype=object)
lex_order = numpy.zeros([numtech,numdesignsperplatform],dtype=object)
design_isused = numpy.zeros([numtech,numdesignsperplatform],dtype=object)

for currenttech in range(numtech):
    for currentdesign in range(numdesignsperplatform):
        #make sure the design meets its constraints
        design_f[currenttech][currentdesign] = LpVariable('numf_on_'+`currenttech` + '_' + `currentdesign`,0,maxf,LpInteger)
        design_x[currenttech][currentdesign] = LpVariable('numx_on_'+`currenttech` + '_' + `currentdesign`,0,maxx,LpInteger)
        prob+=design_f[currenttech][currentdesign]*fonplatform[currenttech]+design_x[currenttech][currentdesign]*xonplatform[currenttech]<=1
        
        
                
        for currentboard in range(numboards):
            board_f[currenttech][currentdesign][currentboard] = LpVariable('numf_on_'+`currenttech` + '_' + `currentdesign` + '_' + `currentboard`,0,maxf,LpInteger)
            prob+=design_f[currenttech][currentdesign] >= board_f[currenttech][currentdesign][currentboard]
            
            board_x[currenttech][currentdesign][currentboard] = LpVariable('numx_on_'+`currenttech` + '_' + `currentdesign` + '_' + `currentboard`,0,maxx,LpInteger)
            prob+=design_x[currenttech][currentdesign] >= board_x[currenttech][currentdesign][currentboard]
            
            #check if the board is used at all
            board_isused[currenttech][currentdesign][currentboard] = LpVariable('isused_'+`currenttech` + '_' + `currentdesign` + '_' + `currentboard`,0,1,LpInteger)
            prob+=board_isused[currenttech][currentdesign][currentboard]*totalblocks - board_f[currenttech][currentdesign][currentboard] - board_x[currenttech][currentdesign][currentboard] >= 0
            
            #if board is used force the number of blocks to be the same as that of the design
            #prob+=design_f[currenttech][currentdesign] - board_f[currenttech][currentdesign][currentboard] <= maxf - maxf*board_isused[currenttech][currentdesign][currentboard]
            #prob+=design_x[currenttech][currentdesign] - board_x[currenttech][currentdesign][currentboard] <= maxx - maxx*board_isused[currenttech][currentdesign][currentboard]
            
            if(currentboard!=0):
                prob+= board_isused[currenttech][currentdesign][currentboard] <= board_isused[currenttech][currentdesign][currentboard-1]
                
        design_isused[currenttech][currentdesign] = LpVariable('isused_'+`currenttech` + '_' + `currentdesign`,0,1,LpInteger)
        prob+=design_isused[currenttech][currentdesign]*(numboards+1) - lpSum(board_isused[currenttech][currentdesign][k] for k in range(numboards)) >= 0
        
        #impose a lexographical order on designs so they are unique
        lex_order[currenttech][currentdesign] = LpVariable('lex_order'+`currenttech` + '_' + `currentdesign`,0,(maxx+1)*(maxf+1),LpInteger)
        prob+=lex_order[currenttech][currentdesign] == design_f[currenttech][currentdesign]*(maxx+1) + design_x[currenttech][currentdesign]
        if(currentdesign!=0):
            prob+=design_isused[currenttech][currentdesign] <= design_isused[currenttech][currentdesign-1]
            prob+=lex_order[currenttech][currentdesign-1] -1 >= lex_order[currenttech][currentdesign]
  
cost=LpVariable('cost',0,None,LpInteger)
prob+=lpSum(board_f[i][j][k] for i in range(numtech) for j in range(numdesignsperplatform) for k in range(numboards)) >= maxf
prob+=lpSum(board_x[i][j][k] for i in range(numtech) for j in range(numdesignsperplatform) for k in range(numboards)) >= maxx
prob+=lpSum([board_isused[i][j][k]*platformcost[i]  for i in range(numtech) for j in range(numdesignsperplatform) for k in range(numboards)]) == cost
boards_used=LpVariable('boards_used',0,None,LpInteger)
prob+=lpSum([board_isused[i][j][k] for i in range(numtech) for j in range(numdesignsperplatform) for k in range(numboards)]) == boards_used
prob+=boards_used<=totalblocks
prob+=cost

prob.writeLP('test.txt')

#status = prob.solve(GLPK(msg = 0))
#status = prob.solve(CPLEX(msg = 0))
status = prob.solve(GUROBI(msg = 0))
print LpStatus[status]

for v in prob.variables():
    if(v.varValue != 0):
        print v.name, "=", v.varValue      


# fpga_f=range(numdesignsperplatform*numfpga)
# fpga_x=range(numdesignsperplatform*numfpga)
# fpgaisused=range(numdesignsperplatform*numfpga)
# for designnumber in range(numdesignsperplatform):
#     for i in range(numfpga):
#         fpga_f[i]=LpVariable('numf_on_fpga_'+`i`,0,maxf,LpInteger)
#         fpga_x[i]=LpVariable('numx_on_fpga_'+`i`,0,maxx,LpInteger)
#         fpgaisused[i]=LpVariable('fpga_is_used_'+`i`,0,1,LpInteger)
#         # dont use all the resources
#         prob+=fpga_f[i]*fonfpga+fpga_x[i]*xonfpga<=1
#         # determine if this fpga is used
#         prob+=fpgaisused[i]*totalblocks - fpga_f[i] - fpga_x[i] >= 0
#         if(i!=0):
#             prob+=fpgaisused[i-1]>=fpgaisused[i]
#             prob+=fpga_x[i-1]>=fpga_x[i]
#     
# gpu_f=range(numgpu)
# gpu_x=range(numgpu)
# gpuisused=range(numgpu)
# for i in range(numgpu):
#     gpu_f[i]=LpVariable('numf_on_gpu_'+`i`,0,maxf,LpInteger)
#     gpu_x[i]=LpVariable('numx_on_gpu_'+`i`,0,maxx,LpInteger)
#     gpuisused[i]=LpVariable('gpu_is_used_'+`i`,0,1,LpInteger)
#     #dont use all the resources
#     prob+=gpu_f[i]*fongpu+gpu_x[i]*xongpu<=1
#     #determine if this gpu is used
#     prob+=gpuisused[i]*totalblocks - gpu_f[i] - gpu_x[i] >= 0
#     if(i!=0):
#         prob+=gpuisused[i-1]>=gpuisused[i]
#         prob+=gpu_x[i-1]>=gpu_x[i]


