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