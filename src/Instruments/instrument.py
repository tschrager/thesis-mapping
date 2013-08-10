from pulp import *
import numpy
from gurobipy import *
import time

class Instrument:   
    def runILP(self):
        starttime = time.time()
        prob = LpProblem("Simple test Problem",LpMinimize)

        blocktypes = len(self.blocks)
        numplatforms = len(self.platforms)
        numboards = self.totalblocks
        

        #initialize arrays for ILP variables
        #represnt the number of <blocktype> on board <platform,board>
        #board_blocks = numpy.zeros([blocktypes,numplatforms,numboards],dtype=object)
        board_blocks = {}
        #represnt the number of blocks with type <blocktype> on board <platform,board> that need to receive data
        #num_receive_data = numpy.zeros([blocktypes,numplatforms,numboards],dtype=object)
        num_receive_data = {}
        #represnt the number of blocks with type <blocktype> on board <platform,board> that need to send data
        #num_send_data = numpy.zeros([blocktypes,numplatforms,numboards],dtype=object)
        num_send_data = {}
        #determine if board <platform,board> is used (has computation blocks assigned to it)
        #board_isused = numpy.zeros([numplatforms,numboards],dtype=object)
        board_isused = {}
        total_used = {}
        #force the boards to fill in a certain order (to reduce symmetry in the design)
        #lex_order = numpy.zeros([numplatforms,numboards],dtype=object)
        lex_order = {}
        

        #multipliers = numpy.zeros([blocktypes],dtype=object)
        multipliers = {}
        #maxblockperplatform = numpy.zeros([blocktypes],dtype=object)
        maxblockperplatform = {}

        nextmult = 1
        for blocktype in self.blocks:
            #print blocktype
            if blocktype not in multipliers:
                totalblocks = 0
                for otherblocktypes in self.blocks:
                    if self.blocks[blocktype].algname==self.blocks[otherblocktypes].algname:
                        multipliers[otherblocktypes] = nextmult
                        totalblocks = totalblocks + self.blocks[otherblocktypes].numblocks

                nextmult = multipliers[blocktype]*(totalblocks+1)
            
        maxlexorder = nextmult
        #print multipliers
        #print maxlexorder
        #print multipliers
        
        for currentplatform in self.platforms:
            board_isused[currentplatform] = numpy.zeros([numboards],dtype=object)
            lex_order[currentplatform] = numpy.zeros([numboards],dtype=object)
            
            for currentboard in range(numboards):
                unique_id = `currentplatform`+'_'+`currentboard`
                board_isused[currentplatform][currentboard]=LpVariable('is_used_'+unique_id,0,1,LpInteger)
                for blocktype in self.blocks:
                    board_blocks[(blocktype,currentplatform,currentboard)]=LpVariable('num' + `blocktype` + '_on_' + unique_id,0,self.blocks[blocktype].numblocks,LpInteger)
                    #if(currentboard!=0 and self.maxdesigns == 1):
                    #    prob += board_blocks[(blocktype,currentplatform,currentboard)] == board_blocks[(blocktype,currentplatform,currentboard-1)]

                # check that we don't overuse resources on the platform
                for currentresource in self.platforms[currentplatform].resources:
                    prob += lpSum(board_blocks[(blocktype,currentplatform,currentboard)]*self.blocks[blocktype].resources[currentplatform][currentresource] for blocktype in self.blocks) <= 1

                #determine if this board is used
                prob += board_isused[currentplatform][currentboard]*self.totalblocks - lpSum(board_blocks[(blocktype,currentplatform,currentboard)] for blocktype in self.blocks) >= 0

                #add in network constrains
                for blocktype in self.blocks:
                    num_receive_data[(blocktype,currentplatform,currentboard)]=LpVariable('rcv' + `blocktype` + '_on_' + unique_id,0,self.blocks[blocktype].numblocks,LpInteger)
                    num_send_data[(blocktype,currentplatform,currentboard)]=LpVariable('send' + `blocktype` + '_on_' + unique_id,0,self.blocks[blocktype].numblocks,LpInteger)

                    #for constraints on receiving data
                    #check that this isn't a source
                    if self.blocks[blocktype].inputfrom!=-1:
                        receivingfrom=self.blocks[blocktype].inputfrom
                        #if this is a 1 to 1 connection, just see how many blocks need to receive data
                        if self.blocks[blocktype].inputconnection==0:
                            #at least this much data needs to go over the network
                            prob += num_receive_data[(blocktype,currentplatform,currentboard)] >= board_blocks[(blocktype,currentplatform,currentboard)] - board_blocks[(receivingfrom,currentplatform,currentboard)]
                        #this is a all to 1 connection, receive *all* data over the network
                        #TODO: add when any blocks we are communicating with reside on a different platform
                        else:
                            prob += num_receive_data[(blocktype,currentplatform,currentboard)] == board_blocks[(blocktype,currentplatform,currentboard)]
                            #prob += numblocks[receivingfrom] - board_blocks[receivingfrom,currentplatform,currentboard] < numblocks[blocktype]*num_receive_data[blocktype,currentplatform,currentboard]

                    #for constraints on sending data
                    #check that this isn't a sink
                    if self.blocks[blocktype].outputto!=-1:
                        sendingto=self.blocks[blocktype].outputto
                        #if this is a 1 to 1 connection, just see how many blocks need to send data
                        if self.blocks[blocktype].outputconnection==0:
                            #at least this much data needs to go over the network
                            prob += num_send_data[(blocktype,currentplatform,currentboard)] >= board_blocks[(blocktype,currentplatform,currentboard)] - board_blocks[(sendingto,currentplatform,currentboard)]
                        #this is a 1 to all connection, send *all* data over the network
                        #TODO: when any blocks we are communicating with reside on a different platform
                        else:
                            prob += num_send_data[(blocktype,currentplatform,currentboard)] == board_blocks[(blocktype,currentplatform,currentboard)]
                            #prob += numblocks[receivingfrom] - board_blocks[receivingfrom,currentplatform,currentboard] < numblocks[blocktype]*num_receive_data[blocktype,currentplatform,currentboard]



                #check that we don't exceed the input/output bandwidth
                prob += lpSum(self.blocks[blocktype].inputbw*num_receive_data[blocktype,currentplatform,currentboard] for blocktype in self.blocks) <= self.platforms[currentplatform].inputbw
                prob += lpSum(self.blocks[blocktype].outputbw*num_send_data[blocktype,currentplatform,currentboard] for blocktype in self.blocks) <= self.platforms[currentplatform].outputbw

                # impose an ordering on the boards, this doesn't do anything to the solution, just breaks some of the symmetry
                #lex_order[currentplatform,currentboard]=LpVariable('lex_order_'+unique_id,0,(maxblockperplatform+1).prod(),LpInteger)
                lex_order[currentplatform][currentboard]=LpVariable('lex_order_'+unique_id,0,maxlexorder,LpInteger)
                prob+=lex_order[currentplatform][currentboard] == lpSum(board_blocks[(blocktype,currentplatform,currentboard)]*multipliers[blocktype] for blocktype in self.blocks)
                
                if(currentboard!=0):
                    prob+=lex_order[currentplatform][currentboard-1]>=lex_order[currentplatform][currentboard]
                    prob+=board_isused[currentplatform][currentboard-1]>=board_isused[currentplatform][currentboard]
                    if(self.maxdesigns != 0):  
                        prob+=lex_order[currentplatform][currentboard] - lex_order[currentplatform][currentboard-1] >= maxlexorder * (board_isused[currentplatform][currentboard]-1)
            
            total_used[currentplatform] = LpVariable('total_'+currentplatform,0,numboards,LpInteger)
            prob+=lpSum(board_isused[currentplatform][currentboard] for currentboard in range(numboards)) == total_used[currentplatform] 
            
            
        #check that all blocks are allocated
        for blocktype in self.blocks:
            prob+=lpSum(board_blocks[(blocktype,currentplatform,currentboard)] for currentplatform in self.platforms for currentboard in range(numboards)) >= self.blocks[blocktype].numblocks
            # force blocks to be implemented on a single platform
            if(self.singleimplementation==1):
                block_is_on={}
                for currentplatform in self.platforms:
                    block_is_on[(blocktype,currentplatform)]=LpVariable(`blocktype` + '_is_on_' + currentplatform,0,1,LpInteger)
                    prob+=lpSum(board_blocks[(blocktype,currentplatform,currentboard)] for currentboard in range(numboards)) <= 2*self.blocks[blocktype].numblocks*block_is_on[(blocktype,currentplatform)]
                prob+=lpSum(block_is_on[(blocktype,currentplatform)] for currentplatform in self.platforms) == 1
                
                    

        cost=LpVariable('cost',0,None,LpInteger)
        prob+=lpSum(board_isused[currentplatform][currentboard]*self.platforms[currentplatform].cost for currentplatform in self.platforms for currentboard in range(numboards)) == cost
        #boards_used=LpVariable('boards_used',0,None,LpInteger)
        #prob+=lpSum([fpgaisused[i] for i in range(numfpga)]) + lpSum([gpuisused[i] for i in range(numgpu)]) == boards_used
        prob+=cost

        #prob+=board_blocks[('ADC0','ROACH',0)]==1

        prob.writeLP('test_generate_ilp.txt')

        #grb = solvers.GUROBI()
        #grbmodel = grb.buildSolverModel(prob)
        #grbmodel.optimize()
        status = prob.solve(GUROBI(msg = 0))
        print LpStatus[status]
        endtime = time.time()

        totalused = {}
        cost = 0
        for currentplatform in self.platforms:
            totalused[currentplatform] = 0
        for v in prob.variables():
            #if(v.varValue != 0 and ('num' in v.name or 'cost' in v.name or 'different' in v.name or 'lex' in v.name or 'is_used' in v.name)):
            #if(v.varValue != 0):
            if(v.varValue != 0 and ('total' in v.name or 'cost' in v.name or 'is_used' in v.name or 'is_on' in v.name)):
                print v.name, "=", v.varValue
            if('cost' in v.name):
                cost = v.varValue/1000
            if('total' in v.name):
                totalused[v.name.split('_')[1]] = v.varValue

                        

                
        return '\\begin{tabular}{c} %d GPUs \\\\ %d ROACH \\\\ \\$%.1fk \\\\ %.2f seconds \\end{tabular}'%(totalused['GPU'],totalused['ROACH'],cost,(endtime-starttime))
    