# -*- encoding: utf-8 -*-

""" Timer GObj. Generate timeout events.

    .. graphviz::

        digraph GTimer {
            size="4.0"
            graph [splines=true overlap=false rankdir="LR"];
            node [penwidth=2 style=filled fillcolor="lightgray"];

            subgraph cluster_parent {
                label="Parent GObj";
                "FSM" [shape=box];
            }
            "FSM" -> "ST_IDLE" [label="EV_SET_TIMER"];
            "FSM" -> "ST_IDLE" [label="mt_set_timer()"];

            subgraph cluster_c_timer {
                label="GTimer";

                "ST_IDLE" [];
            }
            "ST_IDLE" -> "FSM" [label=EV_TIMEOUT];
        }
"""
import logging
log = logging.getLogger(__name__)

from ginsfsm.gobj import (
    GObj,
    )

def ac_set_timer(self, event):
    self.__dict__.update(**event.kw)
    self.mt_set_timer()

TIMER_FSM = {
    'output_list': ('EV_TIMEOUT',),
    'event_list': ('EV_SET_TIMER',),
    'state_list': ('ST_IDLE',),
    'machine': {
        'ST_IDLE':
        (
            ('EV_SET_TIMER',    ac_set_timer,   'ST_IDLE'),
        ),
    }
}

class GTimer(GObj):
    """  Supply timer events.

    *Attributes:*
        * :attr:`subscriber`: subcriber of all output-events.
          **Writable** attribute.
          Default is ``None``, i.e., the parent:
          see :meth:`start_up`.
        * :attr:`timeout_event_name`: timeout event name.
          **Writable** attribute. Default value: ``'EV_TIMEOUT'``.
        * :attr:`seconds`: timeout in seconds. With ``seconds=-1``
          the timer is cancelled. **Writable** attribute.
        * :attr:`autostart`: If `True` then timeout event is repeated
          every ``seconds``. **Writable** attribute

    *Input-Events:*
        * :attr:`'EV_TX_DATA'`: transmit ``event.data``.

          Mandatory attributes of the received :term:`event`:

          * ``data``: data to send.
             Internally the called action calls to :meth:`mt_send_data` method::

                self.mt_send_data(event.data)

        * :attr:`'EV_SET_TIMER'`: Set timer.
            Emit `'EV_TIMEOUT'` event when the ``seconds`` time has elapsed.
            If ``autostart`` is true, the timer is cyclic.

          Possible attributes of the received :term:`event`:

          * ``timeout_event_name``: change the output timeout event name.
          * ``seconds``: seconds of timer.
          * ``autostart``: cyclic timer.

    *Output-Events:*
        * :attr:`EV_TIMEOUT`: timer over. Send the ``'EV_TIMEOUT'``
          event to subscriber.
    """

    def __init__(self):
        GObj.__init__(self, TIMER_FSM)
        self.timeout_event_name = 'EV_TIMEOUT'
        self.seconds = -1
        self.autostart = False
        self.subscriber = None
        """ Subcriber of :term:`output-event` events.
        By default ``None``, i.e., the parent gobj.
        """
        self._timer_id = None

    def start_up(self):
        """ Initialization zone.

        Subcribe the :term:`output-event` to ``subscriber``
        with this sentence::

            self.subscribe_event('EV_TIMEOUT', self.subscriber,\
use_post_event=True)
        """
        # force use post_event(), to get timeout events by queue, not directly
        self.subscribe_event('EV_TIMEOUT', self.subscriber, use_post_event=True)

    def mt_set_timer(self, **kw):
        """ Set timer.

        Emit ``timeout_event_name`` event when the ``seconds`` time has elapsed.
        If ``autostart`` is true, the timer is cyclic.

            *Parameters:* {`timeout_event_name`, `seconds`, `autostart`}.

            .. note::
                We can see in this gobj, two equivalent methods to interact
                with the gobj:

                * send the `'EV_SET_TIMER'` event, or
                * call the `set_timer` method.
        """
        self.__dict__.update(**kw)

        if self._timer_id:
            # Clear the current timer
            self._gaplic._clearTimeout(self._timer_id)
            self._timer_id = None

        if self.seconds != -1:
            self._timer_id = self._gaplic._setTimeout(
                self.seconds,
                self._got_timer,
                autostart=self.autostart)
        return True

    def _got_timer(self):
        """ Callback timer
        """
        self.broadcast_event(self.timeout_event_name)
