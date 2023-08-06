""" Example4.
    Use GServerSock and GConnex.
    Run two gaplics. One is the server, the other the client.
    Stress with many connections and many data. The server echo the data.
    Configure:
        * The server can run as thread o child process.
        * Maximum number of client connections.
"""

import argparse
import logging
from pprint import pprint
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
def ac_clisrv_timeout(self, event):
    self.set_timeout(5)
    pass

def ac_clisrv_connected(self, event):
    print 'connected FROM %s' % str(event.peername)
    print "Server's clients: %d" % len(self.dl_childs)

def ac_clisrv_disconnected(self, event):
    pass

def ac_clisrv_rx_data(self, event):
    pass

def ac_clisrv_transmit_ready(self, event):
    pass

SERVER_FSM = {
    'event_list': ('EV_TIMEOUT','EV_CONNECTED','EV_DISCONNECTED','EV_RX_DATA',
                   'EV_TRANSMIT_READY'),
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

        self.server = self.create_gobj(
            None,
            GServerSock,
            self,
            host='127.0.0.1',
            port=8000)
        self.set_trace_mach(True, pprint, level=-1)

    def set_timeout(self, seconds):
        self.timer.mt_set_timer(seconds=seconds)

    def clear_timeout(self):
        self.timer.mt_set_timer(seconds=-1)

#===============================================================
#                   Client
#===============================================================

def ac_client_timeout(self, event):
    if self.connex is None:
        self.connex = range(CONNECTIONS)
        for i in self.connex:
            self.connex[i] = self.create_gobj(
                'client-%02d' % i,
                GConnex,
                self,
                destinations=[('127.0.0.1',8000)],
            )
    self.set_timeout(10)

def ac_client_connected(self, event):
    #print 'connected TO %s' % str(event.peername)
    #print "conectados: %d" % len(self.dl_childs)
    pass

def ac_client_disconnected(self, event):
    pass

def ac_client_rx_data(self, event):
    pass

def ac_client_transmit_ready(self, event):
    pass

CLIENT_FSM = {
    'event_list': ('EV_TIMEOUT','EV_CONNECTED','EV_DISCONNECTED','EV_RX_DATA',
                   'EV_TRANSMIT_READY'),
    'state_list': ('ST_IDLE',),
    'machine': {
        'ST_IDLE':
        (
            ('EV_TIMEOUT',          ac_client_timeout,         'ST_IDLE'),
            ('EV_CONNECTED',        ac_client_connected,       'ST_IDLE'),
            ('EV_DISCONNECTED',     ac_client_disconnected,    'ST_IDLE'),
            ('EV_RX_DATA',          ac_client_rx_data,         'ST_IDLE'),
            ('EV_TRANSMIT_READY',   ac_client_transmit_ready,  'ST_IDLE'),
        ),
    }
}

class GClientPrincipal(GObj):
    """  Client Principal gobj.
    """
    def __init__(self):
        GObj.__init__(self, CLIENT_FSM)

    def start_up(self):
        self.timer = self.create_gobj(
            None,
            GTimer,
            self
        )
        self.set_timeout(1)
        self.connex = None
        self.set_trace_mach(True, pprint, level=-1)

    def set_timeout(self, seconds):
        self.timer.mt_set_timer(seconds=seconds)

    def clear_timeout(self):
        self.timer.mt_set_timer(seconds=-1)


#===============================================================
#                   Main
#===============================================================
from ginsfsm.gaplic import start_gaplic_thread, start_gaplic_process

if __name__ == "__main__":
    global CONNECTIONS, run_as_process

    parser = argparse.ArgumentParser(description='Client/Server stress.')
    parser.add_argument('CONNECTIONS',  action='store_const', const=100,
                       help='number of connections')
    parser.add_argument('run_as_process', action='store_false',
                       help='Run as process')

    #TODO: bad args
    args = parser.parse_args()
    CONNECTIONS = args.CONNECTIONS
    run_as_process = args.run_as_process

    if run_as_process:
        # run server gaplic as child daemon process
        ga_srv = GAplic('ServerProcess')
        ga_srv.create_gobj('server', GServerPrincipal, None)
        srv_worker = start_gaplic_process(ga_srv)

        # run client gaplic as main process
        ga_cli = GAplic('ClientProcess')
        ga_cli.create_gobj('client', GClientPrincipal, None)

        try:
            ga_cli.mt_process()
        except KeyboardInterrupt:
            srv_worker.shutdown()
            srv_worker.join()
            print('Program stopped')
    else:
        # run server gaplic as thread
        ga_srv = GAplic('ServerWorker')
        ga_srv.create_gobj('server', GServerPrincipal, None)
        srv_worker = start_gaplic_thread(ga_srv)

        # run client gaplic as main process
        ga_cli = GAplic('ClientWorker')
        ga_cli.create_gobj('client', GClientPrincipal, None)

        try:
            ga_cli.mt_process()
        except KeyboardInterrupt:
            srv_worker.shutdown()
            srv_worker.join()
            print('Program stopped')
