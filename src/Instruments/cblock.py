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
    
    @staticmethod    
    def getPFBModel(platforms):
        return {'ROACH': {'registers': 0.2, 'slices': 0.1, 'dsp': 0.1, 'bram': 0.4},'GPU': {'time': 0.56}}

    @staticmethod    
    def getFFTModel(platforms):
        return {'ROACH': {'registers': 0.2, 'slices': 0.1, 'dsp': 0.1, 'bram':0.4}, 'GPU': {'time': 0.5}}

    @staticmethod
    def getXEngModel(platforms):
        return {'ROACH': {'registers': 0.9, 'slices': 0.1, 'dsp': 0.1, 'bram':0.4}, 'GPU': {'time': 0.25}}

    @staticmethod
    def getVAccModel(platforms):
        return {'ROACH': {'registers': 0.2, 'slices': 0.1, 'dsp': 0.1, 'bram':0}, 'GPU': {'time': 0.1}}