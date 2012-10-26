from pulp import *
import numpy

class Instrument:   
    def runILP(self):
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
            multipliers[blocktype] = 0
            #maxblockperplatform[blocktype] = 0
            #for currentplatform in self.platforms:
            #    if 1/self.blocks[blocktype].resources[currentplatform] > maxblockperplatform[blocktype]:
            #        maxblockperplatform[blocktype] = numpy.floor(1/self.blocks[blocktype].resources[currentplatform] )
            multipliers[blocktype] = nextmult
            nextmult = multipliers[blocktype]*(self.blocks[blocktype].numblocks+1)
            # if blocktype == 0:
            #     multipliers[blocktype] = 1
            # else:
            #     multipliers[blocktype] = multipliers[blocktype-1]*(numblocks[blocktype-1]+1)
        maxlexorder = nextmult
        #print multipliers
        #print maxlexorder
        
        for currentplatform in self.platforms:
            board_isused[currentplatform] = numpy.zeros([numboards],dtype=object)
            lex_order[currentplatform] = numpy.zeros([numboards],dtype=object)
            for currentboard in range(numboards):
                unique_id = `currentplatform`+'_'+`currentboard`
                board_isused[currentplatform][currentboard]=LpVariable('is_used_'+unique_id,0,1,LpInteger)
                for blocktype in self.blocks:
                    board_blocks[(blocktype,currentplatform,currentboard)]=LpVariable('num' + `blocktype` + '_on_' + unique_id,0,self.blocks[blocktype].numblocks,LpInteger)

                # check that we don't overuse resources on the platform
                prob += lpSum(board_blocks[(blocktype,currentplatform,currentboard)]*self.blocks[blocktype].resources[currentplatform] for blocktype in self.blocks) <= 1

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
                lex_order[currentplatform,currentboard]=LpVariable('lex_order_'+unique_id,0,maxlexorder,LpInteger)
                prob+=lex_order[currentplatform,currentboard] == lpSum(board_blocks[(blocktype,currentplatform,currentboard)]*multipliers[blocktype] for blocktype in self.blocks)
                if(currentboard!=0):
                    prob+=board_isused[currentplatform][currentboard-1]>=board_isused[currentplatform][currentboard]
                    prob+=lex_order[currentplatform][currentboard-1]>=lex_order[currentplatform][currentboard]

        #check that all blocks are allocated
        for blocktype in self.blocks:
            prob+=lpSum(board_blocks[(blocktype,currentplatform,currentboard)] for currentplatform in self.platforms for currentboard in range(numboards)) == self.blocks[blocktype].numblocks

        cost=LpVariable('cost',0,None,LpInteger)
        prob+=lpSum(board_isused[currentplatform][currentboard]*self.platforms[currentplatform].cost for currentplatform in self.platforms for currentboard in range(numboards)) == cost
        #boards_used=LpVariable('boards_used',0,None,LpInteger)
        #prob+=lpSum([fpgaisused[i] for i in range(numfpga)]) + lpSum([gpuisused[i] for i in range(numgpu)]) == boards_used
        prob+=cost

        prob.writeLP('test_generate_ilp.txt')

        status = prob.solve(GUROBI(msg = 0))
        print LpStatus[status]

        for v in prob.variables():
            if(v.varValue != 0):
                print v.name, "=", v.varValue
    