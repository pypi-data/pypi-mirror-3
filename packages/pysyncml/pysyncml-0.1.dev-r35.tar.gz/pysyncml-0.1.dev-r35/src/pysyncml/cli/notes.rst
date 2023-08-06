.. -------------------------------------------------------------------------------
.. file: $Id$
.. auth: griffin <griffin@uberdev.org>
.. date: 2012/07/01
.. copy: (C) CopyLoose 2012 UberDev <hardcore@uberdev.org>, No Rights Reserved.
.. -------------------------------------------------------------------------------

Sample Implementation: sync-notes
=================================

Below is a sample client-side implementation of a pysyncml
client. Please note that it uses some of the more advanced features of
pysyncml, and may therefore appear overwhelming. For a simpler general
guide to implementing client-side SyncML adapters with pysyncml,
please see the :doc:`../client` guide.

Approach
--------

The ``sync-notes`` program maintains the synchronization of a set of
files in a given directory with a remote "Note" storage SyncML server.
When launched, it scans the directory for any changes, such as new
files, deleted files, or modified files and reports those changes to
the local :meth:`pysyncml.Context.Adapter
<pysyncml.context.Context.Adapter>`. Then (and at user option), it
synchronizes with a potentially pre-configured remote SyncML peer.

Code
----

.. include:: notes.py
   :literal:
   :number-lines:

.. ----------------------------------------------------------------------------
.. end of $Id: README.txt 24 2012-06-19 19:35:12Z griff1n $
.. ----------------------------------------------------------------------------
