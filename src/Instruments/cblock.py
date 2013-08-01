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
        
    @staticmethod
    def getADCModel(platforms):
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
        
    def getPFBModel(platforms):
        model = {}
        for platform in platforms:
            model[platform] = {}
            for resource in platforms[platform].resources:
                model[platform][resource] = 0.2
        return model