.. GinsFSM documentation master file, created by
   sphinx-quickstart on Sun Oct 23 20:50:35 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Wellcome
========

GinsFSM is a python library to develop systems based in finite-state machines
(`FSM <http://en.wikipedia.org/wiki/Finite-state_machine>`_).

This model is really useful when writing networking and communication
applications.
It has been my programming style over 20 years of C language development,
and now that I’m moving to python,
I want to continue with that approach.
I’m from Madrid (Spain). My English is very bad,
so I would appreciate you telling any mistake you see.


Installation
============

You can install the library with ``easy_install``::

    easy_install ginsfsm

or with ``pip``::

    pip install ginsfsm

Documentation in http://ginsfsm.org/.

Code available in https://bitbucket.org/artgins/ginsfsm


Basic Idea
==========

Main classes:

.. image:: ginsfsm-classes.png


Briefly:

* :class:`ginsfsm.gconfig.GConfig`:

  Implements a flexible global configuration system,
  defining a :term:`gconfig-template`.

* :class:`ginsfsm.smachine.SMachine`:

  Implements a simple Finite State Machine,
  defining a :term:`simple-machine`.

* :class:`ginsfsm.gobj.GObj`:

  Well, yes, I'm a very simple brain. Only a machine.

  But you write a good FSM, and I never fail you:

  * derive me,
  * write my :term:`simple-machine` FSM,
  * tell the world how they can parameterize me with a :term:`gconfig-template`,
  * and let me run.

  Now I can feed my machine receiving external events,
  and me too can communicate with others :term:`gobj`'s sending them events.

* :class:`ginsfsm.gaplic.GAplic`:

  Me? Well, I'm too a :term:`gobj`. I'm the root, the grandfather, and I can:

  * supply the main loop in a thread o subprocess context.
  * house all the child :term:`gobj`'s who want.
  * serve as a bridge to other :term:`gaplic` for send/receive events.
  * and more...

The communication between :term:`gobj`'s happens via :term:`event`'s.

The nature of this system is **fully asynchronous** and **event-driven**.

The interface is simple and common to all objects; you just have to change the
name of the event and the data they carry.


Documentation
=============

.. toctree::
    :maxdepth: 1

    api
    examples

License
=======

    Copyright (c) 2012, Ginés Martínez Sánchez.

    GinsFSM is released under terms of The MIT
    License <http://www.opensource.org/licenses/mit-license>


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
