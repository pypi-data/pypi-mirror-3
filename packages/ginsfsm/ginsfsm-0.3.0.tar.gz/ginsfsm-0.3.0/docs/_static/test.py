#! /home/gines/env_ginsfsm/bin/python

from ginsfsm.fsmdraw.fsm2image import fsm2image
#from ginsfsm.c_timer import TIMER_FSM  # , TIMER_GCONFIG
from ginsfsm.c_connex import CONNEX_FSM  # , TIMER_GCONFIG


if __name__ == '__main__':
    svgfile = 'xxx'
    fsm2image('./', svgfile, CONNEX_FSM, 'svg',
              font_name='./DejaVuSans.ttf', font_size=14)
