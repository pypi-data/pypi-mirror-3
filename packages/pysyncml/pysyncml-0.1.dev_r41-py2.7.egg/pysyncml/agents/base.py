# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id: base.py 37 2012-07-21 16:32:26Z griff1n $
# lib:  pysyncml.agents.base
# auth: griffin <griffin@uberdev.org>
# date: 2012/04/21
# copy: (C) CopyLoose 2012 UberDev <hardcore@uberdev.org>, No Rights Reserved.
#------------------------------------------------------------------------------

'''
This module defines the abstract interface :class:`pysyncml.Agent
<pysyncml.agents.base.Agent>`, the base class for all pysyncml
synchronization agents.
'''

import sys, json, StringIO
from elementtree import ElementTree as ET

#------------------------------------------------------------------------------
class Agent(object):
  '''
  The ``Agent`` interface is how the pysyncml Adapter interacts with
  the actual objects being synchronized.  The data is expected to be
  stored by the calling framework, and pysyncml manages the protocol
  for synchronization. This API defines the core required methods that
  need to be implemented (:meth:`addItem`, :meth:`getItem`,
  :meth:`replaceItem`, :meth:`deleteItem`, :meth:`getAllItems`,
  :meth:`loadItem`, :meth:`dumpItem`), as well as several optional
  methods that can be implemented for optimization purposes.
  '''

  #----------------------------------------------------------------------------
  def __init__(self, contentTypes=None, *args, **kw):
    super(Agent, self).__init__(*args, **kw)
    self.contentTypes = contentTypes

  # helper methods
  #----------------------------------------------------------------------------
  def deleteAllItems(self):
    '''
    [OPTIONAL] Deletes all items stored by this Agent. The default
    implementation simply iterates over :meth:`getAllItems` and
    deletes them one at a time.
    '''
    for item in self.getAllItems():
      self.deleteItem(item.id)

  #============================================================================
  # serialization methods -- these MUST be implemented
  #============================================================================

  # TODO: ideally, both would be implemented to call each other, but a
  #       trap for Recursion depth exception would be set so that i can
  #       warn about that... that would allow the sub-classer to implement
  #       either. the `(dump|load)*s*Item` should probably be the "optimized"
  #       route... ie. the non-string version should do the recursion check.

  #----------------------------------------------------------------------------
  def dumpItem(self, item, stream, contentType=None, version=None):
    '''
    Converts the specified `item` to serialized form (such that it can
    be transported over the wire) and writes it to the provided
    file-like `stream` object. For agents that support multiple
    content-types, the desired `contentType` and `version` will be
    specified as a parameter. If `contentType` and `version` are None,
    appropriate default values should be used.
    '''
    raise NotImplementedError()

  #----------------------------------------------------------------------------
  def dumpsItem(self, item, contentType=None, version=None):
    '''
    [OPTIONAL] Identical to :meth:`dumpItem`, except the serialized
    form is returned as a string representation. The default
    implementation just wraps :meth:`dumpItem`.
    '''
    buf = StringIO.StringIO()
    self.dumpItem(item, buf, contentType, version)
    return buf.getvalue()

  #----------------------------------------------------------------------------
  def loadItem(self, stream, contentType=None, version=None):
    '''
    Reverses the effects of the :meth:`dumpItem` method, and returns
    the de-serialized Item from the file-like source `stream`.

    Note: `version` will typically be ``None``, so it should either be
    auto-determined, or not used. This is an issue in the SyncML
    protocol, and is only here for symmetry with :meth:`dumpItem`
    and as "future-proofing".
    '''
    raise NotImplementedError()

  #----------------------------------------------------------------------------
  def loadsItem(self, data, contentType=None, version=None):
    '''
    [OPTIONAL] Identical to :meth:`loadItem`, except the serialized
    form is provided as a string representation in `data` instead of
    as a stream. The default implementation just wraps
    :meth:`loadItem`.
    '''
    buf = StringIO.StringIO(data)
    return self.loadItem(buf, contentType, version)

  #============================================================================
  # core syncing methods -- these MUST be implemented
  #============================================================================

  #----------------------------------------------------------------------------
  def getAllItems(self):
    '''
    Returns an iterable of all the items stored in the local datastore.
    '''
    raise NotImplementedError()

  #----------------------------------------------------------------------------
  def addItem(self, item):
    '''
    The specified `item`, which will have been created via a prior
    ``loadItem()``, is added to the local datastore. This method
    returns either a new :class:`pysyncml.Item
    <pysyncml.items.base.Item>` instance or the same `item` that was
    passed --- in either case, the returned item **MUST** have a valid
    :attr:`pysyncml.Item.id <pysyncml.items.base.Item.id>` attribute.
    '''
    raise NotImplementedError()

  #----------------------------------------------------------------------------
  def getItem(self, itemID):
    '''
    Returns the :class:`pysyncml.Item <pysyncml.items.base.Item>`
    instance associated with the specified `itemID`, which may or may
    not have been converted to a string.
    '''
    raise NotImplementedError()

  #----------------------------------------------------------------------------
  def replaceItem(self, item):
    '''
    Updates the local datastore item with ID `item.id` to the value
    provided as `item`, which will have been created via a prior
    ``loadItem()``.
    '''
    raise NotImplementedError()

  #----------------------------------------------------------------------------
  def deleteItem(self, itemID):
    '''
    Deletes the local datastore item with ID `itemID`.
    '''
    raise NotImplementedError()

  #============================================================================
  # extended syncing methods -- these SHOULD be implemented
  #============================================================================

  #----------------------------------------------------------------------------
  def matchItem(self, item):
    return None

  # other methods in SyncML spec:
  # def copyItem(self, item):                         raise NotImplementedError()
  # def execItem(self, item):                         raise NotImplementedError()
  # def moveItem(self, item):                         raise NotImplementedError()
  # def putItem(self, item):                          raise NotImplementedError()
  # def searchItem(self, item):                       raise NotImplementedError()

#------------------------------------------------------------------------------
# end of $Id: base.py 37 2012-07-21 16:32:26Z griff1n $
#------------------------------------------------------------------------------
