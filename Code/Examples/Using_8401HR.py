import sys, os
sys.path.insert(0, os.path.join( os.path.abspath('.'), 'Code', 'API_Modules') )

# local imports
from SerialCommunication    import COM_io
from PodDevice_8401HR       import POD_8401HR

# authorship
__author__      = "Thresa Kelly"
__maintainer__  = "Thresa Kelly"
__credits__     = ["Thresa Kelly", "Seth Gabbert"]
__license__     = "New BSD License"
__copyright__   = "Copyright (c) 2023, Thresa Kelly"
__email__       = "sales@pinnaclet.com"

# ===============================================================

def ChoosePort() -> str : 
    # get ports
    portList = COM_io.GetCOMportsList()
    print('Available COM Ports: '+', '.join(portList))
    # request port from user
    choice = input('Select port: COM')
    # search for port in list
    for port in portList:
        if port.startswith('COM'+choice):
            return(port)
    print('[!] COM'+choice+' does not exist. Try again.')
    return(ChoosePort())

def Write(pod: POD_8401HR, cmd: str | int, payload: int | bytes | tuple[int | bytes] = None) : 
    write = pod.WritePacket(cmd, payload)
    write = pod.TranslatePODpacket(write)
    print('Write:\t', write)

def Read(pod: POD_8401HR) : 
    read = pod.ReadPODpacket()
    read = pod.TranslatePODpacket(read)
    print('Read:\t', read)

def RunCommand(pod: POD_8401HR, cmd: str | int, payload: int | bytes | tuple[int | bytes] = None) :
   Write(pod,cmd,payload)
   Read(pod)

# ===============================================================

# create instance of 8206-HR POD device

port: str = ChoosePort()
ssGain: dict[str,int|None] = {'A':1,'B':5,'C':None,'D':None}
preampGain: dict[str,int|None] = {'A':10,'B':100,'C':None,'D':None}
pod = POD_8401HR(port, ssGain, preampGain)

# write each command:

print('~~ BASICS ~~')
RunCommand(pod, 'PING') # Used to verify device is present and communicating
RunCommand(pod, 'TYPE') # Returns the device type value.  This is a unique value for each device.  For the 8041-HR it is 0x31
RunCommand(pod, 'ID') # Returns the device ID value 
RunCommand(pod, 'FIRMWARE VERSION') # Returns the device firmware version as 3 values.  So 1.0.10 would come back as 0x31, 0x30, 0x00, 0x41

print('~~ SAMPLE RATE ~~')
sampleRate_Hz: int = 2500
RunCommand(pod, 'SET SAMPLE RATE', sampleRate_Hz) # Sets the sample rate of the system, in Hz.  Valid values are 2000 - 20000 currently
RunCommand(pod, 'GET SAMPLE RATE') # Gets the current sample rate of the system, in Hz.

print('~~ HIGHPASS ~~')
channel = 0 
highPass_Hz = 1
RunCommand(pod, 'SET HIGHPASS', (channel, highPass_Hz)) # Sets the highpass filter for a channel. Requires channel to set, and filter value.  Values are the same as returned in GET HIGHPASS
RunCommand(pod, 'GET HIGHPASS',  channel) # Reads the highpass filter value for a channel.  Requires the channel to read, returns 0-3, 0 = 0.5Hz, 1 = 1Hz, 2 = 10Hz, 3 = DC / No Highpass 

print('~~ LOWPASS ~~')
lowPass_Hz = 400
RunCommand(pod, 'SET LOWPASS', (channel, lowPass_Hz)) # Sets the lowpass filter for the desired channel to the desired value (21 - 15000) in Hz.   Requires the channel to read, and value in Hz.
RunCommand(pod, 'GET LOWPASS',  channel) # Gets the lowpass filter for the desired channel.  Requires the channel to read, Returns the value in Hz

print('~~ DC MODE ~~')
dcMode = 1
RunCommand(pod, 'SET DC MODE', (channel, dcMode)) # Sets the DC mode for the selected channel.   Requires the channel to read, and value to set.  Values are the same as in GET DC MODE
RunCommand(pod, 'GET DC MODE',  channel) # Gets the DC mode for the channel.   Requires the channel to read, returns the value 0 = Subtract VBias, 1 = Subtract AGND.  Typically 0 for Biosensors, and 1 for EEG/EMG

print('~~ BIAS ~~')
bias_V = 0.6
bias_dac = pod.CalculateBiasDAC_GetDACValue(bias_V)
RunCommand(pod, 'SET BIAS', (channel, bias_dac)) # Sets the bias on a given channel.  Requires the channel and DAC value as specified in GET BIAS.  Note that for most preamps, only channel 0/A DAC values are used. This can cause issues with bias subtraction on preamps with multiple bio chanenls
RunCommand(pod, 'GET BIAS',  channel) # Gets the bias on a given channel.  Returns the DAC value as a 16-bit 2's complement value, representing a value from +/- 2.048V

print('~~ EXT ~~')
ext0 = 0
RunCommand(pod, 'SET EXT0', ext0) # Sets the digital value of EXT0, 0 or 1
RunCommand(pod, 'GET EXT0 VALUE') # Reads the analog value on the EXT0 pin.  Returns an unsigned 12-bit value, representing a 3.3V input.  This is normally used to identify preamps.  Note that this function takes some time and blocks, so it should not be called during data acquisition if possible
ext1 = 1 
RunCommand(pod, 'SET EXT1', ext0) # Sets the digital value of EXT1, 0 or 1
RunCommand(pod, 'GET EXT1 VALUE') # Reads the analog value on the EXT1 pin.  Returns an unsigned 12-bit value, representing a 3.3V input.  This is normally used to identify if an 8480 is present.  Similar caveat re blocking as GET EXT0 VALUE

print('~~ GROUND ~~')
channelGrounded = pod.GetChannelBitmask(a=1, b=1, c=0, d=0)
RunCommand(pod, 'SET INPUT GROUND', channelGrounded) # Sets whether channel inputs are grounded or connected to the preamp.  Bitfield, bits 0-3, high nibble should be 0s.  0=Grounded, 1=Connected to Preamp
RunCommand(pod, 'GET INPUT GROUND') # Returns the bitmask value from SET INPUT GROUND

print('~~ TTL ~~')
ttl = pod.GetTTLbitmask(ext0=0,ext1=1,ttl4=0,ttl3=0,ttl2=1,ttl1=1)
RunCommand(pod, 'SET TTL CONFIG', (ttl,ttl)) # Configures the TTL pins.  First argument is output setup, 0 is open collector and 1 is push-pull.  Second argument is input setup, 0 is analog and 1 is digital.  Bit 7 = EXT0, bit 6 = EXT1, bits 4+5 unused, bits 0-3 TTL pins
RunCommand(pod, 'GET TTL CONFIG') # Gets the TTL config byte, values are as per SET TTL CONFIG
RunCommand(pod, 'GET TTL ANALOG', channel) # Reads a TTL input as an analog signal.  Requires a channel to read, returns a 10-bit analog value.  Same caveats and restrictions as GET EXTX VALUE commands.  Normally you would just enable an extra channel in Sirenia for this.

print('~~ SS CONFIG ~~')
ss = pod.GetSSConfigBitmask(gain=1,highpass=1)
RunCommand(pod, 'SET SS CONFIG', (channel,ss)) # Sets the second stage gain config.  Requires the channel and a config bitfield as per GET SS CONFIG
RunCommand(pod, 'GET SS CONFIG',  channel) # Gets the second stage gain config.  Requires the channel and returins a bitfield. Bit 0 = 0 for 0.5Hz Highpass, 1 for DC Highpass.  Bit 1 = 0 for 5x gain, 1 for 1x gain

print('~~ MUX MODE ~~')
muxMode = 0
RunCommand(pod, 'SET MUX MODE', muxMode) # Sets mux mode on or off.  This causes EXT1 to toggle periodically to control 2BIO 3EEG preamps.  0 = off, 1 = on
RunCommand(pod, 'GET MUX MODE') # Gets the state of mux mode.  See SET MUX MODE