

# enviornment imports
import os 
import time
import copy
import numpy       as     np
from   texttable   import Texttable
from   threading   import Thread
from   pyedflib    import EdfWriter
from   io          import IOBase


# local imports
from Setup_PodInterface import Setup_Interface
from PodDevice_8206HR   import POD_8206HR 
from GetUserInput       import UserInput

# authorship
__author__      = "Thresa Kelly"
__maintainer__  = "Thresa Kelly"
__credits__     = ["Thresa Kelly", "Sree Kondi", "Seth Gabbert"]
__license__     = "New BSD License"
__copyright__   = "Copyright (c) 2023, Thresa Kelly"
__email__       = "sales@pinnaclet.com"

class Setup_8206HR(Setup_Interface) : 
    """
    Setup_8206HR provides the setup functions for an 8206-HR POD device.

    Attributes:
        _PARAMKEYS (list[str]): Class-level list containing the device parameter dict keys.
        _LOWPASSKEYS (list[str]): Class-level list containing the keys of the 'Low-pass' parameter \
            dict value.
        _PHYSICAL_BOUND_uV (int): Class-level integer representing the max/-min physical value in uV. \
            Used for EDF files. 
        _NAME (str): Class-level string containing the POD device name.
    """

    # ============ GLOBAL CONSTANTS ============      ========================================================================================================================
    
    
    # deviceParams keys for reference 
    _PARAMKEYS   : list[str] = [Setup_Interface._PORTKEY,'Sample Rate','Preamplifier Gain','Low-pass']
    _LOWPASSKEYS : list[str] = ['EEG1','EEG2','EEG3/EMG']

    # for EDF file writing 
    _PHYSICAL_BOUND_uV : int = 2046 # max/-min stream value in uV

    # overwrite from parent
    _NAME : str = '8206-HR'


    # ============ PUBLIC METHODS ============      ========================================================================================================================


    @staticmethod
    def GetDeviceName() -> str : 
        """Returns the name of the POD device.

        Returns:
            str: String of _NAME.
        """
        # returns the name of the POD device 
        return(Setup_8206HR._NAME)
    

    # ============ PRIVATE METHODS ============      ========================================================================================================================


    # ------------ DEVICE CONNECTION ------------


    def _ConnectPODdevice(self, deviceNum: int, deviceParams: dict[str,(str|int|dict[str,int])]) -> bool : 
        """Creates a POD_8206HR object and write the setup parameters to it. 

        Args:
            deviceNum (int): Integer of the device's number.
            deviceParams (dict[str,): Dictionary of the device's parameters

        Returns:
            bool: True if connection was successful, false otherwise.
        """
        failed = True 
        try : 
            # get port name 
            port = deviceParams[self._PORTKEY].split(' ')[0] # isolate COM# from rest of string
            # create POD device 
            self._podDevices[deviceNum] = POD_8206HR(port=port, preampGain=deviceParams['Preamplifier Gain'])
            # test if connection is successful
            if(self._TestDeviceConnection(self._podDevices[deviceNum])):
                # write setup parameters
                self._podDevices[deviceNum].WriteRead('SET SAMPLE RATE', deviceParams['Sample Rate']          )
                self._podDevices[deviceNum].WriteRead('SET LOWPASS', (0, deviceParams['Low-pass']['EEG1']    ))
                self._podDevices[deviceNum].WriteRead('SET LOWPASS', (1, deviceParams['Low-pass']['EEG2']    ))
                self._podDevices[deviceNum].WriteRead('SET LOWPASS', (2, deviceParams['Low-pass']['EEG3/EMG']))   
                failed = False
        except : # except Exception as e : print('[!]', e) # use this for testing 
            # fill entry 
            self._podDevices[deviceNum] = None

        # check if connection failed 
        if(failed) :
            print('[!] Failed to connect device #'+str(deviceNum)+' to '+port+'.')
        else :
            print('Successfully connected device #'+str(deviceNum)+' to '+port+'.')
        # return True when connection successful, false otherwise
        return(not failed)


    # ------------ SETUP POD PARAMETERS ------------


    def _GetParam_onePODdevice(self, forbiddenNames: list[str]) -> dict[str,(str|int|dict[str,int])] : 
        """Asks the user to input all the device parameters. 

        Args:
            forbiddenNames (list[str]): List of port names already used by other devices.

        Returns:
            dict[str,(str|int|dict[str,int])]: Dictionary of device parameters.
        """
         
        return({
            self._PORTKEY       : self._ChoosePort(forbiddenNames),
            'Sample Rate'       : UserInput.AskForIntInRange('Set sample rate (Hz)', 100, 2000),
            'Preamplifier Gain' : self._ChoosePreampGain(),
            'Low-pass'          : {
                    'EEG1'      : UserInput.AskForIntInRange('Set lowpass (Hz) for EEG1',     11, 500),
                    'EEG2'      : UserInput.AskForIntInRange('Set lowpass (Hz) for EEG2',     11, 500),
                    'EEG3/EMG'  : UserInput.AskForIntInRange('Set lowpass (Hz) for EEG3/EMG', 11, 500)
                }
        })
    
    @staticmethod
    def _ChoosePreampGain() -> int :
        """Asks user for the preamplifier gain of their POD device.

        Returns:
            int: Integer 10 or 100 for the preamplifier gain.
        """
        gain = UserInput.AskForInt('Set preamplifier gain')
        # check for valid input 
        if(gain != 10 and gain != 100):
            # prompt again 
            print('[!] Input must be 10 or 100.')
            return(Setup_8206HR._ChoosePreampGain())
        # return preamplifier gain 
        return(gain)
    

    # ------------ DISPLAY POD PARAMETERS ------------


    def _GetPODdeviceParameterTable(self) -> Texttable :
        """Builds a table containing the parameters for all POD devices.

        Returns:
            Texttable: Texttable containing all parameters.
        """
        # setup table 
        tab = Texttable()
        # write column names
        tab.header(['Device #',self._PORTKEY,'Sample Rate (Hz)', 'Preamplifier Gain', 'EEG1 Low-pass (Hz)','EEG2 Low-pass (Hz)','EEG3/EMG Low-pass (Hz)'])
        # write rows
        for key,val in self._podParametersDict.items() :
            tab.add_row([key, val[self._PORTKEY], val['Sample Rate'], val['Preamplifier Gain'], val['Low-pass']['EEG1'], val['Low-pass']['EEG2'], val['Low-pass']['EEG3/EMG']])       
        return(tab)
    

    # ------------ FILE HANDLING ------------


    def _OpenSaveFile_TXT(self, fname: str) -> IOBase : 
        """Opens a text file and writes the column names. Writes the current date/time at the top of \
        the txt file.

        Args:
            fname (str): String filename.

        Returns:
            IOBase: Opened file.
        """
        # open file and write column names 
        f = open(fname, 'w')
        # write time
        f.write( self._GetTimeHeader_forTXT() ) 
        # columns names
        f.write('\nTime,CH0,CH1,CH2\n')
        return(f)
    

    def _OpenSaveFile_EDF(self, fname: str, devNum: int) -> EdfWriter :
        """Opens EDF file and write header.

        Args:
            fname (str): String filename.
            devNum (int): Integer device number.

        Returns:
            EdfWriter: Opened file.
        """
        # number of channels 
        n = len(self._LOWPASSKEYS)
        # create file
        f = EdfWriter(fname, n) 
        # get info for each channel
        for i in range(n):
            f.setSignalHeader( i, {
                'label' : self._LOWPASSKEYS[i],
                'dimension' : 'uV',
                'sample_rate' : self._podParametersDict[devNum]['Sample Rate'],
                'physical_max': self._PHYSICAL_BOUND_uV,
                'physical_min': -self._PHYSICAL_BOUND_uV, 
                'digital_max': 32767, 
                'digital_min': -32768, 
                'transducer': '', 
                'prefilter': ''            
            } )
        return(f)


    @staticmethod
    def _WriteDataToFile_TXT(file: IOBase, data: list[np.ndarray],  t: np.ndarray) : 
        """Writes data to an open text file.

        Args:
            file (IOBase): opened write file.
            data (list[np.ndarray]): List of 3 items, one for each channel.
            t (np.ndarray): list with the time stamps (in seconds).
        """
        for i in range(len(t)) : 
            line = [t[i], data[0][i], data[1][i], data[2][i] ]
            # convert data into comma separated string
            line = ','.join(str(x) for x in line) + '\n'
            # write data to file 
            file.write(line)


    @staticmethod
    def _WriteDataToFile_EDF(file: EdfWriter, data: list[np.ndarray]) : 
        """Writes data to an open EDF file.

        Args:
            file (EdfWriter): opened EDF file.
            data (list[np.ndarray]): List of 3 items, one for each channel.
        """
        # write data to EDF file 
        file.writeSamples(data)


    # ------------ STREAM ------------ 


    def _StreamThreading(self) -> dict[int,Thread] :
        """Opens a save file, then creates a thread for each device to stream and write data from. 

        Returns:
            dict[int,Thread]: Dictionary with keys as the device number and values as the started Thread.
        """
        # create save files for pod devices
        podFiles = {devNum: self._OpenSaveFile(devNum) for devNum in self._podDevices.keys()}
        # make threads for reading 
        readThreads = {
            # create thread to _StreamUntilStop() to dictionary entry devNum
            devNum : Thread(
                    target = self._StreamUntilStop, 
                    args = ( pod, file, params['Sample Rate'] ))
            # for each device 
            for devNum,params,pod,file in 
                zip(
                    self._podParametersDict.keys(),     # devNum
                    self._podParametersDict.values(),   # params
                    self._podDevices.values(),          # pod
                    podFiles.values() )                 # file
        }
        for t in readThreads.values() : 
            # start streaming (program will continue until .join() or streaming ends)
            t.start()
        return(readThreads)
    
    
    def _StreamUntilStop(self, pod: POD_8206HR, file: IOBase|EdfWriter, sampleRate: int) -> None :
        """Streams data from a POD device and saves data to file. Stops looking when a stop stream \
        command is read. Calculates average time difference across multiple packets to collect a \
        continuous time series data. 

        Args:
            pod (POD_8206HR): POD device to read from.
            file (IOBase | EdfWriter): open file.
            sampleRate (int): Integer sample rate in Hz.
        """
        # get file type
        name, ext = os.path.splitext(self._saveFileName)
        # packet to mark stop streaming 
        stopAt = pod.GetPODpacket(cmd='STREAM', payload=0)  
        # start streaming from device  
        pod.WriteRead(cmd='STREAM', payload=1)
        # initialize times
        t_forEDF: int = 0
        currentTime :float = 0.0 
        times = np.zeros(sampleRate)
        # annotate start
        if(ext == '.edf') : file.writeAnnotation(t_forEDF, -1, "Start")
        # start reading
        while(True):
            # initialize data array 
            data0 = np.zeros(sampleRate)
            data1 = np.zeros(sampleRate)
            data2 = np.zeros(sampleRate)
            # track time (second)
            ti = (round(time.time(),9)) # initial time 
            # read data for one second
            for i in range(sampleRate):
                # read once 
                r = pod.ReadPODpacket()
                # stop looping when stop stream command is read 
                if(r == stopAt) : 
                    if(ext=='.edf') : file.writeAnnotation(t_forEDF, -1, "Stop")
                    file.close()
                    return  ##### END #####
                # translate 
                rt = pod.TranslatePODpacket(r)
                # save data as uV
                data0[i] = self._uV(rt['Ch0'])
                data1[i] = self._uV(rt['Ch1'])
                data2[i] = self._uV(rt['Ch2'])
            # get average sample period
            tf = round(time.time(),9) # final time
            td = tf - ti # time difference 
            average_td = (round((td/sampleRate), 9)) # time between samples
            # increment time for each sample
            for i in range(sampleRate):
                times[i] = (round(currentTime, 9))
                currentTime += average_td  #adding avg time differences + CurrentTime = CurrentTime
            # save to file 
            if(ext=='.csv' or ext=='.txt') : self._WriteDataToFile_TXT(file, [data0,data1,data2], times)
            elif(ext=='.edf') :              self._WriteDataToFile_EDF(file, [data0,data1,data2])
            # increment edf time by 1 sec
            t_forEDF += 1
        # end while 
            
            
    def StopStream(self) -> None :
        """Write a command to stop streaming data to all POD devices."""
        # tell devices to stop streaming 
        for pod in self._podDevices.values() : 
            if(pod != None) : pod.WritePacket(cmd='STREAM', payload=0)
            

    # ------------ VALIDATION ------------


    def _IsOneDeviceValid(self, paramDict: dict) -> bool :
        """Raises an exception if the parameters dictionary is incorrectly formatted.

        Args:
            paramDict (dict): Dictionary of the parameters for one device.

        Raises:
            Exception: Invalid parameters.
            Exception: Invalid parameter value types.
            Exception: Invalid low-pass parameters.
            Exception: Invalid low-pass value types.

        Returns:
            bool: True if no exceptions are raised.
        """
        # check that all params exist 
        if(list(paramDict.keys()).sort() != copy.copy(self._PARAMKEYS).sort() ) :
            raise Exception('[!] Invalid parameters for '+str(self._NAME)+'.')
        # check type of each specific command 
        if( not(
                    isinstance( paramDict[Setup_Interface._PORTKEY], str  ) 
                and isinstance( paramDict['Sample Rate'],            int  ) 
                and isinstance( paramDict['Preamplifier Gain'],      int  ) 
                and isinstance( paramDict['Low-pass'],               dict ) 
            )
        ) : 
            raise Exception('[!] Invalid parameter value types for '+str(self._NAME)+'.')
        # check that low-pass is correct
        if( list(paramDict['Low-pass'].keys()).sort() != copy.copy(self._LOWPASSKEYS).sort() ) : 
            raise Exception('[!] Invalid low-pass parameters for '+str(self._NAME)+'.')
        # check type of low-pass
        for lowPassVal in paramDict['Low-pass'].values() : 
            if( not isinstance(lowPassVal, int) ) : 
                raise Exception('[!] Invalid low-pass value types for '+str(self._NAME)+'.')
        # no exception raised 
        return(True)