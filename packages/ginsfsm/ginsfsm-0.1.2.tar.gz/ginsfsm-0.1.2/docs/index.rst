.. GinsFSM documentation master file, created by
   sphinx-quickstart on Sun Oct 23 20:50:35 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

============
Wellcome
============

GinsFSM is a python library to develop systems based in finite-state machines
(`FSM <http://en.wikipedia.org/wiki/Finite-state_machine>`_).
This model is really useful when writing networking and communication
applications. In fact, it has been my programming style over 20 years of C
language development (Yes!, I'm a grandfather developer), and now that I’m
moving to python, I want to continue with that approach. I’m from Madrid (Spain)
and my English is very bad, so I would appreciate you telling any mistake
you see.


The idea is very simple:

    * All objects, called :term:`gobj`, are instances of a derived
      :class:`ginsfsm.gobj.GObj` class, that we call :term:`gclass`.
    * The :term:`gclass` has an inner :term:`simple-machine`
      that defines its behavior.
    * The communication between :term:`gobj`'s happens via :term:`event`'s.

Thus, the nature of this system is fully asynchronous and event-driven.

The interface is simple and common to all objects; you just have to change the
name of the event and the data they carry.

============
Installation
============

You can install the library with ``easy_install``::

    easy_install ginsfsm

or with ``pip``::

    pip install ginsfsm

See the http://ginsfsm.org/ to view documentation.

Code available in https://bitbucket.org/artgins/ginsfsm

=============
Using GinsFSM
=============

----------------------------
Writing your simple machine
----------------------------

Let's imagine a FSM with the following graph:

.. graphviz::

        digraph simple_machine {
            graph [fontsize=30 labelloc="t" label="" splines=true overlap=true];
            size="7.0"
            node [penwidth=2 style=filled fillcolor="lightgray"];
            rankdir=LR;
            "start_up" -> "ST_STATE1" []
            "ST_STATE1" -> "ST_STATE2" [label="EV_TIMEOUT/ac_task1()"];
            "ST_STATE2" -> "ST_STATE1" [label="EV_TIMEOUT/ac_task2()"];
            }

We can define this FSM with the following structure in python:

::

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

This structure is what we called :term:`simple-machine`.

The behavior of the previous FSM is pretty straightforward:

#. The first or default `state` is the first state ``'ST_STATE1'`` defined
   in ``'event_list'`` tuple.

#. When the :term:`simple-machine` receives the ``'EV_TIMEOUT'`` :term:`event`,
   executes the ``ac_task1()`` :term:`action`,
   and change to ``'ST_STATE2'`` :term:`next-state`:

.. graphviz::

        digraph simple_machine {
            graph [fontsize=30 labelloc="t" label="" splines=true overlap=true];
            size="4.0"
            node [penwidth=2 style=filled fillcolor="lightgray"];
            rankdir=LR;
            "ST_STATE1" -> "ST_STATE2" [label="EV_TIMEOUT/ac_task1()"];
            }


#. When the :term:`simple-machine` receives the ``'EV_TIMEOUT'`` :term:`event`,
   being now in the ``'ST_STATE2'`` :term:`state`, executes the ``ac_task2()``
   :term:`action`, and change to '``ST_STATE1'`` :term:`next-state`:

.. graphviz::

        digraph simple_machine {
            graph [fontsize=30 labelloc="t" label="" splines=true overlap=true];
            size="4.0"
            node [penwidth=2 style=filled fillcolor="lightgray"];
            rankdir=LR;
            "ST_STATE2" -> "ST_STATE1" [label="EV_TIMEOUT/ac_task2()"];
            }


As you can see, the :term:`simple-machine` is a dictionary with three keys:
    * ``output_list``: tuple of :term:`output-event` names..
    * ``event_list``: tuple of :term:`input-event` names.
    * ``state_list``: tuple of state names.
    * ``machine``: dictionary defining the :term:`machine`.

output_list
-----------
All :term:`output-event` issued by the the machine::

    'output_list': ()

event_list
----------
All :term:`input-event` supported by the the machine::

    'event_list': ('EV_TIMEOUT',)

state_list
----------

List of states. The order doesn' matter, but the first state is very important
because it is the default state when the machine starts::

    'state_list': ('ST_STATE1', 'ST_STATE2')

machine
-------
Relationship of :term:`event-name`/:term:`action`/:term:`next-state` in each
state::

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

You define which :term:`event-name`'s are supported by each :term:`state`,
the :term:`action` to be executed for each event, and what is
the :term:`next-state`.

-----------------
Write the actions
-----------------
Next step is to write the :term:`action`'s::

    def ac_task1(self, event):
        print 'TASK1'
        # Program the timer gobj to send us the EV_TIMEOUT event within 2 seconds.
        self.timer.mt_set_timer(seconds=2)

    def ac_task2(self, event):
        print 'TASK2'
        # Program the timer gobj to send us the EV_TIMEOUT event within 4 seconds.
        self.send_event('EV_SET_TIMER', self.timer, seconds=4)

All the :term:`action`'s have the same prototype::

    def action(self, event):

Thanks to :term:`event` argument, the :term:`action` knows
the :term:`event-name` that caused the action, the source :term:`gobj`
and destination :term:`gobj` of the event, and more.

The sentences::

        self.timer.mt_set_timer(seconds=2)
        self.send_event('EV_SET_TIMER', self.timer, seconds=4)

do both the same: telling to the child ``timer`` :term:`gobj` that send us
an ``'EV_TIMEOUT'`` event after 2 and 4 seconds respectly.
``timer`` is an :term:`gobj` of :class:`ginsfsm.c_timer.GTimer` :term:`gclass`.

--------------------------
Subclassing the GObj class
--------------------------

Once you have your :term:`simple-machine` and :term:`action`'s,
you have to subclass the :class:`ginsfsm.gobj.GObj` class in order to
create your own :term:`gclass` type that wraps your :term:`simple-machine`::

    class GPrincipal(GObj):
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

You only need to call the ``__init__`` method of the base class with
your :term:`simple-machine` and override the ``start_up`` method, to create
your :term:`gobj` childs and do the initialization that you need.

In this ``start_up`` sample, we create the ``timer`` :term:`gobj`,
that provides us the ``'EV_TIMEOUT'`` :term:`event`::

        self.timer = self.create_gobj(
            None,       # unnamed gobj
            GTimer,     # gclass
            self        # parent
        )

we program the first ``'EV_TIMEOUT'`` :term:`event`::

            self.timer.mt_set_timer(seconds=2)

and set the machine trace on to see their activity ::

            self.set_trace_mach(True, pprint)

-------------
Run your GObj
-------------
The last step is running your :term:`gobj`::

    if __name__ == "__main__":
        ga = GAplic(name='Example1')
        ga.create_gobj('principal', GPrincipal, None)
        try:
            ga.mt_process()
        except KeyboardInterrupt:
            print('Program stopped')

In order to do so, you need a :term:`gaplic`::

        ga = GAplic(name='Example1')

:term:`gaplic` is the domain that contains your :term:`gobj`'s.

Next, you must create the :term:`principal` gobj::

        ga.create_gobj('test_aplic', GPrincipal, None)

and finally, call the infinite loop::

        ga.mt_process()

----------
The output
----------
this will be the output trace you will see::

    INFO:ginsfsm.gaplic:Init GAplic (Example1)
    ''
    '2012-03-06 13:39:02 * trace_mach: (GPrincipal-principal)'
    '2012-03-06 13:39:04  -> mach: (GPrincipal-principal), st: ST_STATE1, ev: (EV_TIMEOUT,{}), ac: ac_task1()'
    '2012-03-06 13:39:04   - mach: (GPrincipal-principal), new_st: ST_STATE2'
    TASK1
    '2012-03-06 13:39:04  <- mach: (GPrincipal-principal), st: ST_STATE2, ret: None'
    '2012-03-06 13:39:06  -> mach: (GPrincipal-principal), st: ST_STATE2, ev: (EV_TIMEOUT,{}), ac: ac_task2()'
    '2012-03-06 13:39:06   - mach: (GPrincipal-principal), new_st: ST_STATE1'
    TASK2
    '2012-03-06 13:39:06  <- mach: (GPrincipal-principal), st: ST_STATE1, ret: None'
    '2012-03-06 13:39:10  -> mach: (GPrincipal-principal), st: ST_STATE1, ev: (EV_TIMEOUT,{}), ac: ac_task1()'
    '2012-03-06 13:39:10   - mach: (GPrincipal-principal), new_st: ST_STATE2'
    TASK1
    '2012-03-06 13:39:10  <- mach: (GPrincipal-principal), st: ST_STATE2, ret: None'
    '2012-03-06 13:39:12  -> mach: (GPrincipal-principal), st: ST_STATE2, ev: (EV_TIMEOUT,{}), ac: ac_task2()'
    '2012-03-06 13:39:12   - mach: (GPrincipal-principal), new_st: ST_STATE1'
    TASK2
    '2012-03-06 13:39:12  <- mach: (GPrincipal-principal), st: ST_STATE1, ret: None'
    ^CProgram stopped


-----------------
The full program
-----------------

See the full program in :ref:`example1`.

========================
Narrative documentation
========================

.. toctree::

    src/core/core
    src/core/between

=================
Api documentation
=================

.. toctree::

    api

==============
Examples
==============

.. toctree::

    src/examples/examples

=======
License
=======

    GinsFSM is released under terms of The ISC
    License `ISC <http://www.opensource.org/licenses/isc-license>`_.

    Copyright (c) 2012, Ginés Martínez Sánchez, alias "ginsmar".

    Permission to use, copy, modify, and/or distribute this software
    for any purpose with or without fee is hereby granted, provided that
    the above copyright notice and this permission notice appear in all copies.

    THE SOFTWARE IS PROVIDED “AS IS” AND THE AUTHOR DISCLAIMS ALL WARRANTIES
    WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
    MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
    ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
    WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
    ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
    OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

==================
Index and Glossary
==================

* :ref:`glossary`
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. add glossary, foreword, and latexindex in a hidden toc to avoid warnings

.. toctree::
   :hidden:

   glossary
