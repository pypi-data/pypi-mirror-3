# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id: base.py 25 2012-06-21 12:59:41Z griff1n $
# lib:  pysyncml.items.base
# auth: griffin <griffin@uberdev.org>
# date: 2012/05/13
# copy: (C) CopyLoose 2012 UberDev <hardcore@uberdev.org>, No Rights Reserved.
#------------------------------------------------------------------------------

'''
The ``pysyncml.items.base`` module defines the abstract interface to a
SyncML :class:`pysyncml.items.base.Item`, the base class for all SyncML
synchronized objects.

For more information and links to documentation, please go to::

  http://pypi.python.org/pypi/pysyncml/

'''

import StringIO
from .. import constants

#------------------------------------------------------------------------------
class Item(object):

  #----------------------------------------------------------------------------
  def __init__(self, id=None, state=None, *args, **kw):
    super(Item, self).__init__(*args, **kw)
    self.id = id

  #----------------------------------------------------------------------------
  def dump(self, stream, contentType=None, version=None):
    '''
    Converts this Item to serialized form, such that it can be
    transported over the wire and outputs it to the provided file-like
    `stream` object. For agents that support multiple content-types,
    the desired `contentType` and `version` will be specified as a
    parameter. If `contentType` and `version` are None, appropriate
    default values should be used.
    '''
    raise NotImplementedError()

  #----------------------------------------------------------------------------
  def dumps(self, contentType=None, version=None):
    '''
    Identical to :method:`dump`, except the serialized form is returned
    as a string representation.
    '''
    buf = StringIO.StringIO()
    self.dump(buf, contentType, version)
    return buf.getvalue()

  #----------------------------------------------------------------------------
  @classmethod
  def load(cls, stream, contentType=None, version=None):
    '''
    Reverses the effects of the :method:`dump` method, and returns the
    de-serialized Item from the file-like source `stream`.

    Note: `version` will typically be ``None``, so it should either be
    auto-determined, or not used. This is an issue in the SyncML
    protocol, and is only here for symmetry with :method:`dump` and as
    "future-proofing".
    '''
    raise NotImplementedError()

  #----------------------------------------------------------------------------
  @classmethod
  def loads(cls, data, contentType=None, version=None):
    '''
    Identical to :method:`load`, except the serialized form is provided as
    a string representation in `data` instead of as a stream.
    '''
    buf = StringIO.StringIO(data)
    return cls.load(buf, contentType, version)

  #----------------------------------------------------------------------------
  def __repr__(self):
    ret = '<%s.%s' % (self.__class__.__module__, self.__class__.__name__)
    for key, val in self.__dict__.items():
      val = repr(val)
      if len(val) > 40:
        val = val[:40] + '...'
      ret += ' %s=%s' % (key, val)
    return ret + '>'

#------------------------------------------------------------------------------
class Ext(object):

  #----------------------------------------------------------------------------
  def __init__(self, *args, **kw):
    super(Ext, self).__init__(*args, **kw)
    # extensions - dict: keys => ( list ( values ) )
    self.extensions  = dict()

  #----------------------------------------------------------------------------
  def addExtension(self, name, value):
    if name not in self.extensions:
      self.extensions[name] = []
    self.extensions[name].append(value)

#------------------------------------------------------------------------------
# end of $Id: base.py 25 2012-06-21 12:59:41Z griff1n $
#------------------------------------------------------------------------------
