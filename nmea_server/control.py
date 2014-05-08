import BV4111

class Controller(object):
    """Provides functionality for controlling the GPIO board"""

    def __init__(self):
        print "Initialising Relays..."
        sp = BV4111.sv3clV2_2.Connect("/dev/ttyAMA0",115200)
        Devd = BV4111.bv4111(sp,'d')

        # Querying relay state always fails first time, returning an empty string. Get that out of the way here.
        Devd.Send("i\r")
        Devd.Read()

        print "Relays initialised"

    def get_relay_state(self, relay):
        """Takes a relay number (1-8) and returns current state (0 or 1)"""
        
        Devd.Send("i\r")
        state = int(Devd.Read())
        mask = 1 << (relay-1) 
        if mask & state > 0:
            return 1
        else:
            return 0


    def toggle_lights(self):
        current_state = self.get_relay_state(8)
        if current_state == 1:
            Devd.Rly(8,0,0)
        else:
            Devd.Rly(8,1,0)
