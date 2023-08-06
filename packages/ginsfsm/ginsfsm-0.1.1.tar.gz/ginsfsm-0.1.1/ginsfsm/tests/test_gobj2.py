from pprint import pprint
import unittest

from ginsfsm.gobj import (
    GObj,
    EventNotAcceptedError,
    EventError,
    StateError,
    DestinationError,
    GObjError,
    QueueError,
    )

########################################################
#       Machine samples to test filters
########################################################
#******************************
#       Transmitter
#******************************
def ac_pulse(self, event):
    self.pulses_emitted += 1
    self.broadcast_event('EV_WAVEOUT', origin=self.pulses_emitted)

FSM_TRANSMITTER = {
    'output_list': ('EV_WAVEOUT',),
    'event_list': ('EV_PULSE',),
    'state_list': ('ST_IDLE',),
    'machine': {
        'ST_IDLE':
        (
            ('EV_PULSE', ac_pulse, None),
        ),
    }
}

def event_filter(value_returned_by_action):
    if value_returned_by_action is True:
        return True
    return False

class TransmitterGObj(GObj):
    def __init__(self):
        GObj.__init__(self, FSM_TRANSMITTER)

    def start_up(self):
        ''' Create gobj childs, initialize something...
        '''
        self.pulses_emitted = 0
        self.set_owned_event_filter(event_filter)

#******************************
#       Receptor
#******************************
def ac_wave(self, event):
    if event.origin == self.mymod:
        print("    MINE %s! pulse %s" % (self.name, event.origin))
        self.count += 1
        return True
    return False

FSM_RECEPTOR = {
    'event_list': ('EV_WAVEOUT',),
    'state_list': ('ST_IDLE',),
    'machine': {
        'ST_IDLE':
        (
            ('EV_WAVEOUT', ac_wave, None),
        ),
    }
}

class ReceptorGObj(GObj):
    def __init__(self):
        GObj.__init__(self, FSM_RECEPTOR)
        """ Attributes"""
        self.transmitter = None
        self.mymod = 0
        """ End Attributes"""
        self.count = 0

    def start_up(self):
        ''' Create gobj childs, initialize something...
        '''
        self.transmitter.subscribe_event('EV_WAVEOUT', self)

#******************************
#       Principal
#******************************
class PrincipalGObj(GObj):
    def __init__(self):
        GObj.__init__(self, {})
        self.start_up()

    def start_up(self):
        ''' Create gobj childs, initialize something...
        '''
        self.transmitter = self.create_gobj('Trasmitter', TransmitterGObj, self)
        self.receptor_list = list(range(4))
        for idx in list(range(4)):
            self.receptor_list[idx] = self.create_gobj('Receptor%d' % (idx+1),
                ReceptorGObj, self, transmitter=self.transmitter, mymod=idx+1)
        self.set_trace_mach(True, pprint, level=-1)
        #for idx in range(4):
        #    self.send_event(self.transmitter, 'EV_PULSE')

########################################################
#       Tests
########################################################

class TestGObj2(unittest.TestCase):
    def setUp(self):
        self.principal = PrincipalGObj()

    def test_owned_event_filter(self):
        self.principal.send_event(self.principal.transmitter, 'EV_PULSE')
        self.assertEqual(self.principal.receptor_list[0].count, 1)
        self.assertEqual(self.principal.receptor_list[1].count, 0)
        self.assertEqual(self.principal.receptor_list[2].count, 0)
        self.assertEqual(self.principal.receptor_list[3].count, 0)
        self.principal.send_event(self.principal.transmitter, 'EV_PULSE')
        self.assertEqual(self.principal.receptor_list[0].count, 1)
        self.assertEqual(self.principal.receptor_list[1].count, 1)
        self.assertEqual(self.principal.receptor_list[2].count, 0)
        self.assertEqual(self.principal.receptor_list[3].count, 0)
        self.principal.send_event(self.principal.transmitter, 'EV_PULSE')
        self.assertEqual(self.principal.receptor_list[0].count, 1)
        self.assertEqual(self.principal.receptor_list[1].count, 1)
        self.assertEqual(self.principal.receptor_list[2].count, 1)
        self.assertEqual(self.principal.receptor_list[3].count, 0)
        self.principal.send_event(self.principal.transmitter, 'EV_PULSE')
        self.assertEqual(self.principal.receptor_list[0].count, 1)
        self.assertEqual(self.principal.receptor_list[1].count, 1)
        self.assertEqual(self.principal.receptor_list[2].count, 1)
        self.assertEqual(self.principal.receptor_list[3].count, 1)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
