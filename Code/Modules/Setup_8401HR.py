"""
Setup_8401HR provides the setup functions for an 8206-HR POD device.
"""

# enviornment imports
from texttable import Texttable

# local imports
from Setup_PodInterface  import Setup_Interface
from PodDevice_8401HR    import POD_8401HR 

# authorship
__author__      = "Thresa Kelly"
__maintainer__  = "Thresa Kelly"
__credits__     = ["Thresa Kelly", "Seth Gabbert"]
__license__     = "New BSD License"
__copyright__   = "Copyright (c) 2023, Thresa Kelly"
__email__       = "sales@pinnaclet.com"

class Setup_8401HR(Setup_Interface) : 
    
    # ============ GLOBAL CONSTANTS ============      ========================================================================================================================
    
    _CHANNELKEYS = ['A','B','C','D']

    # overwrite from parent
    _NAME : str = '8401-HR'


    # ============ PUBLIC METHODS ============      ========================================================================================================================


    @staticmethod
    def GetDeviceName() -> str : 
        # returns the name of the POD device 
        return(Setup_8401HR._NAME)
    

    # ============ PRIVATE METHODS ============      ========================================================================================================================


    # ------------ SETUP POD PARAMETERS ------------


    def _GetParam_onePODdevice(self, forbiddenNames: list[str]) -> dict[str,(str|int|dict)] :
        params = {
            self._PORTKEY           : self._ChoosePort(forbiddenNames),
            'Preamplifier Device'   : self._GetPreampDeviceName(),
            'Sample Rate'           : Setup_Interface._AskForIntInRange('Set sample rate (Hz)', 2000, 20000),
        }
        # get channel map for the user's preamplifier 
        chmap = POD_8401HR.GetChannelMapForPreampDevice(params['Preamplifier Device'])
        # get parameters for each channel (A,B,C,D)
        params['Preamplifier Gain'] = self._SetForMappedChannels('Set preamplifier gain (1, 10, or 100) for...',        chmap, self._SetPreampGain  )
        params['Second Stage Gain'] = self._SetForMappedChannels('Set second stage gain (1 or 5) for...',               chmap, self._SetSSGain      )
        params['High-pass']         = self._SetForMappedChannels('Set high-pass filter (0, 0.5, 1, or 10 Hz) for...',   chmap, self._SetHighpass    )
        params['Low-pass']          = self._SetForMappedChannels('Set low-pass filter (21-15000 Hz) for...',            chmap, self._SetLowpass     )
        params['DC Mode']           = self._SetForMappedChannels('Set DC mode (VBIAS or AGND) for...',                  chmap, self._SetDCMode      )     
        params['MUX Mode']          = self._SetForMappedChannels('Use Mux mode (y/n) for...',                  chmap, self._SetMuxMode      )     
        # params['Bias']              = self._SetForMappedChannels('Set Bias for...', chmap, self.XXX)
        return(params)


    def _GetPreampDeviceName(self) -> str : 
        deviceList = POD_8401HR.GetSupportedPreampDevices()
        return( Setup_Interface._AskForStrInList(
            prompt='Set mouse/rat preamplifier',
            goodInputs=deviceList,
            badInputMessage='[!] Please input a valid mouse/rat preamplifier '+str(tuple(deviceList))+'.'))

        
    def _SetForMappedChannels(self, message: str, channelMap: dict[str,str], func: 'function') -> dict[str,int|None]: # func MUST take one argument, which is the channel map value 
        print(message)
        preampDict = {}
        for abcd, label in channelMap.items() : 
            # automatically set to None if no-connect (NC)
            if(label == 'NC') : 
                preampDict[abcd] = None
            # otherwise, ask for input 
            else: 
                preampDict[abcd] = func(label)
        return(preampDict)
    

    @staticmethod
    def _SetPreampGain(channelName: str) -> int|None: 
        gain = Setup_Interface._AskForIntInList(
            prompt='\t'+str(channelName), 
            goodInputs=[1,10,100], 
            badInputMessage='[!] For EEG/EMG, the gain must be 10 or 100. For biosensors, the gain is 1 (None).')
        if(gain == 1) : 
            return(None)
        return(gain)
        

    @staticmethod
    def _SetSSGain(channelName: str) -> int|None : 
        return( Setup_8401HR._AskForIntInList(
            prompt='\t'+str(channelName), 
            goodInputs=[1,5], 
            badInputMessage='[!] The gain must be 1 or 5.') )


    @staticmethod
    def _SetHighpass(channelName: str) -> int|None : 
        # NOTE  SET HIGHPASS Sets the highpass filter for a channel (0-3). 
        #       Requires channel to set, and filter value (0-3): 
        #       0 = 0.5Hz, 1 = 1Hz, 2 = 10Hz, 3 = DC / No Highpass 
        # NOTE  be sure to convert the input value to a number key usable by the device!
        hp = Setup_Interface._AskForFloatInList(
            prompt='\t'+str(channelName),
            goodInputs=[0,0.5,1,10],
            badInputMessage='[!] The high-pass filter must be 0.5, 1, or 10 Hz. If the channel is DC, input 0.' )
        if(hp == 0) :
            return(None)
        return(hp)


    @staticmethod
    def _SetLowpass(channelName: str) -> int|None : 
        return(Setup_Interface._AskForIntInRange(
            prompt='\t'+str(channelName), 
            minimum=21, maximum=15000, 
            thisIs='The low-pass filter', unit=' Hz' ))
    

    @staticmethod
    def _SetDCMode(channelName: str) -> str : 
        # NOTE  SET DC MODE Sets the DC mode for the selected channel. 
        #       Requires the channel to read, and value to set: 
        #       0 = Subtract VBias, 1 = Subtract AGND.  
        #       Typically 0 for Biosensors, and 1 for EEG/EMG
        # NOTE  be sure to convert the input value to a number key usable by the device!
        return( Setup_Interface._AskForStrInList(
            prompt='\t'+str(channelName),
            goodInputs=['VBIAS','AGND'],
            badInputMessage='[!] The DC mode must subtract VBias or AGND. Typically, Biosensors are VBIAS and EEG/EMG are AGND.' ))
    

    @staticmethod
    def _SetMuxMode(channelName: str) -> str :
        return(Setup_8401HR._AskYN('\t'+str(channelName), append=': '))
    

    # ------------ DISPLAY POD PARAMETERS ------------


    def _GetPODdeviceParameterTable(self) -> Texttable : 
        # setup table 
        tab = Texttable(150)
        # write column names
        tab.header(['Device #',self._PORTKEY,'Preamplifier Device',
                    'Sample Rate (Hz)','Preamplifier Gain','Second Stage Gain',
                    'High-pass (Hz)','Low-pass (Hz)','DC Mode','MUX Mode'])
        # for each device 
        for key,val in self._podParametersDict.items() :
            # get channel mapping for device 
            chmap = POD_8401HR.GetChannelMapForPreampDevice(val['Preamplifier Device'])
            # write row to table 
            tab.add_row([
                key, val[self._PORTKEY], val['Preamplifier Device'], val['Sample Rate'],
                self._NiceABCDtableText(val['Preamplifier Gain'],   chmap),
                self._NiceABCDtableText(val['Second Stage Gain'],   chmap),
                self._NiceABCDtableText(val['High-pass'],           chmap),
                self._NiceABCDtableText(val['Low-pass'],            chmap),
                self._NiceABCDtableText(val['DC Mode'],             chmap),
                self._NiceABCDtableText(val['MUX Mode'],            chmap)])
        # return table object 
        return(tab)
    

    def _NiceABCDtableText(self, abcdValueDict: dict[str,int|str|None], channelMap: dict[str,str]) -> str:
        # build nicely formatted text
        text = ''
        for key,val in channelMap.items() : 
            # <channel label>: <user's input> \n
            text += (str(val) +': ' + str(abcdValueDict[key]) + '\n')
        # cut off the last newline then return string 
        return(text[:-1])


    # ------------ FILE HANDLING ------------
    # ------------ STREAM ------------ 

    ########################################
    #               WORKING
    ########################################
