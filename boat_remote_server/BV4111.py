# Device BV4111
# Serial relay driver for up to 8 relays, relays are designated
# 'a' throug 'g'
#
#
import sv3clV2_2

class bv4111(sv3clV2_2.sv3):
    # ******************************************************************************
    # R E L A Y  S E C T I O N
    # ******************************************************************************
    
    # ------------------------------------------------------------------------------
    # For convenience the relay 'a' throug 'g' is translated to a number 1 to 8
    # example for use:
    # Rly(3,1,50) # turns on relay 'c' in 50mS
    # returns 0 on sucess
    # ------------------------------------------------------------------------------
    def Rly(self,rly,onn,when):
        #rly+96 convert 1 to 'a' etc.
        cmd = chr(rly+96)+str(onn)+","+str(when)+"\r"
        self.Send(cmd)
        return self.Wack()
    
    # ------------------------------------------------------------------------------
    # returns timer value (integer) for specified relay
    # this time relay is specifed 1 to 8
    # ------------------------------------------------------------------------------
    def Val(self,rly):
        self.Send("r"+str(rly)+"\r")
        return self.Read()
            
    # ------------------------------------------------------------------------------
    # all relays off
    # ------------------------------------------------------------------------------
    def Alloff():
        self.Send("o\r")
        return self.Wack()
    
