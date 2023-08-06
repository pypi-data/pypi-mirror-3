# -*- encoding: utf-8 -*-

from collections import deque

import logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

from ginsfsm.gobj import GObj
from ginsfsm.c_timer import GTimer
from ginsfsm.c_sock import GSock

def ac_timeout_disconnected(self, event):
    if self.timeout_inactivity > 0:
        pass # don' connect until arrives data to transmit
    else:
        self.connect()

def ac_disconnected(self, event):
    self.set_timeout(self.timeout_between_connections)
    if self.disconnected_event_name is not None:
        event.event_name = self.disconnected_event_name
        self.broadcast_event(event)

def ac_timeout_wait_connected(self, event):
    self.set_timeout(self.timeout_between_connections)

def ac_connected(self, event):
    self.clear_timeout()
    if self.timeout_inactivity > 0:
        self.set_timeout(self.timeout_inactivity)
    self.process_dl_tx_data()
    if self.connected_event_name is not None:
        event.event_name = self.connected_event_name
        self.broadcast_event(event)

def ac_rx_data(self, event):
    if self.timeout_inactivity > 0:
        self.set_timeout(self.timeout_inactivity)
    if self.rx_data_event_name is not None:
        event.event_name = self.rx_data_event_name
        self.broadcast_event(event)

def ac_timeout_data(self, event):
    self._gsock.mt_drop()

def ac_tx_data(self, event):
    if self.timeout_inactivity > 0:
        self.set_timeout(self.timeout_inactivity)
    self._gsock.mt_send_data(event.kw['data'])

def ac_enqueue_tx_data(self, event):
    self._dl_tx_data.append(event)
    # try to connect, if this function called, is because we are disconnected.
    self.connect()

def ac_transmit_ready(self, event):
    if self.transmit_ready_event_name is not None:
        event.event_name = self.transmit_ready_event_name
        self.broadcast_event(event)

CONNEX_FSM = {
    'output_list': ('EV_CONNECTED', 'EV_DISCONNECTED',
                    'EV_RX_DATA', 'EV_TRANSMIT_READY'),
    'event_list': ('EV_CONNECTED', 'EV_DISCONNECTED', 'EV_TIMEOUT',
                   'EV_RX_DATA', 'EV_TX_DATA', 'EV_TRANSMIT_READY'),
    'state_list': ('ST_DISCONNECTED', 'ST_WAIT_CONNECTED', 'ST_CONNECTED'),
    'machine': {
        'ST_DISCONNECTED':
        (
            ('EV_TIMEOUT',       ac_timeout_disconnected,  None),
            ('EV_TX_DATA',       ac_enqueue_tx_data,       'ST_DISCONNECTED'),
        ),
        'ST_WAIT_CONNECTED':
        (
            ('EV_CONNECTED',     ac_connected,             'ST_CONNECTED'),
            ('EV_DISCONNECTED',  ac_disconnected,          'ST_DISCONNECTED'),
            ('EV_TIMEOUT',       ac_timeout_wait_connected,'ST_DISCONNECTED'),
            ('EV_TX_DATA',       ac_enqueue_tx_data,       'ST_WAIT_CONNECTED'),
        ),
        'ST_CONNECTED':
        (
            ('EV_DISCONNECTED',  ac_disconnected,          'ST_DISCONNECTED'),
            ('EV_TIMEOUT',       ac_timeout_data,          'ST_CONNECTED'),
            ('EV_RX_DATA',       ac_rx_data,               'ST_CONNECTED'),
            ('EV_TX_DATA',       ac_tx_data,               'ST_CONNECTED'),
            ('EV_TRANSMIT_READY',ac_transmit_ready,        'ST_CONNECTED'),
        ),
    }
}

class GConnex(GObj):
    """  GConnex gobj.
    Responsible for maintaining the client socket connected, or not.
    It can maintain the connection closed, until new data arrived.
    It can have several destinations to connect.

    *Attributes:*
        * :attr:`subscriber`: subcriber gobj of enabled :term:`output-event`'s.
          **Writable** attribute.
          Default is ``None``, i.e., the parent:
          see :meth:`start_up`.
        * :attr:`destinations`: list of destination (host,port) tuples.
          **Writable** attribute.
        * :attr:`timeout_between_connections`: idle timeout to wait between
          attempts of connection.
          **Writable** attribute.
          Default: 5 seconds.
        * :attr:`timeout_inactivity`: inactivity timeout to close the
          connection. Reconnect when new data arrived.
          **Writable** attribute.
          Default: -1 (never close).
        * :attr:`connected_event_name`: name of connected event.
          **Writable** attribute.
          Default: ``'EV_CONNECTED'``. `None` if you want ignore the event.
        * :attr:`disconnected_event_name`: name of disconnected event.
          **Writable** attribute.
          Default: ``'EV_DISCONNECTED'``. `None` if you want ignore the event.
        * :attr:`transmit_ready_event_name`: name of transmit_ready event.
          **Writable** attribute.
          Default: ``'EV_TRANSMIT_READY'``. `None` if you want ignore the event.
        * :attr:`rx_data_event_name`: name of received data event.
          **Writable** attribute.
          Default: ``'EV_RX_DATA'``. `None` if you want ignore the event.
          (sure?!).

    *Input-Events:*
        * :attr:`'EV_TX_DATA'`: transmit ``event.data``.

          Mandatory attributes of the received :term:`event`:

          * ``data``: data to send.

    *Output-Events:*
        * :attr:`'EV_CONNECTED'`: socket connected.

          Attributes added to the sent :term:`event`:

            * ``peername``: remote address to which the socket is connected.
            * ``sockname``: the socket’s own address.

        * :attr:`'EV_DISCONNECTED'`: socket disconnected.
        * :attr:`'EV_TRANSMIT_READY'`: socket ready to transmit more data.
        * :attr:`'EV_RX_DATA'`: data received.
          Attributes added to the sent :term:`event`:

            * ``data``: Data received from remote address.

    """
    def __init__(self):
        GObj.__init__(self, CONNEX_FSM)
        self.destinations = [('', 0)]
        self.subscriber = None
        self.timeout_waiting_connected = 60
        self.timeout_between_connections = 5
        self.timeout_inactivity = -1
        self.connected_event_name = 'EV_CONNECTED'
        self.disconnected_event_name = 'EV_DISCONNECTED'
        self.transmit_ready_event_name = 'EV_TRANSMIT_READY'
        self.rx_data_event_name = 'EV_RX_DATA'

        self._dl_tx_data = deque()   # queue for tx data.
        self._timer = None
        self._gsock = None
        self._idx_dst = 0

    def start_up(self):
        """ Initialization zone.

        Subcribe all enabled :term:`output-event`'s to ``subscriber``
        with this sentence::

            self.subscribe_event(None, self.subscriber)
        """
        self.subscribe_event(None, self.subscriber)
        # select the event'names.
        # If some name is None then parent don't want receive it.
        self._gsock = self.create_gobj(
            self.name,
            GSock,
            self,
        )
        self._gsock.get_next_dst = self.get_next_dst

        self._timer = self.create_gobj(
            'connex_timer',
            GTimer,
            self,
            timeout_event_name='EV_TIMEOUT')
        self.set_timeout(self.timeout_between_connections)

    def set_timeout(self, seconds):
        self._timer.mt_set_timer(seconds=seconds)

    def clear_timeout(self):
        self._timer.mt_set_timer(seconds=-1)

    def connect(self):
        self.set_new_state('ST_WAIT_CONNECTED')
        self.set_timeout(self.timeout_waiting_connected)
        self._gsock.mt_connect()

    def get_next_dst(self):
        """ Return the destination (host,port) tuple to connect from
        the ``destinations`` attribute.
        If there are multiple tuples in ``destinations`` attribute,
        try to connect to each tuple cyclically.
        Override :meth:`ginsfsm.c_sock.GSock.get_next_dst`.
        """
        host, port = self.destinations[self._idx_dst]
        self._idx_dst += 1
        if self._idx_dst >= len(self.destinations):
            self._idx_dst = 0
        return (host, port)

    def process_dl_tx_data(self):
        while True:
            try:
                event = self._dl_tx_data.popleft()
            except IndexError:
                break
            else:
                self._gsock.mt_send_data(event.kw['data'])
