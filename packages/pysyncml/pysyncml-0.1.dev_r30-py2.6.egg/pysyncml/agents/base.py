# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id: base.py 29 2012-06-30 22:52:55Z griff1n $
# lib:  pysyncml.agents.base
# auth: griffin <griffin@uberdev.org>
# date: 2012/04/21
# copy: (C) CopyLoose 2012 UberDev <hardcore@uberdev.org>, No Rights Reserved.
#------------------------------------------------------------------------------

'''
The ``pysyncml.agent`` package exposes the Agent interface, which is
how the pysyncml Adapter interfaces with the actual objects being
synchronized.  The data is expected to be stored by the calling
framework, and pysyncml manages the protocol for synchronization.

For more information and links to documentation, please go to::

  http://pypi.python.org/pypi/pysyncml/

'''

import sys, json, StringIO
from elementtree import ElementTree as ET

#------------------------------------------------------------------------------
class Agent(object):

  #----------------------------------------------------------------------------
  def __init__(self, contentTypes=None, *args, **kw):
    super(Agent, self).__init__(*args, **kw)
    self.contentTypes = contentTypes

  # helper methods
  def deleteAllItems(self):
    for item in self.getAllItems():
      self.deleteItem(item.id)

  # serialization methods -- these MUST be implemented
  # TBD: ideally, both would be implemented to call each other, but a
  #      trap for Recursion depth exception would be set so that i can
  #      warn about that... that would allow the sub-classer to implement
  #      either. the `(dump|load)*s*Item` should probably be the "optimized"
  #      route... ie. the non-string version should do the recursion check.
  def loadItem(self, stream, contentType=None, version=None):
    '''
    Note: `version` will typically be ``None``, so it should either be
    auto-determined, or not used. This is an issue in the SyncML protocol,
    and is only here for symmetry with `dump()` and as "future-proofing".
    '''
    raise NotImplementedError()
  def loadsItem(self, data, contentType=None, version=None):
    buf = StringIO.StringIO(data)
    return self.loadItem(buf, contentType, version)
  def dumpItem(self, item, stream, contentType=None, version=None):
    raise NotImplementedError()
  def dumpsItem(self, item, contentType=None, version=None):
    buf = StringIO.StringIO()
    self.dumpItem(item, buf, contentType, version)
    return buf.getvalue()

  # core syncing methods -- these MUST be implemented
  def getAllItems(self):
    '''
    Returns an iterable of all the items stored in the local datastore.
    '''
    raise NotImplementedError()
  def addItem(self, item):
    '''
    The specified `item`, which will have been created via a prior
    ``loadItem()``, is added to the local datastore. This method
    returns either a new :class:`pysyncml.items.Item` instance or the
    same `item` which *MUST* have a valid ``id`` attribute.
    '''
    raise NotImplementedError()
  def getItem(self, itemID):
    '''
    Returns the :class:`pysyncml.items.Item` instance associated with
    the specified item ID, which may or may not have been converted to
    a string.
    '''
    raise NotImplementedError()
  def replaceItem(self, item):
    '''
    Updates the local datastore item with ID `item.id` to the value
    provided as `item`, which will have been created via a prior
    ``loadItem()``.
    '''
    raise NotImplementedError()
  def deleteItem(self, itemID):
    '''
    Deletes the local datastore item with ID `itemID`.
    '''
    raise NotImplementedError()

  # extended syncing methods -- these SHOULD be implemented
# def copyItem(self, item):                         raise NotImplementedError()
# def execItem(self, item):                         raise NotImplementedError()
# def moveItem(self, item):                         raise NotImplementedError()
# def putItem(self, item):                          raise NotImplementedError()
# def searchItem(self, item):                       raise NotImplementedError()

#------------------------------------------------------------------------------
# end of $Id: base.py 29 2012-06-30 22:52:55Z griff1n $
#------------------------------------------------------------------------------
