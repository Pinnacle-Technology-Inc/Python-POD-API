# local imports
from SerialCommunication    import COM_io
from PodPacketHandling      import POD_Packets
from PodCommands            import POD_Commands
from PodPacket              import Packet_Standard
from PodPacket              import Packet_BinaryStandard

# authorship
__author__      = "Thresa Kelly"
__maintainer__  = "Thresa Kelly"
__credits__     = ["Thresa Kelly", "Seth Gabbert"]
__license__     = "New BSD License"
__copyright__   = "Copyright (c) 2023, Thresa Kelly"
__email__       = "sales@pinnaclet.com"

class POD_Basics : 
    """
    POD_Basics handles basic communication with a generic POD device, including reading and writing 
    packets and packet interpretation.

    Attributes: 
        _port (COM_io): Instance-level COM_io object, which handles the COM port 
        _commands (POD_Commands): Instance-level POD_Commands object, which stores information about \
            the commands available to this POD device.
    """

    # ============ GLOBAL CONSTANTS ============    ========================================================================================================================


    __numPod : int = 0
    """Class-level integer counting the number of POD_Basics instances. \
    Maintained by __init__ and __del__.
    """
    
    # ============ DUNDER METHODS ============      ========================================================================================================================


    def __init__(self, port: str|int, baudrate:int=9600) -> None : 
        """Runs when an instance of POD_Basics is constructed. It initializes the instance variable for 
        the COM port communication (_port) and for the command handler (_commands). It also increments \
        the POD device counter (__NUMPOD).

        Args:
            port (str|int): Serial port to be opened. Used when initializing the COM_io instance.
            baudrate (int): Baud rate of the opened serial port. Used when initializing the COM_io \
                instance. Default value is 9600.
        """
        # initialize serial port 
        self._port : COM_io = COM_io(port, baudrate)
        # create object to handle commands 
        #print(port)
        self._commands : POD_Commands = POD_Commands()
        # increment number of POD device counter
        POD_Basics.__numPod += 1


    def __del__(self) -> None :
        """Runs when an instance is destructed."""
        # decrement number of POD device counter
        POD_Basics.__numPod -= 1


    # ============ STATIC METHODS ============      ========================================================================================================================
    

    # ------------ CLASS GETTERS ------------   ------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def GetU(u: int) -> int : 
        """number of hexadecimal characters for an unsigned u-bit value.

        Args:
            u (int): 8, 16, or 32 bits. Enter any other number for NOVALUE.

        Returns:
            int: number of hexadecimal characters for an unsigned u-bit value.
        """
        match u : 
            case  8: return(POD_Commands.U8())
            case 16: return(POD_Commands.U16())
            case 32: return(POD_Commands.U32())
            case  _: return(POD_Commands.NoValue())


    @staticmethod
    def GetNumberOfPODDevices() -> int :
        """Gets the POD device counter (__numPod).

        Returns: 
            int: Number of POD_Basics instances.
        """
        # returns the counter tracking the number of active pod devices
        return(POD_Basics.__numPod)


    # ------------ POD PACKET COMPREHENSION ------------             ------------------------------------------------------------------------------------------------------------------------
   
    @staticmethod
    def TranslatePODpacket_Binary(msg: bytes) -> dict[str,int|bytes] : 
        """Unpacks the variable-length binary POD packet and converts the values of the ASCII-encoded 
        bytes into integer values and leaves the binary-encoded bytes as is. 

        Args: 
            msg (bytes): Bytes message containing a variable-length POD packet.

        Returns:
            dict[str,int|bytes]: A dictionary containing the 'Command Number' and 'Binary Packet Length' \
                in integers, and 'Binary Data' in bytes.
        """
        # unpack parts of POD packet into dict
        msgDict = Packet_Standard.UnpackPODpacket_Standard(msg)
        # initialize dictionary for translated values 
        msgDictTrans = {}
        # translate the binary ascii encoding into a readable integer
        msgDictTrans['Command Number']          = POD_Packets.AsciiBytesToInt(msgDict['Command Number'])
        msgDictTrans['Binary Packet Length']    = POD_Packets.AsciiBytesToInt(msgDict['Binary Packet Length'])
        msgDictTrans['Binary Data']             = msgDict['Binary Data'] # leave this as bytes, change type if needed 
        # return translated unpacked POD packet 
        return(msgDictTrans)


    # ------------ CHECKSUM HANDLING ------------             ------------------------------------------------------------------------------------------------------------------------


    @staticmethod
    def _ValidateChecksum(msg: bytes) -> bool :
        """Validates the checksum of a given POD packet. The checksum is valid if the calculated checksum 
        from the data matches the checksum written in the packet. 

        Args: 
            msg (bytes): Bytes message containing a POD packet: STX (1 bytes) + data (? bytes) + checksum \
                (2 bytes) + ETX (1 byte). 

        Returns: 
            bool: True if the checksum is correct, false otherwise.

        Raises:
            Exception: msg does not begin with STX or end with ETX. 
        """
        # ... assume that msg contains STX + packet + csm + ETX. This assumption is good for more all 
        #     pod packets except variable length binary packet
        # get length of POD packet 
        packetBytes = len(msg)
        # check that packet begins with STX and ends with ETX
        if(    (msg[0].to_bytes(1,'big') != POD_Packets.STX()) 
            or (msg[packetBytes-1].to_bytes(1,'big') != POD_Packets.ETX())
        ) : 
            raise Exception('Cannot calculate the checksum of an invalid POD packet. The packet must begin with STX and end with ETX.')
        # get message contents excluding STX/ETX
        msgPacket = msg[1:packetBytes-3]
        msgCsm = msg[packetBytes-3:packetBytes-1]
        # calculate checksum from content packet  
        csmValid = POD_Packets.Checksum(msgPacket)
        # return True if checksums match 
        if(msgCsm == csmValid) :
            return(True)
        else:
            return(False)

        
    # ============ PUBLIC METHODS ============      ========================================================================================================================


    # ------------ PORT HANDLING ------------ ------------------------------------------------------------------------------------------------------------------------
    

    def FlushPort(self) -> bool : 
        """Reset the input and output serial port buffer.

        Returns:
            bool: True of the buffers are flushed, False otherwise.
        """
        return(self._port.Flush())
    

    # ------------ COMMAND DICT ACCESS ------------ ------------------------------------------------------------------------------------------------------------------------
        

    def GetDeviceCommands(self) -> dict[int, list[str|tuple[int]|bool]]:
        """Gets the dictionary containing the class instance's available POD commands.

        Returns:
            dict[int, list[str|tuple[int]|bool]]: Dictionary containing the available commands and their \
                information.Formatted as key(command number) : value([command name, number of argument \
                ASCII bytes, number of return bytes, binary flag ])
        """
        # Get commands from this instance's command dict object 
        return(self._commands.GetCommands())


    def SetBaudrateOfDevice(self, baudrate: int) -> bool : 
        """If the port is open, it will change the baud rate to the parameter's value.

        Args:
            baudrate (int): Baud rate to set for the open serial port. 

        Returns:
            bool: True if successful at setting the baud rate, false otherwise.
        """
        # set baudrate of the open COM port. Returns true if successful.
        return(self._port.SetBaudrate(baudrate))


    # ------------ SIMPLE POD PACKET COMPREHENSION ------------             ------------------------------------------------------------------------------------------------------------------------
    

    def UnpackPODpacket(self, msg: bytes) -> dict[str,bytes] : 
        """Determines if the packet is standard or binary, and unpacks accordingly. 

        Args:
            msg (bytes): Bytes string containing either a standard or binary packet

        Returns:
            dict[str,bytes]: A dictionary containing the unpacked message in bytes
        """
        # get command number 
        cmd = Packet_Standard.GetCommandNumber(msg) # same for standard and binary packets 
        if(self._commands.IsCommandBinary(cmd)):
            # message is binary 
            return(Packet_BinaryStandard.UnpackPODpacket_Binary(msg, self._commands))
        else:
            return(Packet_Standard.UnpackPODpacket_Standard(msg, self._commands))


    def TranslatePODpacket(self, msg: bytes) -> dict[str,int|bytes] : 
        """Determines if the packet is standard or binary, and translates accordingly. 

        Args:
            msg (bytes): Bytes string containing either a standard or binary packet.

        Returns:
            dict[str,int|bytes]: A dictionary containing the unpacked message in numbers.
        """
        # get command number 
        cmd = POD_Packets.AsciiBytesToInt(msg[1:5]) # same for standard and binary packets 
        if(self._commands.IsCommandBinary(cmd)):
            # message is binary 
            return(self.TranslatePODpacket_Binary(msg))
        else:
            return(Packet_Standard.TranslatePODpacket_Standard(msg, self._commands))
    

    # ------------ POD COMMUNICATION ------------   ------------------------------------------------------------------------------------------------------------------------


    def WriteRead(self, cmd: str|int, payload:int|bytes|tuple[int|bytes]=None, validateChecksum:bool=True) -> bytes :
        """Writes a command with optional payload to POD device, then reads (once) the device response.

        Args:
            cmd (str | int): Command number. 
            payload (int | bytes | tuple[int|bytes], optional): None when there is no payload. If there \
                is a payload, set to an integer value or a bytes string. Defaults to None.
            validateChecksum (bool, optional): Set to True to validate the checksum. Set to False to skip \
                    validation. Defaults to True.

        Returns:
            bytes: Bytes string containing a POD packet beginning with STX and ending with ETX. This may \
                be a standard packet, binary packet, or an unformatted packet (STX+something+ETX). 
        """
        self.WritePacket(cmd, payload)
        r = self.ReadPODpacket(validateChecksum)
        return(r)


    def GetPODpacket(self, cmd: str|int, payload:int|bytes|tuple[int|bytes]=None) -> bytes :
        """Builds a POD packet and writes it to a POD device via COM port. If an integer payload is give, \
        the method will convert it into a bytes string of the length expected by the command. If a bytes \
        payload is given, it must be the correct length. 

        Args:
            cmd (str | int): Command number. 
            payload (int | bytes | tuple[int | bytes], optional): None when there is no payload. If there \
                is a payload, set to an integer value, bytes string, or tuple. Defaults to None.

        Raises:
            Exception: POD command does not exist.
            Exception: POD command requires a payload.

        Returns:
            bytes: Bytes string of the POD packet. 
        """
        # return False if command is not valid
        if(not self._commands.DoesCommandExist(cmd)) : 
            raise Exception('POD command does not exist.')
        # get command number 
        if(isinstance(cmd,str)):
            cmdNum = self._commands.CommandNumberFromName(cmd)
        else: 
            cmdNum = cmd
        # get length of expected paylaod 
        argSizes = self._commands.ArgumentHexChar(cmdNum)
        # check if command requires a payload
        if( sum(argSizes) > 0 ): 
            # check to see if a payload was given 
            if(payload == None):
                raise Exception('POD command requires a payload.')
            # get payload in bytes
            pld = POD_Packets.PayloadToBytes(payload, argSizes)
        else :
            pld = None
        # build POD packet 
        packet = POD_Packets.BuildPODpacket_Standard(cmdNum, payload=pld)
        # return complete packet 
        return(packet)
    

    def WritePacket(self, cmd: str|int, payload:int|bytes|tuple[int|bytes]=None) -> Packet_Standard :
        """Builds a POD packet and writes it to the POD device. 

        Args:
            cmd (str | int): Command number.
            payload (int | bytes | tuple[int | bytes], optional): None when there is no payload. If there \
                is a payload, set to an integer value, bytes string, or tuple. Defaults to None.

        Returns:
            Packet_Standard: Packet that was written to the POD device.
        """
        # POD packet 
        packet = self.GetPODpacket(cmd, payload) 
        # write packet to serial port 
        self._port.Write(packet)
        # returns packet that was written
        return(Packet_Standard(packet, self._commands))


    def ReadPODpacket(self, validateChecksum:bool=True, timeout_sec: int|float = 5) -> bytes|Packet_Standard :
        """Reads a complete POD packet, either in standard or binary format, beginning with STX and \
        ending with ETX. Reads first STX and then starts recursion. 

        Args:
            validateChecksum (bool, optional): Set to True to validate the checksum. Set to False to \
                skip validation. Defaults to True.
            timeout_sec (int|float, optional): Time in seconds to wait for serial data. \
                Defaults to 5. 

        Returns:
            bytes|Packet_Standard: POD packet beginning with STX and ending with ETX. This \
                may be a standard packet, binary packet, or an unformatted packet (STX+something+ETX). 
        """
        # read until STX is found
        # print("readpod")
        b = None
        while(b != POD_Packets.STX()) :
            b = self._port.Read(1,timeout_sec)     # read next byte  
        # continue reading packet  
        packet = self._ReadPODpacket_Recursive(validateChecksum=validateChecksum)
        # return final packet
        return(packet)


    # ============ PROTECTED METHODS ============      ========================================================================================================================


    # ------------ POD COMMUNICATION ------------   ------------------------------------------------------------------------------------------------------------------------

    def _ReadPODpacket_Recursive(self, validateChecksum:bool=True) -> bytes|Packet_Standard : 
        """Reads the command number. If the command number ends in ETX, the packet is returned. \
        Next, it checks if the command is allowed. Then, it checks if the command is standard or \
        binary and reads accordingly, then returns the packet.

        Args:
            validateChecksum (bool, optional): Set to True to validate the checksum. Set to False to \
                skip validation. Defaults to True.

        Raises:
            Exception: Cannot read an invalid command.

        Returns:
            bytes|Packet_Standard: POD packet beginning with STX and ending with ETX. This may \
                be a standard packet, binary packet, or an unformatted packet (STX+something+ETX). 
        """
        # start packet with STX
        packet = POD_Packets.STX()
        # read next 4 bytes of the command number 
        cmd = self._Read_GetCommand(validateChecksum=validateChecksum)
        packet += cmd 
        # return packet if cmd ends in ETX
        if(cmd[len(cmd)-1].to_bytes(1,'big') == POD_Packets.ETX()) : 
            return(packet)
        # determine the command number
        cmdNum = POD_Packets.AsciiBytesToInt(cmd)
        # check if command number is valid
        if( not self._commands.DoesCommandExist(cmdNum) ) :
            raise Exception('Cannot read an invalid command: ', cmdNum)
        # then check if it is standard or binary
        if( self._commands.IsCommandBinary(cmdNum) ) : 
            # binary read
            packet = self._Read_Binary(prePacket=packet, validateChecksum=validateChecksum)
        else : 
            # standard read 
            packet = self._Read_Standard(prePacket=packet, validateChecksum=validateChecksum)
            packet = Packet_Standard(packet, self._commands)
        # return packet
        return(packet)


    def _Read_GetCommand(self, validateChecksum:bool=True) -> bytes : 
        """Reads one byte at a time up to 4 bytes to get the ASCII-encoded bytes command number. For each \
        byte read, it can (1) start the recursion over if an STX is found, (2) returns if ETX is found, or \
        (3) continue building the command number. 

        Args:
            validateChecksum (bool, optional): Set to True to validate the checksum. Set to False to skip \
                validation. Defaults to True.

        Returns:
            bytes: 4 byte long string containing the ASCII-encoded command number.
        """
        # initialize 
        cmd = None
        cmdCounter = 0
        # read next 4 bytes to get command number
        while(cmdCounter < 4) : 
            # read next byte 
            b = self._port.Read(1)
            cmdCounter += 1
            # build command packet 
            if(cmd == None) : 
                cmd = b
            else : 
                cmd += b
            # start over if STX is found 
            if(b == POD_Packets.STX() ) : 
                self._ReadPODpacket_Recursive(validateChecksu=validateChecksum)
            # return if ETX is found
            if(b == POD_Packets.ETX() ) : 
                return(cmd)
        # return complete 4 byte long command packet
        return(cmd)


    def _Read_ToETX(self, validateChecksum:bool=True) -> bytes : 
        """Reads one byte at a time until an ETX is found. It will restart the recursive read if an STX \
        is found anywhere. 

        Args:
            validateChecksum (bool, optional): Set to True to validate the checksum. Set to False to skip \
                validation. Defaults to True.

        Returns:
            bytes: Bytes string ending with ETX.
        """
        # initialize 
        packet = None
        b = None
        # stop reading after finding ETX
        while(b != POD_Packets.ETX()) : 
            # read next byte
            b = self._port.Read(1)
            # build packet 
            if(packet == None) : 
                packet = b
            else : 
                packet += b
            # start over if STX
            if(b == POD_Packets.STX()) : 
                self._ReadPODpacket_Recursive(validateChecksum=validateChecksum)
        # return packet
        return(packet)


    def _Read_Standard(self, prePacket: bytes, validateChecksum:bool=True) -> bytes :
        """Reads the payload, checksum, and ETX. Then it builds the complete standard POD packet in bytes. 

        Args:
            prePacket (bytes): Bytes string containing the beginning of a POD packet: STX (1 byte) \
                + command number (4 bytes).
            validateChecksum (bool, optional): Set to True to validate the checksum. Set to False to \
                skip validation. Defaults to True.

        Raises:
            Exception: An exception is raised if the checksum is invalid (only if validateChecksum=True).

        Returns:
            bytes: Bytes string for a complete standard POD packet.
        """
        # read until ETX 
        packet = prePacket + self._Read_ToETX(validateChecksum=validateChecksum)
        # check for valid  
        if(validateChecksum) :
            if( not self._ValidateChecksum(packet) ) :
                raise Exception('Bad checksum for standard POD packet read.')
        # return packet
        return(packet)


    def _Read_Binary(self, prePacket: bytes, validateChecksum:bool=True) -> bytes :
        """Reads the remaining part of the variable-length binary packet. It first reads the standard \
        packet (prePacket+payload+checksum+ETX). Then it determines how long the binary packet is from the \
        payload of the standard POD packet and reads that many bytes. It then reads to ETX to get the \
        checksum+ETX. 

        Args:
            prePacket (bytes): Bytes string containing the beginning of a POD packet: STX (1 byte) \
                + command number (4 bytes)
            validateChecksum (bool, optional): Set to True to validate the checksum. Set to False to \
                skip validation. Defaults to True.

        Raises:
            Exception: An exception is raised if the checksum is invalid (only if validateChecksum=True).

        Returns:
            bytes: Bytes string for a variable-length binary POD packet.
        """
        # Variable binary packet: contain a normal POD packet with the binary command, 
        #   and the payload is the length of the binary portion. The binary portion also 
        #   includes an ASCII checksum and ETX.        
         
        # read standard POD packet 
        startPacket = self._Read_Standard(prePacket, validateChecksum=validateChecksum)
        startDict   = Packet_Standard.UnpackPODpacket_Standard(startPacket)
        # get length of binary packet 
        numOfbinaryBytes = POD_Packets.AsciiBytesToInt(startDict['Payload'])
        # read binary packet
        binaryMsg = self._port.Read(numOfbinaryBytes) # read binary packet
        # read csm and etx
        binaryEnd = self._Read_ToETX(validateChecksum=validateChecksum)
        # build complete message
        packet = startPacket + binaryMsg + binaryEnd
        # check if checksum is correct 
        if(validateChecksum):
            csmCalc = POD_Packets.Checksum(binaryMsg)
            csm = binaryEnd[0:2]
            if(csm != csmCalc) : 
                raise Exception('Bad checksum for binary POD packet read.')
        # return complete variable length binary packet
        return(packet)

