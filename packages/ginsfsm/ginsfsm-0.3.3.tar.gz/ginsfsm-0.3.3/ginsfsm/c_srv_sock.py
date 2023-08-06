# -*- encoding: utf-8 -*-
"""
GObj :class:`GServerSock`
=========================

GObj for manage server socket.

.. autoclass:: GServerSock
    :members:

"""
import logging
import socket
from ginsfsm.c_sock import (
    GSock,
    GSOCK_FSM,  # used in documentation
    GSOCK_GCONFIG,  # used in documentation
)


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

    .. ginsfsm::
       :fsm: GSOCK_FSM
       :gconfig: GSOCK_GCONFIG

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
        logging.info("Listening '%s' host '%s', port %d..." %
                 (self.name, self.host, self.port))
        self.listen(1024)

    def handle_accepted(self, sock, addr):
        # The socket options to set on receiving a connection.  It is a list of
        # (level, optname, value) tuples.  TCP_NODELAY disables the Nagle
        # algorithm for writes (Waitress already buffers its writes).
        # TODO: check origins for permitted source ip.
        socket_options = [
            (socket.SOL_TCP, socket.TCP_NODELAY, 1),
            ]
        for (level, optname, value) in socket_options:
            sock.setsockopt(level, optname, value)

        self._n_clisrv += 1
        if self.name and len(self.name):
            prefix_name = self.name
        else:
            prefix_name = None
        channel = '.clisrv-gsock-%x' % self._n_clisrv
        clisrv = self.create_gobj(
            prefix_name + channel if prefix_name else None,
            GSock,
            self.subscriber,
        )
        clisrv.subscribe_event(None, self.subscriber)
        clisrv.set_clisrv_socket(sock)
        clisrv.handle_connect()
