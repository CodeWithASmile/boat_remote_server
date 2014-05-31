# sv3clV2_2.py
#
# Verion 2.0  Implemented as a class separate from the serial connection
#   2.1 16/2/13: Changed how Wack works
#   2.2 23/7/13: Changes to the SV3 protocol
#       SV3 now default to 115200 Baud not autobaud 
#       Added 'H' command to discover devices.
#
# sv3 protocol for ByVac SV3 serial devices. This code can be imported for
# the required device. It contains the common commands and also has a small
# program for setting up the eeprom values.
#
# The serial communication in Python is by defualt text, text is sent and text
# is recieved so in the following code chr() and ord() is used to do the
# conversions
#
# To keep the code simple and easy to read, no range checking is done, you may
# want to add this later.
#
# Only connect 1 device when using the eeprom and some other commands.
#
import serial
from time import sleep
BAUD_RATES = { 2400:1, 4800:2, 9600:3, 14400:4, 19200:5, 38400:6, 115200:7 } 

# ------------------------------------------------------------------------------
# returns the comport connector for use with class. Can only open one instance
# of a serial connection so this has to be used accross classes when there
# is more than one device on the serial bus
# ------------------------------------------------------------------------------
def Connect(port,baud):
    return serial.Serial(port, baud, timeout=.05, stopbits=1, parity='N' )


# ------------------------------------------------------------------------------
# The class does not contain the serial connection but must be passed it. This
# enables more than one device on any serial bus
# ------------------------------------------------------------------------------
class   sv3:
    """SV3 Device Protocol ByVac Version 2.2"""
    sp = None   # sp is set to communication device by Init()
    adr = None # address is the address of the device this instance is addressing
    def __init__(self,com,address,ack='\006'):
        self.sp = com # communication instance
        self.adr = ord(address) # address of device for this instance
        self.ack = ack 
        
    # --------------------------------------------------------------------------
    # commands always start with address, this will send the address followed
    # by the string. NOTE it is up to the caller to supply the \r and Wack
    # --------------------------------------------------------------------------
    def Send(self,str):
        self.sp.flushInput()
        self.sp.write(chr(self.adr))
        self.sp.write(str)

    # --------------------------------------------------------------------------
    # nearly all commands ACK when finished
    # Will wait for ACK and return 0 if not received
    # --------------------------------------------------------------------------
    def Wack(self):
        k = None
        while k != '':
            k = self.sp.read(1)
            if k == '':
                return 0
            elif k == self.ack:
                return 1
        
    # --------------------------------------------------------------------------
    # reads characters up to ACK and returns them
    # note will return a string
    # --------------------------------------------------------------------------
    def Read(self):
        k = ''
        v = ''
        timeout = 100
        while k != self.ack:
            k = self.sp.read(1)
            if len(k) == 0: # timeout
                timeout-=1
                if timeout <= 0:
                    break
                else:
                    continue
            if k != self.ack:
                v = v + k
        return v

    # --------------------------------------------------------------------------
    # returns device ID as an integer
    # --------------------------------------------------------------------------
    def ID(self):
        self.Send('D')
        self.sp.write('\r')
        return self.Read()

    # --------------------------------------------------------------------------
    # returns firmware value as a string in the form "h.l"
    # --------------------------------------------------------------------------
    def Firmware(self):
        self.Send('V')
        self.sp.write('\r')
        return self.Read()

    # --------------------------------------------------------------------------
    # reset, will need initialising again
    # --------------------------------------------------------------------------
    def Reset(self):
        self.Send('c')
        self.sp.write('\r')
        sleep(0.5)

    # --------------------------------------------------------------------------
    # Returns 1 if the device is listening, can also be called a few times
    # Command H introduced 23 July 2013
    # --------------------------------------------------------------------------
    def Active(self):
        self.Send('H')
        self.sp.write('\r')
        return self.Wack()

    # ------------------------------------------------------------------------------
    # EEPROM utilities
    # ------------------------------------------------------------------------------
    # --------------------------------------------------------------------------
    # reads the eeprom from eeprom address to eprom address
    # --------------------------------------------------------------------------
    def ReadEE(self,bfrom,bto):
        self.Send('R')
        self.sp.write(str(bfrom)+',') # comma delimiter
        self.sp.write(str(bto))
        self.sp.write('\r')
        rv = self.Read()
        return rv.split(',')

    # --------------------------------------------------------------------------
    # write a single value to eeprom
    # location is the address of the eeprom that
    # will have the range 0 to 255 - no checking is done.
    # all integers
    # returns 1 on sucesws
    # --------------------------------------------------------------------------
    def WriteEE(self,location,value):
        cmd = "W"+str(location)+","+str(value)+"\r"
        print cmd
        self.Send(cmd)
        return self.Wack()

    # --------------------------------------------------------------------------
    # change device address
    # address is an integer
    # --------------------------------------------------------------------------
    def ChangeAddress(self,adr):
        return self.WriteEE(1,adr)
    
    # --------------------------------------------------------------------------
    # change ACK
    # ACK is an integer
    # --------------------------------------------------------------------------
    def ChangeAck(self,ack):
        self.WriteEE(2,ack)
        self.ack = ack
        sleep(0.5)

    # --------------------------------------------------------------------------
    # change Baud rate 2400 to 115200 or 0
    # returns 1 on sucess
    # --------------------------------------------------------------------------
    def ChangeBaud(self,baud):
        if baud == 0:
            self.WriteEE(4,0)
        else:
            try:
                br = BAUD_RATES[baud]
                self.WriteEE(4,br)
                self.Wack()
                return 1
            except:
                return 0

    # --------------------------------------------------------------------------
    # discover devices on bus
    # --------------------------------------------------------------------------
    def Discover(self):
        devices = []
        self.sp.flushInput()
        for j in range(97,120):
            self.sp.write(chr(j)+"H\r")
            if self.Wack() != 0:
                devices.append(chr(j))
                # get ID
                self.sp.flushInput()
                self.sp.write(chr(j)+"D\r") # device id
                tmp = self.Read()
                devices.append(tmp)
                # get firmware
                self.sp.flushInput()
                self.sp.write(chr(j)+"V\r") # firmware version
                tmp = self.Read()
                devices.append(tmp)
        return devices