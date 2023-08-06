""" Example1.
    Use :class:`ginsfsm.c_timer.GTimer` :term:`gclass` to do two tasks.
"""
import logging
from pprint import pprint

from ginsfsm.gobj import GObj
from ginsfsm.gaplic import GAplic
from ginsfsm.c_timer import GTimer

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

def ac_task1(self, event):
    print 'TASK1'
    # Program the timer gobj to send us the EV_TIMEOUT event within 2 seconds.
    self.timer.mt_set_timer(seconds=2)

def ac_task2(self, event):
    print 'TASK2'
    # Program the timer gobj to send us the EV_TIMEOUT event within 2 seconds.
    self.send_event(self.timer, 'EV_SET_TIMER', seconds=4)

SAMPLE_FSM = {
    'output_list': (),
    'event_list': ('EV_TIMEOUT',),
    'state_list': ('ST_STATE1', 'ST_STATE2'),
    'machine': {
        'ST_STATE1':
        (
            ('EV_TIMEOUT',      ac_task1,       'ST_STATE2'),
        ),
        'ST_STATE2':
        (
            ('EV_TIMEOUT',      ac_task2,       'ST_STATE1'),
        ),
    }
}

class GPrincipal(GObj):
    """  Principal gobj.
    """
    def __init__(self):
        GObj.__init__(self, SAMPLE_FSM)

    def start_up(self):
        """ Initialization zone."""
        self.timer = self.create_gobj(
            None,       # unnamed gobj
            GTimer,     # gclass
            self        # parent
        )
        self.timer.mt_set_timer(seconds=2)
        self.set_trace_mach(True, pprint)

if __name__ == "__main__":
    ga = GAplic(name='Example1')
    ga.create_gobj('principal', GPrincipal, None)
    try:
        ga.mt_process()
    except KeyboardInterrupt:
        print('Program stopped')
