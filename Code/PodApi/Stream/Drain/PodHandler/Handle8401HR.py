# enviornment imports
import pandas as pd

# local imports
from PodApi.Devices import Pod8401HR
from PodApi.Packets import Packet, PacketBinary5
from PodApi.Stream.Drain.PodHandler import DrainDeviceHandler

# authorship
__author__      = "Thresa Kelly"
__maintainer__  = "Thresa Kelly"
__credits__     = ["Thresa Kelly", "Seth Gabbert"]
__license__     = "New BSD License"
__copyright__   = "Copyright (c) 2023, Thresa Kelly"
__email__       = "sales@pinnaclet.com"
        
class Drain8401HR(DrainDeviceHandler) :
    """Class to help handle 8206-HR POD devices for the Drain classes.
    
    Attributes:
        preampDevice (str|None): Optional preamplifier for the 8401-HR.
    """
    
    def __init__(self, preampDevice: str = None) -> None:
        """Sets the class instance variables.

        Args:
            preampDevice (str, optional): Optional preamplifier for the 8401-HR. Defaults to None.
        """
        super().__init__()
        self.preampDevice: str|None = preampDevice

    def GetDeviceColNames(self) -> str :
        """Gets a string of the column names formatter for a text file.

        Returns:
            str: String of the filenames separated by commas and ending in a newline.
        """
        cols = self.GetDeviceColNamesList()
        cols.remove('NC')
        return ','.join(cols) + '\n'
    
    def GetDeviceColNamesList(self, includeTime: bool = True) -> list[str] : 
        """Gets a list of all collumn titles.

        Args:
            includeTime (bool, optional): Flag to include 'Time' in the columns list. \
                Defaults to True. 

        Returns:
            list[str]: List of columns.
        """
        cols: list[str] = []
        if(includeTime) : cols += ['Time']
        if(self.preampDevice != None and Pod8401HR.IsPreampDeviceSupported(self.preampDevice)) : 
            for label in Pod8401HR.GetChannelMapForPreampDevice(str(self.preampDevice)).values() : 
                cols.append(label)
        else : 
            cols += ['A','B','C','D']
        cols += ['Analog EXT0','Analog EXT1','Analog TTL1','Analog TTL2','Analog TTL3','Analog TTL4']
        return cols
                    
    def DropToDf(self, timestamps: list[float], data: list[Packet | None]) -> pd.DataFrame : 
        """Converts the timestamps and data into a Pandas DataFrame. The columns should \
            match GetDeviceColNames().

        Args:
            timestamps (list[float]): List of timestamps in seconds for each data packet.
            data (list[Packet | None]): List of streaming binary data packets. 

        Returns:
            pd.DataFrame: DataFrame containing the timestamps and packet data.
        """
        cols = self.GetDeviceColNamesList()
        dfPrep = { cols[0] : timestamps }
        # channels
        for idx,ch in zip([1,2,3,4], ['A','B','C','D']) : 
            if(cols[idx] != 'NC') : 
                dfPrep[cols[idx]] = [ pkt.Channel(ch) if (isinstance(pkt, PacketBinary5)) else None for pkt in data]
        # EXT
        for idx,ext in zip([5,6], [0,1]) : 
            dfPrep[cols[idx]] = [ pkt.AnalogEXT(ext) if (isinstance(pkt, PacketBinary5)) else None for pkt in data]
        # TTL
        for idx,ttl in zip([7,8,9,10], [1,2,3,4]) : 
            dfPrep[cols[idx]] = [ pkt.AnalogTTL(ttl) if (isinstance(pkt, PacketBinary5)) else None for pkt in data]
        # build df 
        return pd.DataFrame(dfPrep)
