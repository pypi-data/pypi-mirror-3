# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id: ctype.py 26 2012-06-24 18:19:40Z griff1n $
# lib:  pysyncml.ctype
# auth: griffin <griffin@uberdev.org>
# date: 2012/06/23
# copy: (C) CopyLoose 2012 UberDev <hardcore@uberdev.org>, No Rights Reserved.
#------------------------------------------------------------------------------

'''
The ``pysyncml.ctype`` module exposes the
:class:`pysyncml.ctype.ContentTypeInfo` class, which abstracts
content-type handling with respect to transmission, reception and
preferred status within SyncML handling.

For more information and links to documentation, please go to::

  http://pypi.python.org/pypi/pysyncml/

'''

from elementtree import ElementTree as ET
from .common import adict

__all__ = 'ContentTypeInfo',

#------------------------------------------------------------------------------
class ContentTypeInfoMixIn:

  #----------------------------------------------------------------------------
  def merge(self, other):
    if self.ctype != other.ctype \
       or self.versions != other.versions \
       or self.preferred != self.preferred:
      return False
    self.transmit = self.transmit or other.transmit
    self.receive = self.receive or other.receive
    return True

  #----------------------------------------------------------------------------
  def __str__(self):
    ret = '%s@%s:' % (self.ctype, ','.join(self.versions))
    if self.preferred:
      ret += 'Pref'
    if self.transmit:
      ret += 'Tx'
    if self.receive:
      ret += 'Rx'
    return ret

  # #----------------------------------------------------------------------------
  # def describe(self, s1):
  #   print >>s1, self

  #----------------------------------------------------------------------------
  def toSyncML(self, nodeName=None):
    ret = ET.Element(nodeName or 'ContentType')
    ET.SubElement(ret, 'CTType').text = self.ctype
    for v in self.versions:
      ET.SubElement(ret, 'VerCT').text = v
    return ret

  #----------------------------------------------------------------------------
  @classmethod
  def fromSyncML(klass, xnode):
    return klass(
      ctype     = xnode.findtext('CTType'),
      versions  = [x.text for x in xnode.findall('VerCT')],
      preferred = xnode.tag.endswith('-Pref'),
      transmit  = 'Tx' in xnode.tag,
      receive   = 'Rx' in xnode.tag,
      )

#------------------------------------------------------------------------------
class ContentTypeInfo(adict, ContentTypeInfoMixIn):

  #----------------------------------------------------------------------------
  def __init__(self, ctype=None, versions=None,
               preferred=False, transmit=True, receive=True,
               *args, **kw):
    super(ContentTypeInfo, self).__init__(*args, **kw)
    self.ctype     = ctype
    if isinstance(versions, basestring):
      versions = [versions]
    self.versions  = versions
    self.preferred = preferred
    self.transmit  = transmit
    self.receive   = receive

  def __str__(self):
    return ContentTypeInfoMixIn.__str__(self)

  def __repr__(self):
    return ContentTypeInfoMixIn.__repr__(self)

#------------------------------------------------------------------------------
# end of $Id: ctype.py 26 2012-06-24 18:19:40Z griff1n $
#------------------------------------------------------------------------------
