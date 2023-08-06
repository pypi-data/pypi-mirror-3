.. _glossary:

Glossary
========

.. glossary::
    :sorted:

    gaplic
        An instance of :class:`ginsfsm.gaplic.GAplic` class or derived.

    gclass
        Derived class of :class:`ginsfsm.gobj.GObj`
        with a :term:`simple-machine` defining their behavior.

    create_gobj
        Factory function to create :term:`gobj`'s.
        See :meth:`ginsfsm.gaplic.GAplic.create_gobj`.

    gobj
        An instance of a :term:`gclass`.

    principal
        Any :term:`gobj` created without parent.

    unnamed-gobj
        Unnamed :term:`gobj`.

    named-gobj
        Named :term:`gobj`.

    start_up
        The pseudo **"__init__"** method of :term:`gclass`'s.
        Method of :class:`ginsfsm.gobj.GObj` class to be overried.

    simple-machine
        It's a simple implementation of an Finite State Machines
        (`FSM <http://en.wikipedia.org/wiki/Finite-state_machine>`_)
        using a python dictionary: :mod:`ginsfsm.smachine`.

    machine
        Value of ``machine`` key of :term:`simple-machine` that is another
        dictionary describing the machine :mod:`ginsfsm.smachine`.

    event-name
        Name of an event.

    input-event
        Events that a :term:`gobj` receive from other :term:`gobj`'s,
        or send to itself.

    output-event
        Events that only are sent to another :term:`gobj`'s.

    event-filter
        Function for filtering events being broadcasting.
        See :ref:`filtering-events`.

    event-list
        List or tuple of all :term:`input-event`'s event names used in
        the :term:`machine`.

    state-list
        List of state names of the :term:`machine`. No matter the order,
        but it is important the first state, because it is the default state
        when the machine starts.

    event
        A :term:`event-name` or any object with a ``event_name`` attribute that
        feeds a :term:`simple-machine`.

        The module :mod:`ginsfsm.gobj` has a :func:`ginsfsm.gobj.event_factory`
        factory function to create instance
        of :class:`ginsfsm.gobj.Event` class.

    action
        Function to be executed when a :term:`machine` receives an :term:`event`.

    next-state
        Name of next state to set in a :term:`machine` when it receives an event.

    state
        State name of a machine's state. We don't difference between `state`
        and `state-name`, as opposite as :term:`event`/:term:`event-name`,
        because there is no a visible `state instance`.
