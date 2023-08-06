# -*- encoding: utf-8 -*-

# ======================================================================
#   Copyright 2012 by Gines Martinez
#   Code inspired in asyncore.py and tornado.
# ======================================================================

""" GSock GObj. Manage socket events.

    .. graphviz::

        digraph GSock {
            size="4.0"
            graph [splines=true overlap=false rankdir="LR"];
            node [penwidth=2 style=filled fillcolor="lightgray"];

            subgraph cluster_parent {
                label="Parent GObj";
                "FSM" [shape=box];
            }
            "FSM" -> "ST_IDLE" [label="mt_connect()"];
            "FSM" -> "ST_IDLE" [label="mt_drop()"];
            "FSM" -> "ST_IDLE" [label="mt_send_data()"];
            "FSM" -> "ST_IDLE" [label="EV_TX_DATA"];

            subgraph cluster_c_sock {
                label="GSock";

                "ST_IDLE" [];
            }
            "ST_IDLE" -> "FSM" [label=EV_CONNECTED];
            "ST_IDLE" -> "FSM" [label=EV_DISCONNECTED];
            "ST_IDLE" -> "FSM" [label=EV_RX_DATA];
            "ST_IDLE" -> "FSM" [label=EV_TRANSMIT_READY];
        }
"""

import select
import socket
import errno
import sys
import warnings
from collections import deque
import os

from ginsfsm.gobj import GObj
from ginsfsm.compat import string_types
import logging
log = logging.getLogger(__name__)

from errno import (
    EALREADY,
    EINPROGRESS,
    EWOULDBLOCK,
    ECONNRESET,
    EINVAL,
    ENOTCONN,
    ESHUTDOWN,
    EINTR,
    EISCONN,
    EBADF,
    ECONNABORTED,
    EADDRNOTAVAIL,
    errorcode
    )

_DISCONNECTED = frozenset((
    ECONNRESET,
    ENOTCONN,
    ESHUTDOWN,
    ECONNABORTED,
    ))

class IOLoop(object):
    # Constants from the epoll module
    _EPOLLIN = 0x001
    _EPOLLPRI = 0x002
    _EPOLLOUT = 0x004
    _EPOLLERR = 0x008
    _EPOLLHUP = 0x010
    _EPOLLRDHUP = 0x2000
    _EPOLLONESHOT = (1 << 30)
    _EPOLLET = (1 << 31)

    # Our events map exactly to the epoll events
    NONE = 0
    READ = _EPOLLIN
    WRITE = _EPOLLOUT
    ERROR = _EPOLLERR | _EPOLLHUP | _EPOLLRDHUP

def _strerror(err):
    try:
        return os.strerror(err)
    except (ValueError, OverflowError, NameError):
        if err in errorcode:
            return errorcode[err]
        return "Unknown error %s" % err

_reraised_exceptions = (
    KeyboardInterrupt,
    SystemExit,
    )

HEX_FILTER = ''.join(
    [(len(repr(chr(x)))==3) and chr(x) or '.' for x in range(256)]
    )
def hexdump(prefix, src, length=16):
    N = 0
    result = ''
    src = bytes(src)
    while src:
        s,src = src[:length],src[length:]
        hexa = ' '.join(["%02X"%ord(x) for x in s])
        s = s.translate(HEX_FILTER)
        result += "%s %04X   %-*s   %s\n" % (prefix, N, length*3, hexa, s)
        N+=length
    return result

def xbuffer(obj, start=None, stop=None):
    # if memoryview objects gain slicing semantics,
    # this function will change for the better
    # memoryview used for the TypeError
    memoryview(obj)
    if start == None:
        start = 0
    if stop == None:
        stop = len(obj)
    x = obj[start:stop]
    ## print("xbuffer type is: %s"%(type(x),))
    return x

def readwrite(obj, flags):
    try:
        if flags & (IOLoop.ERROR):
            obj.handle_close()
            return
        if flags & (IOLoop.READ):
            obj.handle_read_event()
        if flags & (IOLoop.WRITE):
            obj.handle_write_event()
    except socket.error as e:
        if e.args[0] not in (
                EBADF,
                ECONNRESET,
                ENOTCONN,
                ESHUTDOWN,
                ECONNABORTED):
            obj.handle_error()
        else:
            obj.handle_close()
    except _reraised_exceptions:
        close_all_sockets(obj._socket_map)
        raise
    except:
        #obj.handle_error() #TODO
        raise

def poll_loop(socket_map, _impl, timeout):
    """ check poll, return True if some sock event, otherwise False.
    """
    ret = False
    try:
        event_pairs = _impl.poll(timeout)
    except Exception as e:
        # Depending on python version and IOLoop implementation,
        # different exception types may be thrown and there are
        # two ways EINTR might be signaled:
        # * e.errno == errno.EINTR
        # * e.args is like (errno.EINTR, 'Interrupted system call')
        if (getattr(e, 'errno', None) == errno.EINTR or
                (isinstance(getattr(e, 'args', None), tuple) and
                len(e.args) == 2 and e.args[0] == errno.EINTR)):
            return ret
        else:
            raise
    #print "events ------------->", event_pairs
    #print "sockmp ------------->", socket_map.keys()
    for fd, events in event_pairs:
        obj = socket_map.get(fd, None)
        if obj is None:
            continue
        ret = True
        readwrite(obj, events)
    return ret

#===========================================================
#       GSock gobj
#===========================================================
def ac_send_data(self, event):
    self.mt_send_data(event.data)

GSOCK_FSM = {
    'output_list': ('EV_CONNECTED', 'EV_DISCONNECTED',
                    'EV_RX_DATA', 'EV_TRANSMIT_READY'),
    'event_list': ('EV_TX_DATA',),
    'state_list': ('ST_IDLE',),
    'machine': {
        'ST_IDLE':
        (
            ('EV_TX_DATA',      ac_send_data,       'ST_IDLE'),
        ),
    }
}

class GSock(GObj):
    """  Client socket gobj.

    *Attributes:*
        * :attr:`subscriber`: subcriber of all output-events.
          **Writable attribute**. Default is ``None``, i.e., the parent:
          see :meth:`start_up`.
        * :attr:`host`: destine host. **Writable** attribute.
        * :attr:`port`: destine port. **Writable** attribute.
        * :attr:`connected`: it informs of state: ``True`` connected,
          ``False`` disconnected. **Readable attribute**.
        * :attr:`tx_buffer_size`: transmission buffer size.
          **Writable attribute**. Default is ``4096``.
        * :attr:`use_encoding`: transmission buffer size.
          **Writable attribute**. Default is ``0``.
        * :attr:`encoding`: transmission buffer size.
          **Writable attribute**. Default is ``'latin1'``.
        * :attr:`trace_dump`: trace input/output data dump.
          **Writable attribute**. Default is ``False``.
        * :attr:`connected_event_name`: name of connected event
          **Writable attribute**. Default: ``'EV_CONNECTED'``.
        * :attr:`disconnected_event_name`: name of disconnected event.
          **Writable attribute**. Default: ``'EV_DISCONNECTED'``.
        * :attr:`transmit_ready_event_name`: name of transmit_ready event.
          **Writable attribute**. Default: ``'EV_TRANSMIT_READY'``.
        * :attr:`rx_data_event_name`: name of data event.
          **Writable attribute**. Default: ``'EV_RX_DATA'``.

    *Input-Events:*
        * :attr:`'EV_TX_DATA'`: transmit ``event.data``.

          Mandatory attributes of the received :term:`event`:

          * ``data``: data to send.
             Internally the called action calls to :meth:`mt_send_data` method::

                self.mt_send_data(event.data)

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
        GObj.__init__(self, GSOCK_FSM)
        self.host = ''
        self.port = ''
        self.subscriber = None
        self.connected = False
        self.tx_buffer_size = 4096
        # we don't want to enable the use of encoding by default, because that
        # is a sign of an application bug that we don't want to pass silently
        self.use_encoding = 0
        self.encoding = 'latin1'
        self.txed_msgs = 0
        self.rxed_msgs = 0
        self.txed_bytes = 0
        self.rxed_bytes = 0
        self.trace_dump = False
        self.connected_event_name = 'EV_CONNECTED'
        self.disconnected_event_name = 'EV_DISCONNECTED'
        self.transmit_ready_event_name = 'EV_TRANSMIT_READY'
        self.rx_data_event_name = 'EV_RX_DATA'

        self.addr = None        # dont't private: waitress use it.
        self.socket = None      # dont't private: waitress use it.

        self._socket_map = {}   #socket_map set by gaplic. Dict {fd:Gobj}
        self._impl_poll = None  # _poll(),epoll() implementation
        self._tx_fifo_queue = deque()
        self._accepting = False
        self._transmit_ready_event_done = False
        self._clisrv = False
        self._fileno = None
        self.will_close = False              # set to True to close the socket.

    def start_up(self):
        """ Initialization zone.

        Subcribe all enabled :term:`output-event`'s to ``subscriber``
        with this sentence::

            self.subscribe_event(None, self.subscriber)
        """
        self.subscribe_event(None, self.subscriber)

    def set_clisrv_socket(self, sock):
        # Set to nonblocking just to make sure for cases where we
        # get a socket from a blocking source.
        sock.setblocking(0)
        self.add_socket(sock)
        self.connected = True
        self._clisrv = True
        # The constructor no longer requires that the socket
        # passed be connected.
        try:
            self.addr = sock.getpeername()
        except socket.error as err:
            if err.args[0] == ENOTCONN:
                # To handle the case where we got an unconnected
                # socket.
                self.connected = False
            else:
                # The socket is broken in some unknown way, alert
                # the user and remove it from the socket_map (to prevent
                # polling of broken sockets).
                self.remove_socket()
                raise

    def __repr__(self):
        status = [self.__class__.__module__+"."+self.__class__.__name__]
        if self._accepting and self.addr:
            status.append('listening')
        elif self.connected:
            status.append('connected')
        if self.addr is not None:
            try:
                status.append('%s:%d' % self.addr)
            except TypeError:
                status.append(repr(self.addr))
        return '<%s at %#x>' % (' '.join(status), id(self))

    __str__ = __repr__

    def create_socket(self, family, xtype):
        self.family_and_type = family, xtype
        sock = socket.socket(family, xtype)
        sock.setblocking(0)
        self.add_socket(sock)

    def set_reuse_addr(self):
        # try to re-use a server port if possible
        try:
            self.socket.setsockopt(
                socket.SOL_SOCKET, socket.SO_REUSEADDR,
                self.socket.getsockopt(socket.SOL_SOCKET,
                                       socket.SO_REUSEADDR) | 1
                )
        except socket.error:
            pass

    def add_socket(self, sock):
        self.socket = sock
        self._fileno = sock.fileno()
        self._socket_map[self._fileno] = self
        self._impl_poll.register(
            self._fileno, IOLoop.WRITE|IOLoop.READ|IOLoop.ERROR)

    def remove_socket(self):
        fd = self._fileno
        self._socket_map.pop(fd, None)
        self._fileno = None
        self.socket = None
        try:
            self._impl_poll.unregister(fd)
        except (OSError, IOError):
            logging.debug("Error deleting fd from IOLoop", exc_info=True)

    #==================================================
    #   socket object methods.
    #==================================================
    def listen(self, num):
        self._accepting = True
        if os.name == 'nt' and num > 5:
            num = 5
        return self.socket.listen(num)

    def bind(self, addr):
        self.addr = addr
        return self.socket.bind(addr)

    def connect(self, address):
        self.connected = False
        err = self.socket.connect_ex(address)
        if err in (EINPROGRESS, EALREADY, EWOULDBLOCK, ) \
        or err == EINVAL and os.name in ('nt', 'ce'):
            return
        if err in (0, EISCONN):
            self.addr = address
            self.handle_connect_event()
        else:
            raise socket.error(err, errorcode[err])

    def accept(self):
        # XXX can return either an address pair or None
        try:
            conn, addr = self.socket.accept()
        except TypeError:
            return None
        except socket.error as why:
            if why.args[0] in (EWOULDBLOCK, ECONNABORTED):
                return None
            else:
                raise
        else:
            return conn, addr

    def send(self, data):
        try:
            result = self.socket.send(data)
            return result
        except socket.error as why:
            if why.args[0] == EWOULDBLOCK:
                return 0
            elif why.args[0] in _DISCONNECTED:
                self.handle_close()
                return 0
            else:
                raise

    def recv(self):
        try:
            data = self.socket.recv(4096)
            if not data:
                # a closed connection is indicated by signaling
                # a read condition, and having recv() return 0.
                self.handle_close()
                return b''
            else:
                return data
        except socket.error as why:
            # winsock sometimes throws ENOTCONN
            if why.args[0] in _DISCONNECTED:
                self.handle_close()
                return b''
            else:
                raise

    def close(self):
        self.connected = False
        self._accepting = False
        if self.socket:
            try:
                self.socket.close()
            except socket.error as why:
                if why.args[0] not in (ENOTCONN, EBADF):
                    raise

    # cheap inheritance, used to pass all other attribute
    # references to the underlying socket object.
    def __getattr__(self, attr):
        try:
            retattr = getattr(self.socket, attr)
        except AttributeError:
            raise AttributeError("%s instance has no attribute '%s'"
                                 %(self.__class__.__name__, attr))
        else:
            msg = "%(me)s.%(attr)s is deprecated; use %(me)s.socket.%(attr)s "\
                "instead" % {'me' : self.__class__.__name__, 'attr' : attr}
            warnings.warn(msg, DeprecationWarning, stacklevel=2)
            return retattr

    def handle_read_event(self):
        #log.debug("handle_read_event    (%s %s)" % (self, self.name))
        if self._accepting:
            # _accepting sockets are never connected, they "spawn" new
            # sockets that are connected
            self.handle_accept()
        elif not self.connected:
            self.handle_connect_event()
            self.handle_read()
        else:
            self.handle_read()

    def handle_connect_event(self):
        #log.debug("handle_connect_event (%s %s)" % (self, self.name))
        err = self.socket.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
        if err != 0:
            raise socket.error(err, _strerror(err))
        self.connected = True
        self.handle_connect()

    def handle_write_event(self):
        #log.debug("handle_write_event   (%s %s)" % (self, self.name))
        if self._accepting:
            # Accepting sockets shouldn't get a write event.
            # We will pretend it didn't happen.
            return

        if not self.connected:
            #check for errors
            err = self.socket.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
            if err != 0:
                raise socket.error(err, _strerror(err))

            self.handle_connect_event()
        self.handle_write()

    def handle_error(self):
        nil, t, v, tbinfo = compact_traceback()

        # sometimes a user repr method will crash.
        try:
            self_repr = repr(self)
        except:
            self_repr = '<__repr__(self) failed for object at %0x>' % id(self)

        log.error(
            'uncaptured python exception, closing channel %s (%s:%s %s)' % (
                self_repr,
                t,
                v,
                tbinfo
                )
            )
        self.handle_close()

    #====================================================
    #   Mine's
    #====================================================
    def handle_accept(self):
        try:
            pair = self.accept()
            if pair is not None:
                self.handle_accepted(*pair)

        except socket.error:
            # Linux: On rare occasions we get a bogus socket back from
            # accept. socketmodule.c:makesockaddr complains that the
            # address family is unknown. We don't want the whole server
            # to shut down because of this.
            log.warning('server accept() threw an exception',
                                exc_info=True)

    def handle_accepted(self, sock, addr):
        sock.close()
        log.warn('unhandled accepted event')

    def mt_connect(self, **kw):
        """ Try to connect to (host, port).

        :param kw: valid keyword arguments are ``host`` and ``port``.

        This method calls to :meth:`get_next_dst` to get the destination tuple.

        Example::

            mt_connect(host='127.0.0.1', port=80) #override host,port attributes

        Or::

            mt_connect() # use current host,port attributes

        :class:`GSock` will broadcast some of ``'EV_CONNECTED'`` or
        ``'EV_DISCONNECTED'`` event as result of this action.
        """
        self.__dict__.update(**kw)

        if self.connected:
            log.error("ERROR connecting to host '%s', port %s. "
                      "ALREADY CONNECTED." % (self.host, self.port))
            return False
        if self.socket:
            log.error("ERROR connecting to host '%s', port %s. SOCKET EXISTS." %
                      (self.host, self.port))
            self.close() #??
            self.remove_socket() #??
            #TODO: si cumple el timeout de conexion viene por aqui
            #return False ???

        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host, self.port = self.get_next_dst()
        try:
            ip = socket.gethostbyname(self.host)
        except Exception as e:
            log.error('ERROR gethostbyname %s' % e)
            return False
        log.info("%s connecting to host '%s', ip '%s', port %s..." % (
            self.name, self.host, ip, self.port))
        try:
            self.connect((ip, self.port))
        except Exception as e:
            log.error("mt_connect() ERROR %s" % repr(e))
            return False
        return True

    def get_next_dst(self):
        """ Supply the destination ``(host,port)`` tuple to
        :meth:`mt_connect` method.
        By default this function returns the internal ``(host,port)``
        attributes.

        TO BE OVERRIDE if you need other policy.
        """
        return (self.host, self.port)

    def handle_connect(self):
        data = {}
        data['peername'] = self.socket.getpeername()
        data['sockname'] = self.socket.getsockname()
        log.info("%s connected %s host '%s'" % (
            self.name, "FROM" if self._clisrv else "TO", str(data['peername'])))
        # remove WRITE
        self._impl_poll.modify(self._fileno, IOLoop.READ|IOLoop.ERROR)
        self.broadcast_event(self.connected_event_name, **data)

    def mt_drop(self):
        """ Drop the connexion.
        """
        log.info("mt_drop(), disconnecting from '%s', host '%s', port %s..." %
                 (self.name, self.host, self.port))
        if self.socket:
            self.socket.shutdown(socket.SHUT_RDWR)
            self._impl_poll.modify(
                self._fileno, IOLoop.WRITE|IOLoop.READ|IOLoop.ERROR)
        else:
            self.close()
        return 0

    def handle_close(self):
        self.close()
        self.remove_socket()
        #TODO: pon la causa del disconnect
        self.broadcast_event(self.disconnected_event_name)

    def handle_read(self):
        try:
            data = self.recv()
        except socket.error as why:
            self.handle_error()
            return

        if isinstance(data, (string_types)) and self.use_encoding:
            data = bytes(str, self.encoding)

        ln = len(data)
        self.rxed_msgs += 1
        self.rxed_bytes += ln
        if self.trace_dump:
            log.debug("Recv data '%s' (%d bytes)\n%s" % (
                self.name, ln, hexdump('<=', data)))

        self.broadcast_event(self.rx_data_event_name, data=data)

    def readable(self):
        #"predicate for inclusion in the readable for select()"
        return True

    def write_soon(self, data):
        """ Same as mt_send_data. Need it for waitress use.
        """
        #TODO: study how integrate the Buffers from waitress
        """
        if data:
            # the async mainloop might be popping data off outbuf; we can
            # block here waiting for it because we're in a task thread
            with self.outbuf_lock:
                if data.__class__ is ReadOnlyFileBasedBuffer:
                    # they used wsgi.file_wrapper
                    self.outbufs.append(data)
                    nextbuf = OverflowableBuffer(self.adj.outbuf_overflow)
                    self.outbufs.append(nextbuf)
                else:
                    self.outbufs[-1].append(data)
            # XXX We might eventually need to pull the trigger here (to
            # instruct select to stop blocking), but it slows things down so
            # much that I'll hold off for now; "server push" on otherwise
            # unbusy systems may suffer.
            return len(data)
        return 0
        """
        self.mt_send_data(data)

    def mt_send_data(self, data):
        """ Send data.

        :param data: data to send.

        If ``data`` is instance of string type, and :attr:`use_encoding` is set,
        then ``data`` is encoding with::

            data = bytes(data, self.encoding)
        """
        if not self.connected:
            log.error('ERROR mt_send_data(): socket %s not connected' %
                      (self.name))
            return
        if self.trace_dump:
            log.debug("Send data '%s' (%d bytes)\n%s" %
                      (self.name, len(data), hexdump('=>', data)))

        sabs = self.tx_buffer_size
        ln = len(data)
        self.txed_msgs += 1
        if ln > sabs:
            for i in range(0, len(data), sabs):
                self._tx_fifo_queue.append(data[i:i+sabs])
        else:
            self._tx_fifo_queue.append(data)
        self._transmit_ready_event_done = False
        self.initiate_send()

    def handle_write(self):
        # Precondition: there's data in the out buffer to be sent, or
        # there's a pending will_close request
        if not self.connected:
            # we dont want to close the channel twice
            return

        self.initiate_send()
        if not self._transmit_ready_event_done:
            self._transmit_ready_event_done = True
            self.broadcast_event(self.transmit_ready_event_name)

    def writable(self):
        #"predicate for inclusion in the writable for select()"
        return self._tx_fifo_queue or (not self.connected) or self.will_close

    def initiate_send(self):
        # Return False if there is no more data to send.
        if not (self._tx_fifo_queue and self.connected):
            return

        first = self._tx_fifo_queue[0]
        if not first:
            del self._tx_fifo_queue[0]
            return

        # handle classic producer behavior
        obs = self.tx_buffer_size
        data = xbuffer(first, 0, obs)

        if isinstance(data, (string_types)) and self.use_encoding:
            data = bytes(data, self.encoding)

        # send the data
        num_send = 0
        try:
            num_sent = self.send(data)
        except socket.error:
            self.will_close = True

        if num_sent:
            self.txed_bytes += num_sent
            if num_sent < len(data) or obs < len(first):
                self._tx_fifo_queue[0] = first[num_sent:]
            else:
                del self._tx_fifo_queue[0]

        if self.will_close:
            self.handle_error()

    def discard_buffers (self):
        # Emergencies only!
        self._tx_fifo_queue.clear()

# ---------------------------------------------------------------------------
# used for debugging.
# ---------------------------------------------------------------------------
def compact_traceback():
    t, v, tb = sys.exc_info()
    tbinfo = []
    if not tb: # Must have a traceback
        raise AssertionError("traceback does not exist")
    while tb:
        tbinfo.append((
            tb.tb_frame.f_code.co_filename,
            tb.tb_frame.f_code.co_name,
            str(tb.tb_lineno)
            ))
        tb = tb.tb_next

    # just to be safe
    del tb

    file, function, line = tbinfo[-1]
    info = ' '.join(['[%s|%s|%s]' % x for x in tbinfo])
    return (file, function, line), t, v, info

def close_all_sockets(socket_map, ignore_all=False):
    for x in list(socket_map.values()):
        try:
            print('closinggggg' % x)
            x.close()
        except OSError as x:
            if x.args[0] == EBADF:
                pass
            elif not ignore_all:
                raise
        except _reraised_exceptions:
            raise
        except:
            if not ignore_all:
                raise
    socket_map.clear()

#================================================================
#   Poll implementations
#================================================================

class _EPoll(object):
    """An epoll-based event loop using our C module for Python 2.5 systems"""
    _EPOLL_CTL_ADD = 1
    _EPOLL_CTL_DEL = 2
    _EPOLL_CTL_MOD = 3

    def __init__(self):
        self._epoll_fd = epoll.epoll_create()

    def fileno(self):
        return self._epoll_fd

    def close(self):
        os.close(self._epoll_fd)

    def register(self, fd, events):
        epoll.epoll_ctl(self._epoll_fd, self._EPOLL_CTL_ADD, fd, events)

    def modify(self, fd, events):
        epoll.epoll_ctl(self._epoll_fd, self._EPOLL_CTL_MOD, fd, events)

    def unregister(self, fd):
        epoll.epoll_ctl(self._epoll_fd, self._EPOLL_CTL_DEL, fd, 0)

    def poll(self, timeout):
        return epoll.epoll_wait(self._epoll_fd, int(timeout * 1000))

class _KQueue(object):
    """A kqueue-based event loop for BSD/Mac systems."""
    def __init__(self):
        self._kqueue = select.kqueue()
        self._active = {}

    def fileno(self):
        return self._kqueue.fileno()

    def close(self):
        self._kqueue.close()

    def register(self, fd, events):
        self._control(fd, events, select.KQ_EV_ADD)
        self._active[fd] = events

    def modify(self, fd, events):
        self.unregister(fd)
        self.register(fd, events)

    def unregister(self, fd):
        events = self._active.pop(fd)
        self._control(fd, events, select.KQ_EV_DELETE)

    def _control(self, fd, events, flags):
        kevents = []
        if events & IOLoop.WRITE:
            kevents.append(select.kevent(
                    fd, filter=select.KQ_FILTER_WRITE, flags=flags))
        if events & IOLoop.READ or not kevents:
            # Always read when there is not a write
            kevents.append(select.kevent(
                    fd, filter=select.KQ_FILTER_READ, flags=flags))
        # Even though control() takes a list, it seems to return EINVAL
        # on Mac OS X (10.6) when there is more than one event in the list.
        for kevent in kevents:
            self._kqueue.control([kevent], 0)

    def poll(self, timeout):
        kevents = self._kqueue.control(None, 1000, timeout)
        events = {}
        for kevent in kevents:
            fd = kevent.ident
            if kevent.filter == select.KQ_FILTER_READ:
                events[fd] = events.get(fd, 0) | IOLoop.READ
            if kevent.filter == select.KQ_FILTER_WRITE:
                if kevent.flags & select.KQ_EV_EOF:
                    # If an asynchronous connection is refused, kqueue
                    # returns a write event with the EOF flag set.
                    # Turn this into an error for consistency with the
                    # other IOLoop implementations.
                    # Note that for read events, EOF may be returned before
                    # all data has been consumed from the socket xbuffer,
                    # so we only check for EOF on write events.
                    events[fd] = IOLoop.ERROR
                else:
                    events[fd] = events.get(fd, 0) | IOLoop.WRITE
            if kevent.flags & select.KQ_EV_ERROR:
                events[fd] = events.get(fd, 0) | IOLoop.ERROR
        return events.items()

class _Select(object):
    """A simple, select()-based IOLoop implementation for non-Linux systems"""
    def __init__(self):
        self.read_fds = set()
        self.write_fds = set()
        self.error_fds = set()
        self.fd_sets = (self.read_fds, self.write_fds, self.error_fds)

    def close(self):
        pass

    def register(self, fd, events):
        if events & IOLoop.READ: self.read_fds.add(fd)
        if events & IOLoop.WRITE: self.write_fds.add(fd)
        if events & IOLoop.ERROR:
            self.error_fds.add(fd)
            # Closed connections are reported as errors by epoll and kqueue,
            # but as zero-byte reads by select, so when errors are requested
            # we need to listen for both read and error.
            self.read_fds.add(fd)

    def modify(self, fd, events):
        self.unregister(fd)
        self.register(fd, events)

    def unregister(self, fd):
        self.read_fds.discard(fd)
        self.write_fds.discard(fd)
        self.error_fds.discard(fd)

    def poll(self, timeout):
        readable, writeable, errors = select.select(
            self.read_fds, self.write_fds, self.error_fds, timeout)
        events = {}
        for fd in readable:
            events[fd] = events.get(fd, 0) | IOLoop.READ
        for fd in writeable:
            events[fd] = events.get(fd, 0) | IOLoop.WRITE
        for fd in errors:
            events[fd] = events.get(fd, 0) | IOLoop.ERROR
        return events.items()

#================================================================
#   Choose a poll implementation. Use epoll if it is available,
#   fall back to select() for non-Linux platforms
#================================================================
if hasattr(select, "epoll"):
    # Python 2.6+ on Linux
    _poll = select.epoll
elif hasattr(select, "kqueue"):
    # Python 2.6+ on BSD or Mac
    _poll = _KQueue
else:
    try:
        # Linux systems with our C module installed
        import epoll
        _poll = _EPoll
    except Exception:
        # All other systems
        if "linux" in sys.platform:
            logging.warning("epoll module not found; using select()")
        _poll = _Select

#_poll = _Select
