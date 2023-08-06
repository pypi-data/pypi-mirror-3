# -*- encoding: utf-8 -*-

import socket
from ginsfsm.c_sock import GSock

import logging
log = logging.getLogger(__name__)

class GServerSock(GSock):
    """  Server socket gobj.
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
        * :attr:`subscriber`: parent of the connected clients and
          subcriber of all output-events from connected clients.
          **Writable** attribute.
          Default is ``None``, i.e., the parent of GServerSock gobj.
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
        GSock.__init__(self)
        self.subscriber = None
        self.host = ''
        self.port = ''
        self.origins = None

        self._n_clisrv = 0

    def start_up(self):
        """ Initialization zone.

        Start listen to (host,port).
        """
        if self.subscriber is None:
            self.subscriber = self.parent
        self.do_listen()

    def do_listen(self):
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((self.host, self.port))
        log.info("Listening '%s' host '%s', port %d..." %
                 (self.name, self.host, self.port))
        self.listen(5)

    def handle_accepted(self, sock, addr):
        self._n_clisrv += 1
        clisrv = self.create_gobj(
            'clisrv-%d' % self._n_clisrv,
            GSock,
            self.subscriber,
        )
        clisrv.subscribe_event(None, self.subscriber)
        clisrv.set_clisrv_socket(sock)
        clisrv.handle_connect()
