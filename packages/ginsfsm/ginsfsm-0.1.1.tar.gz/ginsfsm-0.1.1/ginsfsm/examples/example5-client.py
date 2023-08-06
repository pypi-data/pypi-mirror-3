""" Example5-client.
    Use GConnex.
    Stress with many connections and many data. The server echo the data.
"""

import argparse
import datetime
from pprint import pprint
import logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

from ginsfsm.gobj import GObj
from ginsfsm.gaplic import GAplic
from ginsfsm.c_sock import GSock
from ginsfsm.c_timer import GTimer
from ginsfsm.c_connex import GConnex
from ginsfsm.c_srv_sock import GServerSock

#===============================================================
#                   Client
#===============================================================
query = "GET / HTTP/1.1\r\n" + \
    "Host: \r\n" + \
    "\r\n"

def ac_client_timeout(self, event):
    if self.connex is None:
        self.connex = range(CONNECTIONS)

    if self.n_clients < CONNECTIONS:
        for i in range(self.n_clients, CONNECTIONS):
            self.n_clients += 1
            self.connex[i] = self.create_gobj(
                'client-%d' % i,
                GConnex, #GSock,
                self,
                destinations=[(host,port)],
                idx=i,
                conectado=0,
                sended_msgs=0,
                received_msgs=0,
            )
            #self.connex[i].mt_connect(host='172.21.228.211', port=8084)
            #ret = self.connex[i].mt_connect(host='127.0.0.1', port=8000) #8082
            #if not ret:
            #    break
    print "conectados: %d" % self.n_connected_clients
    if self.n_connected_clients == CONNECTIONS:
        n_echoes = 0
        n_total = 0
        diff = datetime.timedelta(seconds=0)
        for cli in self.connex:
            #print 'cli %d txed_msgs %d, rxed_msgs %d' % (cli.idx, cli.gsock.txed_msgs, cli.gsock.rxed_msgs)
            if cli.gsock.rxed_msgs == cli.gsock.txed_msgs:
                n_total += 1
            if cli.sended_msgs == cli.received_msgs:
                n_echoes += 1
            diff += self.diff
        print "Echoes OK: %d of %d, taverage %s" % (n_echoes, CONNECTIONS, diff/CONNECTIONS)

        for cli in self.connex:
            if cli.gsock.connected:
                cli.sended_msgs = 1
                cli.received_msgs = 0
                cli.tx_time = datetime.datetime.now()
                self.send_event(cli, 'EV_TX_DATA', data=query) #data="HOLA")

    self.set_timeout(10)

def ac_client_connected(self, event):
    if not event.source[-1].conectado:
        self.n_connected_clients += 1
        event.source[-1].conectado = 1
    print "C: conectados: %d" % self.n_connected_clients

def ac_client_disconnected(self, event):
    if event.source[-1].conectado:
        self.n_connected_clients -= 1
        event.source[-1].conectado = 0
    print "D: conectados: %d" % self.n_connected_clients

def ac_client_rx_data(self, event):
    cli = self.connex[event.source[-1].idx]
    cli.received_msgs += 1
    cli.rx_time = datetime.datetime.now()
    diff = cli.rx_time - cli.tx_time
    if diff < self.min_response_time:
        self.min_response_time = diff
    if diff > self.max_response_time:
        self.max_response_time = diff
    self.diff = diff
    #print 'recibo:', event.data
    #print 'diff %s, min %s, max %s' % (diff, self.min_response_time, self.max_response_time)

def ac_client_transmit_ready(self, event):
    pass

CLIENT_FSM = {
    'event_list': ('EV_TIMEOUT','EV_CONNECTED','EV_DISCONNECTED','EV_RX_DATA','EV_TRANSMIT_READY'),
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
        self.n_clients = 0
        self.n_connected_clients = 0

    def start_up(self):
        self.timer = self.create_gobj(
            None,
            GTimer,
            self
        )
        self.set_timeout(1)
        self.set_trace_mach(False, pprint)
        self.connex = None
        self.sended_msgs = 0
        self.received_msgs = 0
        self.min_response_time = datetime.timedelta(seconds=100)
        self.max_response_time = datetime.timedelta(seconds=0)
        self.diff = datetime.timedelta(seconds=0)

    def set_timeout(self, seconds):
        self.timer.mt_set_timer(seconds=seconds)

    def clear_timeout(self):
        self.timer.mt_set_timer(seconds=-1)


#===============================================================
#                   Main
#===============================================================
if __name__ == "__main__":
    global host, port, CONNECTIONS

    parser = argparse.ArgumentParser(description='Client/Server stress.')
    parser.add_argument('CONNECTIONS',  action='store_const', const=500,
                       help='number of connections')
    parser.add_argument('host', action='store_const', const='127.0.0.1',
                       help='host')
    parser.add_argument('port', action='store_const', const=8000,
                       help='host')

    args = parser.parse_args()

    host = args.host
    port = args.port
    CONNECTIONS = args.CONNECTIONS

    ga_cli = GAplic('ClientWorker')
    ga_cli.create_gobj('client', GClientPrincipal, None)

    try:
        ga_cli.mt_process()
    except (KeyboardInterrupt, SystemExit):
        from ginsfsm.c_sock import close_all_sockets
        close_all_sockets(ga_cli._socket_map)
        print('Program stopped')
