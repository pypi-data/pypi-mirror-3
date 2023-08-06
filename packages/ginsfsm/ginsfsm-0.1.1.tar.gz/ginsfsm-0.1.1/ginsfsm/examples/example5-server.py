""" Example5-server.
    Use GServerSock.
    Stress with many connections and many data. The server echo the data.
"""

from pprint import pprint
import logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

from ginsfsm.gobj import GObj
from ginsfsm.gaplic import GAplic
from ginsfsm.c_timer import GTimer
from ginsfsm.c_connex import GConnex
from ginsfsm.c_srv_sock import GServerSock

#===============================================================
#                   Server
#===============================================================
n_connected_clisrv = 0

def ac_clisrv_timeout(self, event):
    self.set_timeout(10)
    print "Server's clients: %d, connected %d" % (len(self.dl_childs), n_connected_clisrv)

def ac_clisrv_connected(self, event):
    global n_connected_clisrv
    n_connected_clisrv += 1

def ac_clisrv_disconnected(self, event):
    global n_connected_clisrv
    n_connected_clisrv -= 1
    self.destroy_gobj(event.source[-1])
    pass

def ac_clisrv_rx_data(self, event):
    #print 'recibo:', event.data
    # Do echo
    self.send_event('EV_TX_DATA', event.source[-1], data=event.data)

def ac_clisrv_transmit_ready(self, event):
    pass

SERVER_FSM = {
    'event_list': ('EV_TIMEOUT','EV_CONNECTED','EV_DISCONNECTED','EV_RX_DATA','EV_TRANSMIT_READY'),
    'state_list': ('ST_IDLE',),
    'machine': {
        'ST_IDLE':
        (
            ('EV_TIMEOUT',          ac_clisrv_timeout,         'ST_IDLE'),
            ('EV_CONNECTED',        ac_clisrv_connected,       'ST_IDLE'),
            ('EV_DISCONNECTED',     ac_clisrv_disconnected,    'ST_IDLE'),
            ('EV_RX_DATA',          ac_clisrv_rx_data,         'ST_IDLE'),
            ('EV_TRANSMIT_READY',   ac_clisrv_transmit_ready,  'ST_IDLE'),
        ),
    }
}

class GServerPrincipal(GObj):
    """  Server Principal gobj.
    """
    def __init__(self):
        GObj.__init__(self, SERVER_FSM)

    def start_up(self):
        self.timer = self.create_gobj(
            None,
            GTimer,
            self)
        self.set_timeout(5)
        self.set_trace_mach(False, pprint)

        self.server = self.create_gobj(
            None,
            GServerSock,
            self,
            host='0.0.0.0',
            port=8000)

    def set_timeout(self, seconds):
        self.timer.mt_set_timer(seconds=seconds)

    def clear_timeout(self):
        self.timer.mt_set_timer(seconds=-1)


#===============================================================
#                   Main
#===============================================================
if __name__ == "__main__":
    ga_srv = GAplic('ServerWorker')
    ga_srv.create_gobj('server', GServerPrincipal, None)

    try:
        ga_srv.mt_process()
    except KeyboardInterrupt:
        print('Program stopped')
