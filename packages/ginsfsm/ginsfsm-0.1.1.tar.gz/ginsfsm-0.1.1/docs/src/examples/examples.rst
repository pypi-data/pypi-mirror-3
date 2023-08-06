********
Examples
********

.. _example1:

========
Example1
========

Use GTimer :term:`gclass` to do two tasks.

.. literalinclude:: ../../../ginsfsm/examples/example1.py
    :linenos:

.. _example2:

========
Example2
========

Use GSock :term:`gclass`. Connect to google, get /, and disconnect, periodically.

.. literalinclude:: ../../../ginsfsm/examples/example2.py
    :linenos:

.. _example3:

========
Example3
========

Use GConnex :term:`gclass`. Send a query to google and twitter alternatively.
How? send the query each 10 seconds, but set a timeout_inactivity of 5.
In each disconnection the next connection will swing between the
two destinations.

.. literalinclude:: ../../../ginsfsm/examples/example3.py
    :linenos:

.. _example4:

========
Example4
========

Use GServerSock and GConnex.
Run two gaplics. One is the server, the other the client.
Stress with many connections and many data. The server echo the data.
Configure:
* The server can run as thread o child process.
* Maximum number of client connections.

.. literalinclude:: ../../../ginsfsm/examples/example4.py
    :linenos:

.. _example5:

========
Example5
========

Client
======

.. literalinclude:: ../../../ginsfsm/examples/example5-client.py
    :linenos:

Server
======

.. literalinclude:: ../../../ginsfsm/examples/example5-server.py
    :linenos:
