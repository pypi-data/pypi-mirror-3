GinsFSM
=======

GinsFSM is a python library to develop systems based in finite-state machines
(http://en.wikipedia.org/wiki/Finite-state_machine).
This model is really useful when writing networking and communication
applications.

The idea is very simple:

    * All objects, called `gobj`, are instances of a derived
      `ginsfsm.gobj.GObj` class, that we call `gclass`.
    * The `gclass` has an inner `simple-machine`
      that defines its behavior.
    * The communication between `gobj`'s happens via `event`'s.

Thus, the nature of this system is fully asynchronous and event-driven.

The interface is simple and common to all objects; you just have to change the
name of the event and the data they carry.

Support and Documentation
-------------------------

See the <http://ginsfsm.org/> to view documentation.

Code available in <https://bitbucket.org/artgins/ginsfsm>

License
-------

GinsFSM is released under terms of The ISC
License ISC <http://www.opensource.org/licenses/isc-license>.

Authors
-------

GinsFSM is made available by ArtGins <http://artgins.com>
and a team of contributors.
