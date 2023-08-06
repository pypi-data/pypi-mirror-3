""" Example3.
    Use GConnex. Send a query to google and twitter alternatively.
    How? send the query each 10 seconds, but set a timeout_inactivity of 5.
    In each disconnection the next connection will swing between the
    two destinations.
"""

from pprint import pprint
import logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

from ginsfsm.gobj import GObj
from ginsfsm.gaplic import GAplic
from ginsfsm.c_timer import GTimer
from ginsfsm.c_connex import GConnex

query = "GET / HTTP/1.1\r\n" + \
    "Host: www\r\n" + \
    "\r\n"

def ac_rx_data(self, event):
    print 'ac_rx_data'
    #print event.kw['data']

def ac_timeout(self, event):
    self.set_timeout(10)
    self.send_event(self.connex, 'EV_TX_DATA', data=query)


SAMPLE_FSM = {
    'event_list': ('EV_TIMEOUT', 'EV_RX_DATA'),
    'state_list': ('ST_IDLE',),
    'machine': {
        'ST_IDLE':
        (
            ('EV_TIMEOUT',          ac_timeout,         'ST_IDLE'),
            ('EV_RX_DATA',          ac_rx_data,         'ST_IDLE'),
        ),
    }
}

class GPrincipal(GObj):
    """  Principal gobj.
    """
    def __init__(self):
        GObj.__init__(self, SAMPLE_FSM)

    def start_up(self):
        self.timer = self.create_gobj(
            'principal_timer',
            GTimer,
            self,
            timeout_event_name='EV_TIMEOUT')

        self.connex = self.create_gobj(
            'connex',
            GConnex,
            self,
            destinations=[('www.google.es',80),('www.twitter.com',80)],
            timeout_inactivity=5,
            connected_event_name=None,
            disconnected_event_name=None,
            transmit_ready_event_name=None,
            )
        self.set_timeout(5)
        self.set_trace_mach(True, pprint, level=-1)

    def set_timeout(self, seconds):
        self.timer.mt_set_timer(seconds=seconds)

    def clear_timeout(self):
        self.timer.mt_set_timer(seconds=-1)

if __name__ == "__main__":
    ga = GAplic('Example3')
    ga.create_gobj('test_aplic', GPrincipal, None)
    try:
        ga.mt_process()
    except KeyboardInterrupt:
        print('Program stopped')
