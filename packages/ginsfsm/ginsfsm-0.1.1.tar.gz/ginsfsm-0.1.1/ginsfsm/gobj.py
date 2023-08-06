# -*- encoding: utf-8 -*-
"""
These module provides support for:

* creating :term:`gclass`: derive the :class:`GObj` class with your
  :term:`simple-machine`.
* creating :term:`gobj`'s with :func:`create_gobj` factory function.

The :class:`GObj` class provides support for:

* sending events:

    * sending events by direct delivery: :meth:`GObj.send_event`.
    * sending events by queues: :meth:`GObj.post_event`.
    * sending events to subscribers: :meth:`GObj.broadcast_event`.

* receiving events:

    * directly from another :term:`gobj`'s who knows you.
    * subscribing to events by the :meth:`GObj.subscribe_event` method.
    * you can filtering events being broadcasting with
      :meth:`GObj.set_owned_event_filter` method.

"""

from ginsfsm.compat import (
    string_types,
    is_nonstr_iter,
    )

from ginsfsm.smachine import (
    SMachine,
    StateError,
    EventError,
    MachineError,
    EventNotAcceptedError,
    )

class ParentError(Exception):
    """ Raised when parent is already defined."""

class DestinationError(Exception):
    """ Raised when destination is not know."""

class GObjError(Exception):
    """ Raised when an object is not a GObj type, and must be!."""

class QueueError(Exception):
    """ Raised when there is no support for enqueue objs, i.e., use of
        GObj.post_event() method.
    """

class Event(object):
    """ Collect event properties. This is the argument received by actions.

    :param destination: destination gobj whom to send the event.
    :param event_name: event name.
    :param source: list with path of gobj sources. Firt item ``source[0]``
        is the original sender gobj. Last item ``source[-1]`` is the
        nearest sender gobj.
    :param kw: keyword arguments with associated data to event.
    """
    # For now, event_factory is private. Automatically using by send_event...
    #Use the :meth:`GObj.event_factory` factory function to create Event
    #instances.
    def __init__(self, destination, event_name, source, **kw):
        self.destination = destination
        self.event_name = event_name
        if not issubclass(source.__class__, list):
            source = [source]
        self.source = source
        self.kw = kw
        self.__dict__.update(**kw)

class _Subscription(object):
    """ Collect subscriber properties
    `event_name`: event name.
    `subscriber_gobj`: subcriber gobj to sending event.
    `kw`: event parameters
    """
    def __init__(self, event_name, subscriber_gobj, **kw):
        self.event_name = event_name
        self.subscriber_gobj = subscriber_gobj
        self.kw = kw
        self.__dict__.update(**kw)


class GObj(SMachine):
    """ Well, yes, I'm a very simple brain. Only a machine.
    But write a good FSM, and I never fail you. Derive me, and write my FSM.

    Sample :term:`gclass`::

        class MyGClass(GObj):
            def __init__(self):
                GObj.__init__(self, FSM)

            def start_up(self):
                ''' Initialization zone.'''

    :param fsm: FSM :term:`simple-machine`.

    """
    def __init__(self, fsm):
        SMachine.__init__(self, fsm)
        self.name = None
        """ My name.
        Set by :meth:`create_gobj`
        """
        self.parent = None
        """My parent, destination of my events... or not.
        Set by :meth:`create_gobj`
        """
        self.dl_childs = set()        # my childs... me too like be parent.
        """List of gobj childs.
        """
        self.owned_event_filter = None #TODO debe ser una lista de filtros
        """Filter to broadcast_event function to check the owner of events.
        """

        self._dl_subscriptions = set()      # uauuu, how many fans!!
        self._some_subscriptions = False

    def create_gobj(self, name, gclass, parent, **kw):
        """ Factory function to create gobj's instances.

        :param name: Name of gobj. If it's a :term:`named-gobj` then the
            :meth:`GObj.register_gobj` will be called.
            :meth:`GObj.register_gobj` is a empty method that
            must be override by a superior domain like :term:`gaplic`.
        :param gclass: :term:`gclass` is the :class:`GObj` type used to create the
            new gobj.It's must be a derived class of :class:`GObj`
            otherwise a :exc:`GObjError` exception will be raised.
        :param parent: parent of the new :term:`gobj`. ``None`` if it has no parent.
            It it's not ``None``, then must be a derived class
            of :class:`GObj` otherwise a :exc:`GObjError`
            exception will be raised.
        :param kw: Attributes that are added to the new :term:`gobj`.
            All the keyword arguments used in the function
            **are added as attributes** to the created :term:`gobj`.
            You must consult the attributes supported
            by each :term:`gclass` type.
        :rtype: new gobj instance.

        The factory funcion does:

        * Add the :term:`gobj` to their parent child list :attr:`GObj.dl_childs`,
        * If it's a :term:`named-gobj` call the :meth:`GObj.register_gobj`.
        * Call :meth:`GObj.start_up`.
        * Add to the :term:`gobj` several attributes:

            * **name**: name of the created :term:`gobj`.
            * **parent**: the parent :term:`gobj` of the created :term:`gobj`.

        .. warning:: the :meth:`GObj.register`, :meth:`GObj.deregister`
            and :meth:`GObj.search` methods must be override and supplied by a
            superior instance, like :term:`gaplic`,
            otherwise :term:`named-gobj` objects cannot be used.
        """

        if gclass is None:
            raise GObjError(
                '''ERROR create_gobj(): No GObj class supplied.''')
        if not issubclass(gclass, GObj):
            raise GObjError(
                '''ERROR create_gobj(): class '%s' is NOT a GObj subclass''' % (
                    repr(gclass)))

        if parent is not None:
            if not issubclass(parent.__class__, GObj):
                raise GObjError(
                    '''ERROR create_gobj(): parent '%s' is NOT a GObj subclass''' % (
                        repr(gclass)))

        gobj = gclass()
        if parent is not None:
            parent.add_child(gobj)

        #TODO: must would be .update(**kw) be in start_up
        # (explicit instead of implicit?)
        gobj.__dict__.update({'name': name})
        gobj.__dict__.update(**kw)
        if name:
            gobj.register_gobj(gobj)
        gobj.start_up()
        return gobj

    def destroy_gobj(self, gobj):
        """ Destroy a gobj
        """
        #TODO: must would delete child gobjs?
        gobj.deregister_gobj(gobj)
        if gobj.parent is not None:
            gobj.parent.remove_child(gobj)
        del gobj

    def start_up(self):
        """ Initialization zone.

        Well, the __init__ method is used to build the FSM so I need another
        function to initialize the new gobj.
        Please, **override me**, and write here all the code you need to
        start up the machine: create your owns childs, etc.
        This function is called by :meth:`create_gobj`
        after creating the gobj instance.
        """

    def event_factory(self, destination, event, **kw):
        """ Factory to create Event instances.

        :param destination: destination gobj whom to send the event.
        :param event: an :term:`event`.
        :param kw: keyword arguments with associated data to event.
        :rtype: Return Event instance.

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
        if destination is None:
            if hasattr(event, 'destination'):
                destination = event.destination

        if destination is not None:
            if not (issubclass(destination.__class__, string_types) or
                    issubclass(destination.__class__, GObj)):
                raise GObjError(
                    'event_factory() BAD TYPE destination %s in (%s,%s)' %
                    (repr(destination), self.__class__.__name__, self.name))

            if issubclass(destination.__class__, string_types):
                named_gobj = self.search_gobj(destination)
                if not named_gobj:
                    raise GObjError(
                        'event_factory() destination %s NOT FOUND in (%s,%s)' %
                        (repr(destination), self.__class__.__name__, self.name))
                destination = named_gobj

        if not (issubclass(event.__class__, string_types) or
                issubclass(event.__class__, Event)):
            raise EventError('event_factory() BAD TYPE event %s in (%s,%s)' %
                (repr(event), self.__class__.__name__, self.name))

        if issubclass(event.__class__, Event):
            # duplicate the event
            if event.source[-1] != self:
                event.source.append(self)
            event = Event(event.destination, event.event_name,
                    event.source, **event.kw)
            if len(kw):
                event.__dict__.update(**kw)
            if destination is not None:
                event.destination = destination
        else:
            event = Event(destination, event, self, **kw)

        return event

    def send_event(self, destination, event, **kw):
        """
        Send **right now** the :term:`event` ``event`` to the
        destination gobj ``destination``, with associated data ``kw``.

        :param event: :term:`event` to send.
        :param destination: destination :term:`gobj` of the event.
        :param kw: keyword argument with data associated to event.
        :rtype: return the returned value from the executed action.

            .. note::
                All the keyword arguments **are added as attributes** to
                the sent :term:`event`.

        If ``event`` argument is a string type, then the
        :func:`event_factory` function  is called, to create a :class:`Event`
        instance.

        The algorithm to calculate the destination :term:`gobj` will be:

            1. ``destination`` if the ``destination`` argument is not ``None``.
            2. ``event.destination`` if ``event`` is a Event instance and
               ``event.destination`` is not ``None``.
            3. If ``destination`` and ``event.destination`` is None, then
               a :exc:`DestinationError` exception will be raised.

        If the :term:`event-name` exists in the machine, but it's not accepted
        by the current state, then no exception is raised but the
        function **returns** :exc:`EventNotAcceptedError`.

            .. note:: The :meth:`inject_event` method doesn't
                **raise** :exc:`EventNotAcceptedError` because a :term:`machine`
                should run under any circumstances. In any way an action can
                raise exceptions.

        If ``destination`` is a :term:`named-gobj`, i.e. a string, then the gobj
        will be search with :meth:`search_gobj` method. This method must be
        supplied and override by superior instance, like :term:`gaplic`.

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
        event = self.event_factory(destination, event, **kw)
        if event.destination is None:
            raise DestinationError(
                'send_event() destination gobj is None in (%s,%s)' % (
                self.__class__.__name__, self.name))
        ret = event.destination.inject_event(event)
        return ret

    def post_event(self, destination, event, **kw):
        """ Post the event in the event queue. To use with domains like
        :term:`gaplic` because it's necessary to override :meth:`enqueue_event`
        in order to supply a queue system.

        :param event: :term:`event` to send.
        :param destination: destination :term:`gobj` of the event.
        :param kw: keyword argument with data associated to event.

            .. note::
                All the keyword arguments **are added as attributes** to
                the sent :term:`event`.

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
        event = self.event_factory(destination, event, **kw)
        self.enqueue_event(event)

    def enqueue_event(self, event):
        """ Enqueue a event to send by queue system.
        To be overriden by :term:`gaplic` or similar
        """
        raise QueueError(
              'enqueue_event() no support in (%s,%s)' % (
              self.__class__.__name__, self.name))

    def broadcast_event(self, event, **kw):
        """ Broadcast the ``event`` to all subscribers.

        :param event: :term:`event` to send.
        :param kw: keyword argument with data associated to event.

            .. note::
                All the keyword arguments **are added as attributes** to
                the sent :term:`event`.

        Use this function when you don't know who are your event's clients,
        when you don't know the :term:`gobj` destination of
        your :term:`output-event`'s

        If there is no subscriptors, the event is not sent.

        When an event has several subscriptors, there is a mechanism called
        :term:`event-filter` that allows to a subcriptor to own the event
        and no further spread by more subscribers.

        The filter function set by :meth:`set_owned_event_filter` method,
        is call with the returned value of an :term:`action` as argument:
        If the filter function return ``True``, the event is owned, and the
        :func:`ginsfsm.gobj.GObj.broadcast_event` function doesn't continue
        sending the event to other subscribers.

        .. note:: If :func:`ginsfsm.gobj.GObj.broadcast_event` function
           uses :func:`ginsfsm.gobj.GObj.post_event`,
           the :term:`event-filter` cannot be applied.
        """
        sended = False
        if self._some_subscriptions:
            event = self.event_factory(None, event, **kw)
            for sub in self._dl_subscriptions:
                if sub.event_name is None or event.event_name in sub.event_name:
                    if hasattr(sub, 'use_post_event'):
                        ret = self.post_event(sub.subscriber_gobj, event)
                    else:
                        ret = self.send_event(sub.subscriber_gobj, event)
                    sended = True
                    if self.owned_event_filter:
                        ret = self.owned_event_filter(ret)
                        if ret is True:
                            return True  # propietary event, retorno otra cosa?

    def subscribe_event(self, event_name, subscriber_gobj, **kw):
        """ Subscribe to event.

        :param event_name: string event name or tuple/list of string
            event names.  If ``event_name`` is ``None`` then it subscribe
            to all events. If it's not ``None`` then it must be a valid event
            name from the :term:`output-event` list,
            otherwise a :exc:`EventError` will be raised.
        :param subscriber_gobj: subscriber obj that wants receive the event.
            If ``subscriber`` is ``None`` then the subscriber is the parent.
            ``subscriber_gobj`` must be `None` or a `string` or a
            :class:`GObj` types, otherwise a :exc:`GObjError` will be raised.
        :param kw: keyword argument with data associated to subscription.

        **kw** values:
            * `use_post_event`:
              You must set it to `True` in order to broadcast the events
              using `post-event` instead of `send-event`.

        """
        if subscriber_gobj is None:
            subscriber_gobj = self.parent

        if subscriber_gobj is not None:
            if not (issubclass(subscriber_gobj.__class__, string_types) or
                    issubclass(subscriber_gobj.__class__, GObj)):
                raise GObjError(
                    'subcribe_event(): BAD TYPE subscriber_gobj %s in (%s,%s)' %
                    (repr(subscriber_gobj), self.__class__.__name__, self.name))

            if issubclass(subscriber_gobj.__class__, string_types):
                named_gobj = self.search_gobj(subscriber_gobj)
                if not named_gobj:
                    raise GObjError(
                        'subscribe_event() subscriber_gobj %s NOT FOUND in '
                        '(%s,%s)' % (repr(subscriber_gobj),
                        self.__class__.__name__, self.name))
                subscriber_gobj = named_gobj

        if event_name is not None:
            output_events = self.get_output_event_list()

            if not is_nonstr_iter(event_name):
                event_name = (event_name,)

            for name in event_name:
                if not issubclass(name.__class__, string_types):
                    raise EventError(
                        'subscribe_event(): event %s is not string in (%s,%s)'
                        % (repr(name), self.__class__.__name__, self.name))

                if name not in output_events:
                    raise EventError(
                        'subscribe_event(): output-event %s not defined in (%s,%s)'
                        % (repr(event_name), self.__class__.__name__, self.name))

        existing_subs = self._find_subscription(event_name, subscriber_gobj)
        if existing_subs:
            # avoid duplication subscriptions
            self.delete_subscription(existing_subs)
        subscription = _Subscription(event_name, subscriber_gobj, **kw)
        self._dl_subscriptions.add(subscription)
        ln = len(self._dl_subscriptions)
        if ln > 0:
            self._some_subscriptions = True
        else:
            self._some_subscriptions = False

    def _find_subscription(self, event_name, subscriber_gobj):
        """ Find a subscription by event_name and subscriber gobj.
        Internal use to avoid duplicates subscriptions.
        """
        if not is_nonstr_iter(event_name):
            event_name = (event_name,)
        for sub in self._dl_subscriptions:
            if sub.event_name == event_name and \
                sub.subscriber_gobj == subscriber_gobj:
                    return sub

    def delete_subscription(self, event_name, subscriber_gobj):
        """ Remove `subscription`.

        :param event_name: string event name or tuple/list of string
            event names.
        :param subscriber_gobj: subscriber gobj.
        """
        existing_subs = self._find_subscription(event_name, subscriber_gobj)
        if existing_subs:
            self._dl_subscriptions.remove(existing_subs)
            if len(self._dl_subscriptions) == 0:
                self._some_subscriptions = False
            return True
        return False

    def set_owned_event_filter(self, filter):
        """ Set a filter function to be used by :meth:`broadcast_event` function
        to check the owner of events.
        """
        self.owned_event_filter = filter

    def register_gobj(self, gobj):
        """ Register a :term:`named-gobj`.
        To be overriden by :term:`gaplic` or similar.
        """

    def deregister_gobj(self, gobj):
        """ Deregister a :term:`named-gobj`.
        To be overriden by :term:`gaplic` or similar.
        """

    def search_gobj(self, gobj_name):
        """ Search a :term:`named-gobj`.
        To be overriden by :term:`gaplic` or similar.
        """

    def add_child(self, gobj):
        """ Add a child ``gobj``.

        :param gobj: :term:`gobj` child to add.

        Raise :exc:`ParentError` is ``gobj`` already has a parent.
        This function is called by :meth:`create_gobj`
        after creating the gobj instance.
        """
        if gobj.parent:
            raise ParentError(
                'add_child(): gobj already has parent in (%s,%s)' %
                (self.__class__.__name__, self.name))
        self.dl_childs.add(gobj)
        gobj.parent = self

    def remove_child(self, gobj):
        """ Remove the child ``gobj``.

        :param gobj: :term:`gobj` child to remove.

        Raise :exc:`KeyError` is ``gobj`` is not in the childs list.
        This function is called by :meth:`destroy_gobj`.
        """
        self.dl_childs.remove(gobj)
        gobj.parent = None

    def set_trace_mach(self, enable, log=None, level=0):
        """  Enable/Disable machine trace.

        :param enable: Set or reset the trace of fsm.
        :type enable: bool
        :param level: level trace of childs. `0` only this gobj. `-1` all
            tree of childs.
        :rtype: Return the previous value.
        """
        #TODO: doc
        prev = SMachine.set_trace_mach(self, enable, log)
        if level:
            for child in self.dl_childs:
                child.set_trace_mach(enable, log, level-1)
        return prev
