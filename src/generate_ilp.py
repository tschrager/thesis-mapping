#!/usr/bin/python2.6

from pulp import *
import numpy



numplatforms = 2

#design pfb, fft, xeng
# blocktypes = 5
# numblocks = numpy.array([128,128,128,128,128])
# blockresourcesonplatform = numpy.array([[0.1,0.5],[0.1,0.5],[0.1,0.5],[0.1,0.5],[0.2,0.25]])

#design fft, xeng
# blocktypes = 2
# numblocks = numpy.array([128,1024])
# blockresourcesonplatform = numpy.array([[0.1,0.5],[0.2,0.25]])

#design pfb, fft, xeng
#blocktypes = 3
numblocks = numpy.array([16,16,16])

blockresourcesonplatform = numpy.array([[0.1,0.5],[0.1,0.5],[0.9,0.25]])

inputfrom = [-1,0,1]
inputconnection = [0,0,1]
blockinputbw = [0,6.4,6.4]

outputto = [1,2,-1]
outputconnection = [0,1,0]
blockoutputbw = [6.4,6.4,0]

platforminputbw = [10,10]
platformoutputbw = [40,1]

totalblocks = sum(numblocks)
numboards = totalblocks

platformcosts = numpy.array([20,10])



def generate_ILP():
    prob = LpProblem("Simple test Problem",LpMinimize)
    
    blocktypes = numblocks.size
    
    #initialize arrays for ILP variables
    #represnt the number of <blocktype> on board <platform,board>
    board_blocks = numpy.zeros([blocktypes,numplatforms,numboards],dtype=object)
    #represnt the number of blocks with type <blocktype> on board <platform,board> that need to receive data
    num_receive_data = numpy.zeros([blocktypes,numplatforms,numboards],dtype=object)
    #represnt the number of blocks with type <blocktype> on board <platform,board> that need to send data
    num_send_data = numpy.zeros([blocktypes,numplatforms,numboards],dtype=object)
    #determine if board <platform,board> is used (has computation blocks assigned to it)
    board_isused = numpy.zeros([numplatforms,numboards],dtype=object)
    #force the boards to fill in a certain order (to reduce symmetry in the design)
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
                board_blocks[blocktype,currentplatform,currentboard]=LpVariable('num' + `blocktype` + '_on_' + unique_id,0,numblocks[blocktype],LpInteger)
            
            # check that we don't overuse resources on the platform
            prob += lpSum(board_blocks[blocktype,currentplatform,currentboard]*blockresourcesonplatform[blocktype,currentplatform] for blocktype in range(blocktypes)) <= 1
        
            #determine if this board is used
            prob += board_isused[currentplatform,currentboard]*totalblocks - lpSum(board_blocks[blocktype,currentplatform,currentboard] for blocktype in range(blocktypes)) >= 0
        
            #add in network constrains
            for blocktype in range(blocktypes):
                num_receive_data[blocktype,currentplatform,currentboard]=LpVariable('rcv' + `blocktype` + '_on_' + unique_id,0,numblocks[blocktype],LpInteger)
                num_send_data[blocktype,currentplatform,currentboard]=LpVariable('send' + `blocktype` + '_on_' + unique_id,0,numblocks[blocktype],LpInteger)
            
                #for constraints on receiving data
                #check that this isn't a source
                if inputfrom[blocktype]!=-1:
                    receivingfrom=inputfrom[blocktype]
                    #if this is a 1 to 1 connection, just see how many blocks need to receive data
                    if inputconnection[blocktype]==0:
                        #at least this much data needs to go over the network
                        prob += num_receive_data[blocktype,currentplatform,currentboard] >= board_blocks[blocktype,currentplatform,currentboard] - board_blocks[receivingfrom,currentplatform,currentboard]
                    #this is a all to 1 connection, receive *all* data over the network
                    #TODO: add when any blocks we are communicating with reside on a different platform
                    else:
                        prob += num_receive_data[blocktype,currentplatform,currentboard] == board_blocks[blocktype,currentplatform,currentboard]
                        #prob += numblocks[receivingfrom] - board_blocks[receivingfrom,currentplatform,currentboard] < numblocks[blocktype]*num_receive_data[blocktype,currentplatform,currentboard]

                #for constraints on sending data
                #check that this isn't a sink
                if outputto[blocktype]!=-1:
                    sendingto=outputto[blocktype]
                    #if this is a 1 to 1 connection, just see how many blocks need to send data
                    if outputconnection[blocktype]==0:
                        #at least this much data needs to go over the network
                        prob += num_send_data[blocktype,currentplatform,currentboard] >= board_blocks[blocktype,currentplatform,currentboard] - board_blocks[sendingto,currentplatform,currentboard]
                    #this is a 1 to all connection, send *all* data over the network
                    #TODO: when any blocks we are communicating with reside on a different platform
                    else:
                        prob += num_send_data[blocktype,currentplatform,currentboard] == board_blocks[blocktype,currentplatform,currentboard]
                        #prob += numblocks[receivingfrom] - board_blocks[receivingfrom,currentplatform,currentboard] < numblocks[blocktype]*num_receive_data[blocktype,currentplatform,currentboard]
                    
                
            
            #check that we don't exceed the input/output bandwidth
            prob += lpSum(blockinputbw[blocktype]*num_receive_data[blocktype,currentplatform,currentboard] for blocktype in range(blocktypes)) <= platforminputbw[currentplatform]
            prob += lpSum(blockoutputbw[blocktype]*num_send_data[blocktype,currentplatform,currentboard] for blocktype in range(blocktypes)) <= platformoutputbw[currentplatform]
        
            # impose an ordering on the boards, this doesn't do anything to the solution, just breaks some of the symmetry
            #lex_order[currentplatform,currentboard]=LpVariable('lex_order_'+unique_id,0,(maxblockperplatform+1).prod(),LpInteger)
            lex_order[currentplatform,currentboard]=LpVariable('lex_order_'+unique_id,0,(numblocks+1).prod(),LpInteger)
            prob+=lex_order[currentplatform,currentboard] == lpSum(board_blocks[blocktype,currentplatform,currentboard]*multipliers[blocktype] for blocktype in range(blocktypes))
            if(currentboard!=0):
                prob+=board_isused[currentplatform,currentboard-1]>=board_isused[currentplatform,currentboard]
                prob+=lex_order[currentplatform,currentboard-1]>=lex_order[currentplatform,currentboard]
            
    #check that all blocks are allocated
    for blocktype in range(blocktypes):
        prob+=lpSum(board_blocks[blocktype,currentplatform,currentboard] for currentplatform in range(numplatforms) for currentboard in range(numboards)) == numblocks[blocktype]

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
            
generate_ILP()
