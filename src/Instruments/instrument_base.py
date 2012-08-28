import abc

#make this an abstract class, requires an implementation
class Instrument_Base(object):
    
    @abc.abstractmethod
    def generateILP(self):
        return
        
    @abc.abstractmethod
    def generateDataflow(self):
        return
        