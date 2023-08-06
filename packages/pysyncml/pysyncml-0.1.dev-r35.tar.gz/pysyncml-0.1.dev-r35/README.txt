.. ----------------------------------------------------------------------------
.. file: $Id: README.txt 32 2012-07-02 17:09:43Z griff1n $
.. desc: pysyncml README.txt file
.. auth: griffin <griffin@uberdev.org>
.. date: 2012/04/22
.. copy: (C) CopyLoose 2012 UberDev <hardcore@uberdev.org>, No Rights Reserved.
.. ----------------------------------------------------------------------------

.. _readme.welcome:

Welcome to pysyncml
===================

Welcome to the ``pysyncml`` library, a pure-python implementation of
the SyncML adapter framework and protocol. SyncML_ is a protocol for
allowing abstract objects to be synchronized between multiple clients
and a server.

.. important::

  2012/07/01: ``pysyncml`` is currently alpha. That means very little
  really works yet! However, it is being actively developed, so check
  back in a couple of months.

  Functional components as of 0.1.dev-r30:

  * Client-side SyncML framework with support for CRUD operations,
    i.e. Add/Replace/Delete Sync commands.
  * Client-side synchronization of "note" datatype.

.. _readme.goals:

Goals
=====

The ``pysyncml`` project has the following goals, some of them diverge
critically from other SyncML implementations and are the reasons for
creating a new package instead of building on other existing
implementations:

* Can be installed and used with a single "``pip install pysyncml``"
  (or easy_install).
* Is python 2.6+ and 3+ compatible.
* Implements a sufficiently large subset of the SyncML 1.2.2 (a.k.a.
  the OMA Data Synchronization specification) as to be interoperable
  with other implementations without necessarily being "conformant".
* Can be easily integrated into sqlalchemy_ based projects to
  store data in the application's database instead of separated out
  (so that integrated database triggers and cascading can be applied).
* Can be extended in order to make properly crafted clients able
  to operate in "distributed" mode - this means that in the absence
  of a network, SyncML client peers are able to synchronize with
  each other in the anticipation that the central server may or may
  not eventually become available again.
* Differentiates as little as possible between "client" and "server"
  modes to enable the previous goal.
* Makes basic synchronization easy and complicated synchronization
  possible by providing standard implementations for commonly used
  approaches, while allowing these components to be overriden or
  extended.
* Provides basic command line tools for commonly synchronized data
  types.
* Provides a framework of server-push notifications which are
  transport agnostic.
* Auto-discovery of SyncML server URI locations; i.e. finding the
  "right" paths to bind object types is done automatically instead
  of needing error-prone user configuration.

Limitations
===========

It is the goal of the project to get a minimally functional library going
in the shortest possible timeframe. To that end, the following features
of SyncML will *NOT* be implemented until a later phase, even if this means
that the library does not provide a conformant implementation:

* NOT supported: filtering of searches or synchronization targets.
* NOT supported: data split over multiple messages.
* NOT supported: soft-deletes.
* NOT supported: memory constraint management.
* NOT supported: suspend, resume and busy signaling.
* NOT supported: MD5 authentication scheme.
* NOT supported: per-database-layer authorization.

Installation
============

Installation of ``pysyncml`` is near-trivial with PIP_::

  $ pip install pysyncml

or, using easy_install_::

  $ easy_install pysyncml

.. _readme.docref:

Documentation
=============

For downloaded packages, please see the generated documents in the
"doc" directory, otherwise you can find links to the latest how-to and
API reference documentation at pysyncml_.

.. _SyncML: http://en.wikipedia.org/wiki/SyncML
.. _sqlalchemy: http://www.sqlalchemy.org
.. _PIP: http://www.pip-installer.org
.. _easy_install: http://peak.telecommunity.com/DevCenter/EasyInstall
.. _pysyncml: http://www.pysyncml.org

.. ----------------------------------------------------------------------------
.. end of $Id: README.txt 32 2012-07-02 17:09:43Z griff1n $
.. ----------------------------------------------------------------------------
