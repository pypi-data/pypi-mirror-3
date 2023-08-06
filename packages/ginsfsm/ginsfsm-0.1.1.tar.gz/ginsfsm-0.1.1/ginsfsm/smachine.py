# -*- encoding: utf-8 -*-
"""
This module implements a simple Finite State Machine
(`FSM <http://en.wikipedia.org/wiki/Finite-state_machine>`_).

Simple Machine
--------------

We define the FSM by a :term:`simple-machine`, that it's running by
the :class:`SMachine` class.

A :term:`simple-machine` is a dictionary with three keys::

    FSM = {
        'output_list': (),
        'event_list': (),
        'state_list': (),
        'machine': {}
    }

where:

* ``output_list``:
    item value is a tuple with all :term:`output-event` :term:`event-name`'s
    issued by the machine.
* ``event_list``:
    item value is a tuple with all :term:`input-event` :term:`event-name`'s
    supported by the machine.
* ``state_list``:
    item value is a tuple with all :term:`state`'s of the machine.
* ``machine``:
    item value is another dictionary with the description of
    the :term:`machine`.

If something is wrong in the :term:`simple-machine` definition, a
:exc:`MachineError` exception it will be raised.

The ``machine`` item value is a another dictionary describing which
:term:`event-name`'s are supported by each :term:`state`,
the :term:`action` to be executed for each event, and what is
the :term:`next-state`.

The dictionary's keys are the state names.
The values are a tuple of tuples with three items:

    * :term:`event-name`.
    * :term:`action`.
    * :term:`next-state`.

where:
    **event-name**: event name, a name of the ``event_list`` tuple.

    **action**: function to be executed when the machine receives
    the :term:`event` through :meth:`SMachine.inject_event` method call.

        Their prototype is::

            def action(self, event):

        where ``event`` is the argument used in
        the :meth:`inject_event` method call.

    **next-state**: next state to set. Must be a name of ``state_list``
    or ``None``.

    .. note:: The next state is changed **before** executing
        the :term:`action` function.
        If you don't like this behavior, set to the `next-state`
        to ``None``. Then you can use the :meth:`SMachine.set_new_state`
        method to change the :term:`state` inside the :term:`action`
        function, otherwise, the machine will remain in the same
        state.

A :term:`simple-machine` example::

    def ac_task1(self, event):
        print 'TASK1'

    def ac_task2(self, event):
        print 'TASK2'

    def ac_task3(self, event):
        print 'TASK3'

    def ac_task4(self, event):
        print 'TASK4'

    SAMPLE_FSM = {
        'output_list': (,),
        'event_list': ('EV_EVENT1', 'EV_EVENT2'),
        'state_list': ('ST_STATE1', 'ST_STATE2'),
        'machine' = {
            'ST_STATE1':
            (
                ('EV_EVENT1',      ac_task1,       'ST_STATE2'),
                ('EV_EVENT2',      ac_task2,       'ST_STATE2'),
            ),
            'ST_STATE2':
            (
                ('EV_EVENT1',      ac_task3,       'ST_STATE1'),
                ('EV_EVENT2',      ac_task4,       'ST_STATE1'),
            ),
        }
    }

.. warning:: All event names and state names used in the :term:`machine`
    must be defined in :term:`event-list` and :term:`state-list`
    respectively, otherwise a :exc:`MachineError` will be raised.

.. note:: You can too have :term:`output-event` events.
   These events it's not necessary to be in :term:`event-list`.

.. note:: The list with :term:`output-event` events is not used
    by :class:`SMachine`. It is merely informative.

"""

import datetime
from ginsfsm.compat import (
    string_types,
    integer_types,
    iterkeys_,
    itervalues_,
    )

EMPTY_FSM = {
    'output_list': (),
    'event_list': (),
    'state_list': (),
    'machine': {}
}

class StateError(Exception):
    """ Raised when the state name doesn't match any name of
    the :term:`state-list` list."""

class EventError(Exception):
    """ Raised when the event name doesn't match any name of
    the :term:`event-list` list."""

class MachineError(Exception):
    """ Raised when something is wrong in the :term:`simple-machine`
    definition."""

class EventNotAcceptedError(Exception):
    """ Raised when the event name is good, but the event is not accepted
    in the current machine's state."""

class SMachine(object):
    """ A class to run a :term:`simple-machine`.

    :param fsm: a :term:`simple-machine`, the dictionary describing the fsm.

    If the :term:`simple-machine` has errors a :exc:`MachineError` exception
    will be raised.
    """
    _inside = [0]    # to tab machine trace.

    def __init__(self, fsm):
        self.name = None
        if not issubclass(fsm.__class__, dict):
            raise MachineError("set_new_state(\"%s\") invalid TYPE in (%s,%s)" %
                               (repr(fsm), self.__class__.__name__, self.name))
        self._output_list = fsm.get('output_list',())
        self._event_list = fsm.get('event_list',())
        self._state_list = fsm.get('state_list',())
        fsm = fsm.get('machine', {})
        self._states = []
        self._last_state = 0
        self._current_state = 0
        self._trace_mach = False
        self._log = None

        # check state names
        state_names = list(self._state_list)
        for st_name in iterkeys_(fsm):
            if st_name in state_names:
                state_names.remove(st_name)
            else:
                raise MachineError(
                    "machine state '%s' is NOT in state-list in (%s,%s)" %
                    (repr(st_name), self.__class__.__name__, self.name))
        if len(state_names):
            raise MachineError("state-list OVERFILLED: %s in (%s,%s)" %
                (repr(state_names), self.__class__.__name__, self.name))

        # check event names
        event_names = list(self._event_list)
        set_event_names = set()
        for ev_ac in itervalues_(fsm):
            for ev_name, ac, nt in ev_ac:
                if ev_name in event_names:
                    set_event_names.add(ev_name)
                else:
                    raise MachineError(
                        "event name '%s' is NOT in event-list in (%s,%s)" %
                        (repr(ev_name), self.__class__.__name__, self.name))
        if len(event_names) != len(set_event_names):
            over = [x for x in event_names if x not in set_event_names]
            if len(over) == 0:
                for ev_name in set_event_names:
                    event_names.remove(ev_name)
                over = event_names
            raise MachineError("event-list OVERFILLED: %s in (%s,%s)" %
                (repr(over), self.__class__.__name__, self.name))

        # check next state names and actions
        state_names = list(self._state_list)
        for ev_ac in itervalues_(fsm):
            for ev_name, ac, nt in ev_ac:
                if nt is not None and nt not in state_names:
                    raise MachineError("next statename '%s' is NOT in "
                        "state-list in (%s,%s)" %
                        (repr(nt), self.__class__.__name__, self.name))
                if ac is not None:
                    if not hasattr(ac, '__call__'):
                        raise MachineError(
                            "action '%s' is NOT callable in (%s,%s)" %
                            (repr(ac), self.__class__.__name__, self.name))


        # Build constant names (like C enum) for events: dict of name:id
        self._event_index = {}
        idx = 0
        for ev in self._event_list:
            self._event_index[ev] = idx
            idx = idx + 1

        # Build constant names (like C enum) for states: dict of name:id
        self._state_index = {}
        idx = 0
        for st in self._state_list:
            self._state_index[st] = idx
            idx = idx + 1

        # Build list of states
        self._states = list(range(len(self._state_list)))
        for st in self._state_list:
            st_idx = self._state_index[st]
            ev_action_list = fsm[st]
            self._states[st_idx] = list(range(len(self._event_list)))

            for ev_act in ev_action_list:
                iev = self._event_index[ev_act[0]]
                # Save the action
                ac = ev_act[1]
                #Save the next state
                if ev_act[2] is not None:
                    next_state_id = self._state_index[ev_act[2]]
                else:
                    next_state_id = None
                self._states[st_idx][iev] = [ac, next_state_id]

    def set_new_state(self, new_state):
        """  Set a new state.
        Method to used inside actions, to force the change of state.

        :param new_state: new state to set.

        ``new_state`` must match some of the state names of the
        machine's :term:`state-list` or a :exc:`StateError` exception
        will be raised.
        """
        if not issubclass(new_state.__class__, (string_types)):
            raise StateError("set_new_state(\"%s\") invalid TYPE in (%s,%s)" %
                (repr(new_state), self.__class__.__name__, self.name))

        state_id = self._state_index.get(new_state, -1)
        if state_id == -1:
            raise StateError("set_new_state(\"%s\") state UNKNOWN in (%s,%s)" %
                (repr(new_state), self.__class__.__name__, self.name))
        self._set_new_state(state_id)

    def _set_new_state(self, state_id):
        if state_id is None or \
                not issubclass(state_id.__class__, integer_types) or \
                state_id < 0 or state_id >= len(self._state_list):
            raise StateError(
                "_set_new_state(\"%s\") state_id INVALID in (%s,%s)" %
                (repr(state_id), self.__class__.__name__, self.name))

        self._last_state = self._current_state
        self._current_state = state_id
        if self._trace_mach:
            if self._last_state != state_id:
                hora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self._log("%s%s - mach: (%s-%s), new_st: %s" % (
                    hora,
                    self._tab(),
                    self.__class__.__name__, self.name,
                    self._state_list[self._current_state]))
        return True

    def get_current_state(self):
        """ Return the name of the current state.

        If there is no state it returns ``None``.
        """
        if self._current_state == -1 or len(self._state_list) == 0:
            return None
        return self._state_list[self._current_state]

    def inject_event(self, event):
        """  Inject an event into the FSM.

        :param event: a string event name or any object with an ``event_name``
                      attribute.

        .. warning:: use this method if you use the :class:`SMachine` class in
           isolation, otherwise use the methods to send events from
           the :class:`ginsfsm.gobj.GObj` class.

        Execute the associated :term:`action` to the ``event`` in the current
        state.

        The `event name` must match some of the :term:`event-name` of the
        machine's :term:`event-list` or a :exc:`EventError` exception
        will be raised.

        If the :term:`event-name` exists in the machine , but it's not accepted
        by the current state, then no exception is raised but the
        function **returns** :exc:`EventNotAcceptedError`.

            .. note:: The :meth:`inject_event` method doesn't
                **raise** :exc:`EventNotAcceptedError` because a :term:`machine`
                should run under any circumstances. In any way an action can
                raise exceptions.

        If the event is accepted by the machine, the returned value
        by :meth:`inject_event` method it will be the returned value by
        the executed :term:`action`.
        """
        result = None

        if issubclass(event.__class__, (string_types)):
            event_name = event
        else:
            if not hasattr(event, 'event_name'):
                raise EventError("inject_event(\"%s\") invalid TYPE in (%s,%s)"
                    % (self.__class__.__name__, self.name, repr(event)))
            event_name = event.event_name

        event_id = self._event_index.get(event_name, -1)
        if event_id < 0:
            raise EventError("inject_event(\"%s\") event UNKNOWN in (%s,%s)" % (
                self.__class__.__name__, self.name, repr(event_name)))

        self._increase_inside()

        action = None
        if self._states:
            action = self._states[self._current_state][event_id]

        if not action or issubclass(action.__class__, integer_types):
            # Can be an int if there is no action defined to this event.
            # because of the use of range().

            if self._log:
                hora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self._log("%s%s-> mach: (%s-%s), st: %s, ev: %s "
                                "(NOT ACCEPTED, no match action)" % (
                    hora,
                    self._tab(),
                    self.__class__.__name__, self.name,
                    self._state_list[self._current_state],
                    event.event_name))
            self._decrease_inside()
            return EventNotAcceptedError

        if self._trace_mach:
            action_name = ''
            if action[0]:
                action_name = action[0].__name__
            hora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self._log("%s%s-> mach: (%s-%s), st: %s, ev: (%s,%s), ac: %s()" %(
                hora,
                self._tab(),
                self.__class__.__name__, self.name,
                self._state_list[self._current_state],
                self._event_list[event_id],
                repr(event.kw),
                action_name))

        if action[1] is not None:
            self._set_new_state(action[1])

        if action[0]:
            # Action found, execute
            result = action[0](self, event)

        if self._trace_mach:
            hora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self._log("%s%s<- mach: (%s-%s), st: %s, ret: %s" %(
                hora,
                self._tab(),
                self.__class__.__name__, self.name,
                self._state_list[self._current_state],
                repr(result)))

        self._decrease_inside()
        return result

    def get_input_event_list(self):
        """ Return the list with the :term:`input-event`'s names.
        """
        return list(self._event_list)

    def get_output_event_list(self):
        """ Return the list with the :term:`output-event`'s names.
        """
        return list(self._output_list)

    def set_trace_mach(self, enable, log=None):
        """  Enable/Disable machine trace.

        :param enable: Set or reset the trace of fsm.
        :param log: Function to print the trace messages.
        :type enable: bool
        :rtype: Return the previous value.
        """
        #TODO: doc
        prev = self._trace_mach
        new_val  = bool(enable)
        if log:
            self._log = log
        if new_val and self._log:
            self._trace_mach = new_val
            hora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self._log("")
            self._log("%s%s* trace_mach: (%s-%s)" % (
                hora,
                self._tab(),
                self.__class__.__name__, self.name))
        return prev

    def _increase_inside(self):
        """ TO BE OVERRIDEN by gaplic
        """
        self._inside[0] += 1

    def _decrease_inside(self):
        """ TO BE OVERRIDEN by gaplic
        """
        self._inside[0] -= 1

    def _tab(self):
        """ Indent, return spaces multiple of depth level gobj.
        With this, we can see the trace messages indenting according
        to depth level.
        TO BE OVERRIDEN by gaplic.
        """
        if self._inside[0] <= 0:
            spaces = 1
        else:
            spaces = self._inside[0]*2
        pad = ' ' * spaces
        return pad;
