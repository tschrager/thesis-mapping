import abc

#make this an abstract class, requires an implementation
class CBlock_Base(object):
    
    @abc.abstractmethod
    def generateConstraints(self):
        return
