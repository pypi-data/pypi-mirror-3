# -*- encoding: utf-8 -*-

import time
import traceback
import socket

from waitress.buffers import (
    OverflowableBuffer,
    ReadOnlyFileBasedBuffer,
    )

from waitress.parser import HTTPRequestParser

from waitress.task import (
    ErrorTask,
    WSGITask,
    )

from waitress.utilities import (
    InternalServerError,
    )

from waitress.adjustments import Adjustments

from ginsfsm.gobj import GObj
from ginsfsm.c_srv_sock import GServerSock

import logging
log = logging.getLogger(__name__)

#===============================================================
#                   HTTPChannel
#===============================================================


def ac_httpchannel_connected(self, event):
    print 'connected'
    self._n_connected_clisrv += 1
    channel = event.source[0]
    channel.server = self


def ac_httpchannel_disconnected(self, event):
    self._n_connected_clisrv -= 1
    self.destroy_gobj(event.source[-1])
    print 'disconnected'


def ac_httpchannel_rx_data(self, event):
    """
    Receives input: can be one or more requests to the channel.
    """
    #print 'recibo:', event.data
    # Do echo
    #self.send_event('EV_TX_DATA', event.source[-1], data=event.data)
    new_request = self._current_request
    requests = []
    data = event.data
    if not data:
        return

    while data:
        if new_request is None:
            new_request = HTTPRequestParser(self.adj)
        n = new_request.received(data)
        if new_request.expect_continue and new_request.headers_finished:
            # guaranteed by parser to be a 1.1 new_request
            new_request.expect_continue = False
            if not self.sent_continue:
                # there's no current task, so we don't need to try to
                # lock the outbuf to append to it.
                self.outbufs[-1].append(b'HTTP/1.1 100 Continue\r\n\r\n')
                self.sent_expect_continue = True
                self._flush_some()
                new_request.completed = False
        if new_request.completed:
            # The new_request (with the body) is ready to use.
            self._current_request = None
            if not new_request.empty:
                requests.append(new_request)
            new_request = None
        else:
            self._current_request = new_request
        if n >= len(data):
            break
        data = data[n:]

    """Execute all pending requests """
    channel = event.source[0]

    while requests:
        request = requests[0]
        if request.error:
            task = ErrorTask(channel, request)
        else:
            task = WSGITask(channel, request)
        try:
            task.service()
        except:
            log.exception('Exception when serving %s' %
                                  task.request.path)
            if not task.wrote_header:
                if self.adj.expose_tracebacks:
                    body = traceback.format_exc()
                else:
                    body = ('The server encountered an unexpected '
                            'internal server error')
                request = HTTPRequestParser(self.adj)
                request.error = InternalServerError(body)
                task = ErrorTask(channel, request)
                task.service() # must not fail
            else:
                task.close_on_finish = True
        # we cannot allow self.requests to drop to empty til
        # here; otherwise the mainloop gets confused
        if task.close_on_finish:
            self.close_when_flushed = True
            for request in requests:
                request._close()
            requests = []
        else:
            request = requests.pop(0)
            request._close()

    self.force_flush = True
    self.last_activity = time.time()


def ac_httpchannel_timeout(self, event):
    self.set_timeout(10)
    print "Server's clients: %d, connected %d" % (len(self.dl_childs),
                                                  self._n_connected_clisrv)


def ac_httpchannel_transmit_ready(self, event):
    pass


HTTP_CHANNEL_FSM = {
    'event_list': ('EV_TIMEOUT', 'EV_CONNECTED', 'EV_DISCONNECTED',
                   'EV_RX_DATA', 'EV_TRANSMIT_READY'),
    'state_list': ('ST_IDLE',),
    'machine': {
        'ST_IDLE':
        (
            ('EV_TIMEOUT',          ac_httpchannel_timeout,         'ST_IDLE'),
            ('EV_CONNECTED',        ac_httpchannel_connected,       'ST_IDLE'),
            ('EV_DISCONNECTED',     ac_httpchannel_disconnected,    'ST_IDLE'),
            ('EV_RX_DATA',          ac_httpchannel_rx_data,         'ST_IDLE'),
            ('EV_TRANSMIT_READY',   ac_httpchannel_transmit_ready,  'ST_IDLE'),
        ),
    }
}


class GWSGIServer(GObj):
    """  WSGI Server gobj.

    The incoming connections will create a new :class:`ginsfsm.c_sock.GSock`
    :term:`gobj`,
    that will be child of the :attr:`subscriber` :term:`gobj`.

        .. warning::  Remember destroy the accepted `gobj`
           with :func:`destroy_gobj` when the `gobj` has been disconnected.

           The `subcriber` knows when a new `gobj` has been accepted because it
           receives the ``'EV_CONNECTED'`` event.

           When the `subcriber` receives a ``'EV_DISCONNECTED'`` event must
           destroy the `gobj` because the connection ceases to exist.

    *Attributes:*
        * :attr:`application`: wsgi application.
          **Writable** attribute.
        * :attr:`host`: listening host.
          **Writable** attribute.
        * :attr:`port`: listening port.
          **Writable** attribute.
        * :attr:`origins`: list of (host, port) tuples allowed to connect from.
          **Writable** attribute.
          Default: ``None``. TODO.

    *Input-Events:*
        The relationship is directly between the
        accepted :class:`ginsfsm.c_sock.GSock` gobj and the :attr:`subscriber`.

        See :class:`ginsfsm.c_sock.GSock` `input-events`.

    *Output-Events:*
        The relationship is directly between the
        accepted :class:`ginsfsm.c_sock.GSock` gobj and the :attr:`subscriber`.

        See :class:`ginsfsm.c_sock.GSock` `output-events`.
    """

    def __init__(self):
        GObj.__init__(self, HTTP_CHANNEL_FSM)
        self.host = ''
        self.port = ''
        self.origins = None
        self.application = None   # wsgi application
        self._n_connected_clisrv = 0
        self._current_request = None      # current receiving request
        self.trace_dump = False

    def start_up(self):
        self.serversock = self.create_gobj(
            None,
            GServerSock,
            self,
            #TODO: must use adj, like waitress?
            subscriber=self,
            host=self.host,
            port=self.port,
            origins=self.origins,
            trace_dump=self.trace_dump,
        )

        self.adj = Adjustments() #TODO: need to integrate waitress style of params.
        self.effective_host, self.effective_port = self.getsockname()
        self.server_name = self.get_server_name(self.adj.host)

    def get_server_name(self, ip):
        """Given an IP or hostname, try to determine the server name."""
        if ip:
            server_name = str(ip)
        else:
            server_name = str(self.socketmod.gethostname())
        # Convert to a host name if necessary.
        for c in server_name:
            if c != '.' and not c.isdigit():
                return server_name
        try:
            if server_name == '0.0.0.0':
                return 'localhost'
            server_name = self.socketmod.gethostbyaddr(server_name)[0]
        except socket.error: # pragma: no cover
            pass
        return server_name

    def getsockname(self):
        return self.serversock.socket.getsockname()
