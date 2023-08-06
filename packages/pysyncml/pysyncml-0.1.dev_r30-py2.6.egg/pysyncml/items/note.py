# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# note: $Id: note.py 24 2012-06-19 19:35:12Z griff1n $
# lib:  pysyncml.items.note
# auth: griffin <griffin@uberdev.org>
# date: 2012/05/13
# copy: (C) CopyLoose 2012 UberDev <hardcore@uberdev.org>, No Rights Reserved.
#------------------------------------------------------------------------------

'''
The ``pysyncml.items.note`` module defines the abstract interface to a
Note object via the :class:`pysyncml.items.note.NoteItem` class.

.. warning::
  Beware as this is NOT a standard SyncML object type.

For more information and links to documentation, please go to::

  http://pypi.python.org/pypi/pysyncml/

'''

import os, re
import elementtree.ElementTree as ET
from .base import Item, Ext
from .. import constants, common

#------------------------------------------------------------------------------
class NoteItem(Item, Ext):

  #----------------------------------------------------------------------------
  def __init__(self, name=None, body=None, *args, **kw):
    super(NoteItem, self).__init__(*args, **kw)
    self.name        = name
    self.body        = body

  #----------------------------------------------------------------------------
  def dump(self, stream, contentType=None, version=None):
    if contentType is None or contentType == constants.TYPE_TEXT_PLAIN:
      stream.write(self.body)
      return
    if contentType == constants.TYPE_SIF_NOTE:
      root = ET.Element('note')
      # TBD: check `version`...
      ET.SubElement(root, 'SIFVersion').text = '1.1'
      if self.name is not None:
        ET.SubElement(root, 'Subject').text = self.name
      if self.body is not None:
        ET.SubElement(root, 'Body').text = self.body
      for name, values in self.extensions.items():
        for value in values:
          ET.SubElement(root, name).text = value
      ET.ElementTree(root).write(stream)
      return
    raise common.InvalidContentType('cannot serialize note to "%s"' % (contentType,))

  #----------------------------------------------------------------------------
  @classmethod
  def load(cls, stream, contentType=None, version=None):
    if contentType is None or contentType == constants.TYPE_TEXT_PLAIN:
      data = stream.read()
      name = data.split('\n')[0]
      # tbd: localize?!...
      name = re.compile(r'^(title|name):\s*', re.IGNORECASE).sub('', name).strip()
      return NoteItem(name=name, body=data)
    if contentType == constants.TYPE_SIF_NOTE:
      data = ET.parse(stream).getroot()
      ret = NoteItem(name=data.findtext('Subject'), body=data.findtext('Body'))
      for child in data:
        if child.tag in ('SIFVersion', 'Subject', 'Body'):
          continue
        ret.addExtension(child.tag, child.text)
      return ret
    raise common.InvalidContentType('cannot de-serialize note from "%s"' % (contentType,))

#------------------------------------------------------------------------------
# end of $Id: note.py 24 2012-06-19 19:35:12Z griff1n $
#------------------------------------------------------------------------------
