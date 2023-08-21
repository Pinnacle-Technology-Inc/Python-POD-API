# enviornment imports
from pyedflib import EdfWriter
from typing import Literal

# local imports
from PodApi.Stream.Drain    import DrainToFile
from PodApi.Stream          import Bucket

# authorship
__author__      = "Thresa Kelly"
__maintainer__  = "Thresa Kelly"
__credits__     = ["Thresa Kelly", "Seth Gabbert"]
__license__     = "New BSD License"
__copyright__   = "Copyright (c) 2023, Thresa Kelly"
__email__       = "sales@pinnaclet.com"

class DrainToEDF(DrainToFile) : 
    
    def __init__(self, dataBucket: Bucket, fileName: str, preampDevice: str|None = None) -> None:
        """Set class instance variables.

        Args:
            dataBucket (Bucket): Bucket to collect streaming data.
            fileName (str): Name (with optional file path) of the file to save data to.
            preampDevice (str | None, optional): Optional preamplifier for the 8401-HR. Defaults to None.

        Raises:
            DrainToEDF: DrainToTXT only accepts the '.edf' extension.
        """
        super().__init__(dataBucket, fileName, preampDevice)
        if( DrainToEDF.GetExtension(self.fileName) != '.edf' ) : 
            raise DrainToEDF('[!] DrainToTXT only accepts the \'.edf\' extension.')
        # init
        self.file: EdfWriter|None = None

    @staticmethod
    def PhysicalBound() -> Literal[2046] :
        return 2046 # max/-min stream value in uV

    @staticmethod
    def DigitalMax() -> Literal[32767] :
        return 32767
    
    @staticmethod
    def DigitalMin() -> Literal[-32768] : 
        return -32768

    def OpenFile(self) : 
        """Opens and initializes a file using the fileName to save data to. 
        """
        # get signals/channels 
        allChannels = self.deviceHandler.GetDeviceColNamesList(False)
        n = len(allChannels)
        # create file 
        self.file = EdfWriter(self.fileName, n)
        # set header for each channel
        for i in range(n) :
            self.file.setSignalHeader( i, {
                'label'         : allChannels[i],
                'dimension'     : 'uV',
                'sample_rate'   : DrainToEDF.SampleRate(),
                'physical_max'  : DrainToEDF.PhysicalBound(),
                'physical_min'  : -DrainToEDF.PhysicalBound(), 
                'digital_max'   : DrainToEDF.DigitalMax(), 
                'digital_min'   : DrainToEDF.DigitalMin(), 
                'transducer'    : '', 
                'prefilter'     : ''            
            } )

    def CloseFile(self) : 
        """Closes the file that data is saved to.
        """
        if(self.file != None) : 
            self.file.close()