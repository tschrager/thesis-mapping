from Instruments.spectrometer import *



def test_spectrometer():
    hiresspec = Spectrometer(100,1024,10)
    hiresspec.generateDataflow()


if __name__ == "__main__":  
    test_spectrometer()