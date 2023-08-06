""" Example2.
    Use GSock. Connect to google, get /, and disconnect, periodically.
"""

from pprint import pprint
import logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

from ginsfsm.gobj import GObj
from ginsfsm.gaplic import GAplic
from ginsfsm.c_timer import GTimer
from ginsfsm.c_sock import GSock


query = "GET / HTTP/1.1\r\n" + \
    "Host: www.google.com\r\n" + \
    "\r\n"

def ac_connect(self, event):
    self.set_timeout(10)
    self.gsock.mt_connect()

def ac_connected(self, event):
    self.clear_timeout()
    self.set_timeout(2)

def ac_transmit(self, event):
    self.gsock.mt_send_data(query)
    self.set_timeout(2)

def ac_disconnect(self, event):
    print 'ac_disconnect()'
    self.gsock.mt_drop()
    self.set_timeout(2)

def ac_disconnected(self, event):
    print 'ac_disconnected()'
    #self.set_timeout(10)

def ac_rx_data(self, event):
    print 'ac_rx_data'
    #print event.kw['data']

def ac_timeout_connect(self, event):
    self.set_new_state('ST_DISCONNECTED')
    self.set_timeout(5)

SAMPLE_FSM = {
    'event_list': ('EV_CONNECT', 'EV_CONNECTED', 'EV_DISCONNECTED', 'EV_TIMEOUT',
                   'EV_RX_DATA', 'EV_TRANSMIT_READY'),
    'state_list': ('ST_DISCONNECTED', 'ST_WAIT_CONNECTED', 'ST_CONNECTED'),
    'machine': {
        'ST_DISCONNECTED':
        (
            ('EV_CONNECT',          ac_connect,         'ST_WAIT_CONNECTED'),
            ('EV_TIMEOUT',          ac_connect,         'ST_WAIT_CONNECTED'),
        ),
        'ST_WAIT_CONNECTED':
        (
            ('EV_CONNECTED',        ac_connected,       'ST_CONNECTED'),
            ('EV_DISCONNECTED',     ac_disconnected,    'ST_DISCONNECTED'),
            ('EV_TIMEOUT',          ac_timeout_connect, 'ST_WAIT_CONNECTED'),
        ),
        'ST_CONNECTED':
        (
            ('EV_DISCONNECTED',     ac_disconnected,    'ST_DISCONNECTED'),
            ('EV_TIMEOUT',          ac_disconnect,      'ST_CONNECTED'),
            ('EV_RX_DATA',          ac_rx_data,         'ST_CONNECTED'),
            ('EV_TRANSMIT_READY',   ac_transmit,        'ST_CONNECTED'),
        ),
    }
}

class GPrincipal(GObj):
    """  Principal gobj.
    """
    def __init__(self):
        GObj.__init__(self, SAMPLE_FSM)

    def start_up(self):
        """ Initialization zone."""
        self.timer = self.create_gobj(
            None,
            GTimer,
            self,
            timeout_event_name='EV_TIMEOUT')

        # You can receive the event by subscription or
        #    to directly to parent if you don't use subuscription
        if 0:
            self.timer.subscribe_event('EV_TIMEOUT', self)

        # You can set the timer with event or method:
        if 1:
            self.timer.mt_set_timer(seconds=1)
        else:
            self.send_event(self.timer, 'EV_SET_TIMER', seconds=1)

        self.gsock = self.create_gobj(
            None,
            GSock,
            self,
            connected_event_name='EV_CONNECTED',
            disconnected_event_name='EV_DISCONNECTED',
            #host='172.21.228.211', port=80
            host='www.google.com', port=80
            )
        self.set_trace_mach(True, pprint, level=-1)

    def set_timeout(self, seconds):
        self.timer.mt_set_timer(seconds=seconds)
        #self.send_event('EV_SET_TIMER', self.timer, seconds=seconds)

    def clear_timeout(self):
        self.timer.mt_set_timer(seconds=-1)
        #self.send_event('EV_SET_TIMER', self.timer, seconds=-1)

if __name__ == "__main__":
    ga = GAplic('Example2')
    ga.create_gobj('test_aplic', GPrincipal, None)
    try:
        ga.mt_process()
    except KeyboardInterrupt:
        print('Program stopped')
