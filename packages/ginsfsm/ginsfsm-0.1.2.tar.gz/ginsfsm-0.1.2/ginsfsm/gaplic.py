# -*- encoding: utf-8 -*-
""" Container of gobjs.
"""
import time
from collections import deque

from ginsfsm.compat import (
    iterkeys_,
    )

from ginsfsm.c_sock import (
    poll_loop,
    close_all_sockets,
    _poll,
    GSock,
    )
from ginsfsm.gobj import (
    GObj,
    )

import logging
log = logging.getLogger(__name__)

def _start_timer(seconds):
    """ Start a timer of :param:`seconds` seconds.
    The returned value must be used to check the end of the timer
    with _test_timer() function.
    """
    timer = time.time()
    timer = timer + seconds
    return timer

def _test_timer(value):
    """ Check if timer :param:`value` has ended.
    Return True if the timer has elapsed, False otherwise.
    WARNING: it will fail when system clock has been changed.
    TODO: check if system clock has been changed.
    """
    timer_actual = time.time()
    if timer_actual >= value:
        return True
    else:
        return False

class _XTimer(object):
    """  Group attributes for timing.
    :param:`got_timer` callback will be executed :param:`sec` seconds.
    The callback will be called with :param:`param1` parameter.
    If :param:`autostart` is True, the timer will be cyclic.
    """
    def __init__(self, sec, got_timer_func, param1, autostart):
        self.sec = sec
        self.got_timer_func = got_timer_func
        self.param1 = param1
        self.autostart = autostart

class GAplic(GObj):
    """ Container of gobj's running under the same process or thread.

    :param name: name of the gaplic, default is ``None``.

    Manage the timer's, event queues, etc.
    Supplies register, deregister and search or named-events.

    Example::

        if __name__ == "__main__":
            ga = GAplic(name='Example1')
            ga.create_gobj('test_aplic', GPrincipal, None)
            try:
                ga.mt_process()
            except KeyboardInterrupt:
                print('Program stopped')

    """
    def __init__(self, name=None):
        GObj.__init__(self, {})
        self.name = name
        self.do_exit = None # Event() to signal for shutdown the thread/process.
        """threading.Event() or multiprocessing.Event() object
        to signal the shutdown of gaplic."""
        self.loop_timeout = 0.5     # timeout to select(),poll() function.
        """Loop timeout. Default 0.5 seconds."""
        self._impl_poll = _poll()   # Used by gsock. epoll() implementation.
        self._socket_map = {}       # Used by gsock. Dict {fd:Gobj}
        self._gotter_timers = {}    # Dict with timers  {_XTimer:timer value}
        self._qevent = deque()      # queue for post events.
        self._inside = 0            # to tab machine trace.
        log.info('Init GAplic (%s)' % self.name)

    def _increase_inside(self):
        self._inside += 1

    def _decrease_inside(self):
        self._inside -= 1

    def _tab(self):
        if self._inside <= 0:
            spaces = 1
        else:
            spaces = self._inside*2
        pad = ' ' * spaces
        return pad

    def create_gobj(self, name, gclass, parent, **kw):
        """ Factory function to create gobj's instances.

        :param name: Name of gobj.
            You can create :term:`named-gobj` or :term:`unnamed-gobj` gobjs.
            :term:`named-gobj` gobjs can be reached by his name,
            but the :term:`unnamed-gobj` gobjs
            are only knowing by their `pointer`.

        :param gclass: :term:`gclass` is the GObj type used to create the
            new gobj.It's must be a derived class of :class:`ginsfsm.gobj.GObj`.
        :param parent: parent of the new :term:`gobj`.
            If `None`, the gobj will be a :term:`principal` gobj and
            their parent will be :term:`gaplic`.
        :param kw: Attributes that are added to the new :term:`gobj`.
            All the keyword arguments used in the function
            **are added as attributes** to the created :term:`gobj`.
            You must consult the attributes supported
            by each :term:`gclass` type.
        :rtype: new gobj instance.

        When a :term:`gobj` is created by the factory function, it's added to
        their parent child list :attr:`ginsfsm.gobj.GObj.dl_childs`,
        and several attributes are created:

        * **parent**: the parent :term:`gobj` of the created :term:`gobj`.
        * **gaplic**: the :term:`gaplic` of the created :term:`gobj`.

        If the :term:`gclass` is subclass of :class:`ginsfsm.c_sock.GSock`
        two private attributes are added to the created  :term:`gobj`:

        * **_socket_map**: dictionary of open sockets.
        * **_impl_poll**: poll implementation: can be epoll, select, KQueue..
          the best found option.

        It's the base of the asynchronous behavior.
        """
        if parent is None:
            parent = self

        kw.update({
            '_gaplic' : self,
            'create_gobj' : self.create_gobj,
            'enqueue_event' : self._enqueue_event,
            'register_gobj' : self.register_gobj,
            'deregister_gobj' : self.deregister_gobj,
            'search_gobj' : self.search_gobj,
            '_increase_inside' : self._increase_inside,
            '_decrease_inside' : self._decrease_inside,
            '_tab' : self._tab,
        })

        if issubclass(gclass, GSock):
            kw.update({
                '_socket_map':self._socket_map,
                '_impl_poll':self._impl_poll
            })

        gobj = GObj.create_gobj(self, name, gclass, parent, **kw)
        return gobj

    def register_gobj(self, gobj):
        """ Register a :term:`named-gobj`.
        TODO: It must be optional a 'unique' named-gobj.
        """
        pass #TODO

    def deregister_gobj(self, gobj):
        """ Deregister a :term:`named-gobj`.
        """
        pass #TODO

    def search_gobj(self, gobj_name):
        """ Search a :term:`named-gobj`.
        """
        pass #TODO

    def _loop(self):
        """ process event queue, timer queue, and epoll.
        Return True if there is some remain event for be proccessed.
        Useful for testing purposes.
        """
        remain = self._process_qevent()
        if remain:
            timeout = 0.01
        else:
            timeout = self.loop_timeout
        some_event = poll_loop(self._socket_map, self._impl_poll, timeout)
        if some_event:
            remain = True
        remain |= self._process_timer()

        self.mt_subprocess()
        return remain

    def mt_process(self):
        """ Infinite loop function to be called by thread or process.
        """
        if self.do_exit is None:
            while True:
                self._loop()
        else:
            while True:
                # with do_exit Event set (being thread or process),
                # wait to event set to exit, ignoring KeyboardInterrupt.
                try:
                    if self.do_exit.is_set():
                        close_all_sockets(self._socket_map)
                        break
                    self._loop()
                except (KeyboardInterrupt, SystemExit):
                    close_all_sockets(self._socket_map)
                    raise
        log.info("GAplic '%s' loop stopped" % self.name)

    def mt_subprocess(self):
        """ Subclass :class:`GAplic` class and override this function
        to do extra work in the infinite loop.
        """

    def _enqueue_event(self, event):
        """ Post the event in the next :term:`gaplic` loop cycle,
        not right now.

        :param event: :term:`event` to send.
        :param destination: destination :term:`gobj` of the event.
        :param kw: keyword argument with data associated to event.

            .. note::
                All the keyword arguments **are added as attributes** to
                the sent :term:`event`.

        Same as :meth:`send_event` function but the event is sent in the
        next :term:`gaplic` loop cycle, not right now.

        It **does not return** the return of the executed action because the
        action it's executed later, in the next loop cycle.

        It's mandatory use this function, if the `destination`
        :term:`gobj` is not local.

        .. note:: It **DOES NOT** return the return of the executed action
            because the action it's executed later, in the next loop cycle,
            so you **CANNOT** receive valid direct data from the action.

        .. warning:: If you use :meth:`post_event` without a :term:`gaplic`
            then a :exc:`GAplicError` exception will be raised.

        ``destination`` must be a `string` or :class:`GObj` types, otherwise a
        :exc:`GObjError` will be raised.

        ``event`` must be a `string` or :class:`Event` types, otherwise a
        :exc:`EventError` will be raised.

        If ``event`` is an :class:`Event` instance, a new :class:`Event`
        duplicated instance is returned, but it will be updated with
        the new ``destination`` and ``kw`` keyword arguments.

        .. note::
            All the keyword arguments used in the factory function
            **are added as attributes** to the created :term:`event` instance.
            You must consult the attributes supported by each machine's event.
        """
        self._qevent.append(event)

    def _process_qevent(self):
        """ Return True if remains events.
        """
        ln = len(self._qevent)
        #print "qevent...........%d" % (ln)
        it = 0
        maximum = 10
        while True:
            if it > maximum:
                return True
            try:
                event = self._qevent.popleft()
            except IndexError:
                break
            else:
                it += 1
                source = event.source[-1]
                source.send_event(event.destination,
                    event.event_name, **event.kw)
        return False

    def _process_timer(self):
        # dont use iteritems() items(),
        # some xtimer can remove during processing timers
        some_event = False
        try:
            for xtimer in iterkeys_(self._gotter_timers):
                try:
                    value = self._gotter_timers[xtimer]
                except KeyError:
                    # timer deleted while loop.
                    continue
                some_event = True
                if value and _test_timer(value):
                    if xtimer.autostart:
                        self._gotter_timers[xtimer] = _start_timer(xtimer.sec)
                    else:
                        self._gotter_timers[xtimer] = 0
                    if xtimer.param1 is None:
                        xtimer.got_timer_func()
                    else:
                        xtimer.got_timer_func(xtimer.param1)
                    if not xtimer.autostart:
                        self._gotter_timers.pop(xtimer)
        except RuntimeError:
            # timer deleted while loop.
            some_event = True
        return some_event

    def _setTimeout(self, sec, got_timer_func, param1=None, autostart=False):
        """ Set a callback to be executed in ``sec`` seconds.
        Function used by :class:`GTimer` gobj. Not for general use.
        Return an object to be used in :func:`clearTimeout`.
        """
        xtimer = _XTimer(sec, got_timer_func, param1, autostart)
        self._gotter_timers[xtimer] = _start_timer(sec)
        return xtimer

    def _clearTimeout(self, xtimer):
        """ Clear callback timeout.
        Function used by :class:`GTimer` gobj. Not for general use.
        """
        t = self._gotter_timers.get(xtimer, None)
        if t:
            # prevent timer cleared in proces_timer loop
            self._gotter_timers[xtimer] = 0
            self._gotter_timers.pop(xtimer)

#===============================================================
#                   Thread wrapper for gaplic
#===============================================================
import threading

class GAplicThreadWorker(threading.Thread):
    """ Class derived from :class:`threading.Thread` to run gaplic."""
    def __init__(self, gaplic):
        threading.Thread.__init__(self)
        self.daemon = True
        self.gaplic = gaplic
        gaplic.do_exit = threading.Event()

    def run(self):
        log.info("Running GAplic THREAD: %s" % self.name)
        self.gaplic.mt_process()

    def shutdown(self):
        """ Signalize the worker to shutdown """
        log.info("Shutdown GAplic THREAD initiated: %s" % self.name)
        self.gaplic.do_exit.set()

    def join(self, timeout=10.0):   # wait until 10 seconds for thread killed.
        """ Wait for worker to shutdown, until ``timeout`` seconds."""
        super(GAplicThreadWorker, self).join(timeout)
        log.info("GAplic THREAD terminated: %s" % self.name)

def start_gaplic_thread(gaplic):
    """ Run gaplic as thread.
    Return the worker.
    """
    worker = GAplicThreadWorker(gaplic)
    worker.start()
    return worker

#===============================================================
#                   Process wrapper for gaplic
#===============================================================
import multiprocessing

class GAplicProcessWorker(multiprocessing.Process):
    """ Class derived from :class:`multiprocessing.Process` to run gaplic."""
    def __init__(self, gaplic):
        multiprocessing.Process.__init__(self)
        self.daemon = True
        self.gaplic = gaplic
        gaplic.do_exit = multiprocessing.Event()

    def run(self):
        log.info("Running GAplic PROCESS: %s" % self.name)
        self.gaplic.mt_process()

    def shutdown(self):
        """ Signalize the worker to shutdown """
        log.info("Shutdown GAplic PROCESS initiated: %s" % self.name)
        self.gaplic.do_exit.set()

    def join(self, timeout=10.0):   # wait until 10 seconds for process killed.
        """ Wait for worker to shutdown, until ``timeout`` seconds."""
        super(GAplicProcessWorker, self).join(timeout)
        log.info("GAplic PROCESS terminated: %s" % self.name)

def start_gaplic_process(gaplic):
    """ Run gaplic as process.
    Return the worker.
    """
    worker = GAplicProcessWorker(gaplic)
    worker.start()
    return worker
