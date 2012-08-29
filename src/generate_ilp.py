from pulp import *
import numpy

prob = LpProblem("Simple test Problem",LpMinimize)

numplatforms = 2

#design pfb, fft, xeng
blocktypes = 3
numblocks = numpy.array([128,128,1024])
blockresourcesonplatform = numpy.array([[0.1,0.5],[0.1,0.5],[0.2,0.25]])

#design pfb, fft, xeng
blocktypes = 5
numblocks = numpy.array([128,128,128,128,1024])
blockresourcesonplatform = numpy.array([[0.1,0.5],[0.1,0.5],[0.1,0.5],[0.1,0.5],[0.2,0.25]])

#design fft, xeng
# blocktypes = 2
# numblocks = numpy.array([128,1024])
# blockresourcesonplatform = numpy.array([[0.1,0.5],[0.2,0.25]])


totalblocks = sum(numblocks)
numboards = totalblocks

platformcosts = numpy.array([20,10])


board_blocks = numpy.zeros([blocktypes,numplatforms,numboards],dtype=object)
board_isused = numpy.zeros([numplatforms,numboards],dtype=object)
lex_order = numpy.zeros([numplatforms,numboards],dtype=object)

multipliers = numpy.zeros([blocktypes],dtype=object)
maxblockperplatform = numpy.zeros([blocktypes],dtype=object)

for blocktype in range(0,blocktypes):
    for currentplatform in range(numplatforms):
        if 1/blockresourcesonplatform[blocktype,currentplatform] > maxblockperplatform[blocktype]:
            maxblockperplatform[blocktype] = numpy.floor(1/blockresourcesonplatform[blocktype,currentplatform])
    if blocktype == 0:
        multipliers[blocktype] = 1
    else:
        multipliers[blocktype] = multipliers[blocktype-1]*(numblocks[blocktype-1]+1)

for currentplatform in range(numplatforms):
    for currentboard in range(numboards):
        unique_id = `currentplatform`+'_'+`currentboard`
        board_isused[currentplatform,currentboard]=LpVariable('is_used_'+unique_id,0,1,LpInteger)
        for blocktype in range(blocktypes):
            #board_blocks[blocktype,currentplatform,currentboard]=LpVariable('num' + `blocktype` + '_on_' + unique_id,0,maxblockperplatform[blocktype],LpInteger)
            board_blocks[blocktype,currentplatform,currentboard]=LpVariable('num' + `blocktype` + '_on_' + unique_id,0,numblocks[blocktype],LpInteger)
        prob += lpSum(board_blocks[blocktype,currentplatform,currentboard]*blockresourcesonplatform[blocktype,currentplatform] for blocktype in range(blocktypes)) <= 1
        prob += board_isused[currentplatform,currentboard]*totalblocks - lpSum(board_blocks[blocktype,currentplatform,currentboard] for blocktype in range(blocktypes)) >= 0
        
        # impose an ordering on the boards, this doesn't do anything to the solution, just breaks some of the symmetry
        #lex_order[currentplatform,currentboard]=LpVariable('lex_order_'+unique_id,0,(maxblockperplatform+1).prod(),LpInteger)
        lex_order[currentplatform,currentboard]=LpVariable('lex_order_'+unique_id,0,(numblocks+1).prod(),LpInteger)
        prob+=lex_order[currentplatform,currentboard] == lpSum(board_blocks[blocktype,currentplatform,currentboard]*multipliers[blocktype] for blocktype in range(blocktypes))
        if(currentboard!=0):
            prob+=board_isused[currentplatform,currentboard-1]>=board_isused[currentplatform,currentboard]
            prob+=lex_order[currentplatform,currentboard-1]>=lex_order[currentplatform,currentboard]
            

for blocktype in range(blocktypes):
    prob+=lpSum(board_blocks[blocktype,currentplatform,currentboard] for currentplatform in range(numplatforms) for currentboard in range(numboards)) >= numblocks[blocktype]

cost=LpVariable('cost',0,None,LpInteger)
prob+=lpSum(board_isused[currentplatform,currentboard]*platformcosts[currentplatform] for currentplatform in range(numplatforms) for currentboard in range(numboards)) == cost
#boards_used=LpVariable('boards_used',0,None,LpInteger)
#prob+=lpSum([fpgaisused[i] for i in range(numfpga)]) + lpSum([gpuisused[i] for i in range(numgpu)]) == boards_used
prob+=cost

prob.writeLP('test_generate_ilp.txt')

status = prob.solve(GUROBI(msg = 0))
print LpStatus[status]

for v in prob.variables():
    if(v.varValue != 0):
        print v.name, "=", v.varValue