.. _gobj_module:

-----------------------
:mod:`ginsfsm.gobj`
-----------------------

.. automodule:: ginsfsm.gobj

.. autoclass:: Event
    :members:

.. autoclass:: GObj
    :members: start_up, create_gobj, destroy_gobj,
        send_event, post_event, broadcast_event,
        subscribe_event, delete_subscription, set_owned_event_filter,
        search_gobj,
        set_trace_mach

    .. attribute:: name

        My name.

        Set by :meth:`create_gobj`.

    .. attribute:: parent

        My parent, destination of my events... or not.

        Set by :meth:`create_gobj`.

    .. attribute:: dl_childs

        Set of my gobj childs. Me too like be parent!.


    .. method:: set_new_state

        Set a new state.
        Method to used inside actions, to force the change of state.

        :param new_state: new state to set.

        ``new_state`` must match some of the state names of the
        machine's :term:`state-list` or a :exc:`StateError` exception
        will be raised.

    .. method:: get_current_state

        Return the name of the current state.

        If there is no state it returns ``None``.

    .. method:: get_input_event_list

       Return the list with the :term:`input-event`'s names.

    .. method:: get_output_event_list

       Return the list with the :term:`output-event`'s names.


.. autoexception:: ParentError

.. autoexception:: DestinationError

.. autoexception:: GObjError

.. autoexception:: EventError

.. autoexception:: StateError

.. autoexception:: MachineError

.. autoexception:: EventNotAcceptedError

.. autoexception:: QueueError
