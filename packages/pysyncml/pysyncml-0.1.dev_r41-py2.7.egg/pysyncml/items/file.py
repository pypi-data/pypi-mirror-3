# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id: file.py 34 2012-07-03 02:48:00Z griff1n $
# lib:  pysyncml.items.file
# auth: griffin <griffin@uberdev.org>
# date: 2012/05/13
# copy: (C) CopyLoose 2012 UberDev <hardcore@uberdev.org>, No Rights Reserved.
#------------------------------------------------------------------------------

'''
The ``pysyncml.items.file`` module defines the abstract interface to an
OMA DS File object via the :class:`pysyncml.items.file.FileItem` class.
'''

import os
import elementtree.ElementTree as ET
from .base import Item, Ext
from .. import constants, common

#------------------------------------------------------------------------------
class FileItem(Item, Ext):

  #----------------------------------------------------------------------------
  def __init__(self, name=None, parent=None,
               created=None, modified=None, accessed=None,
               contentType=None, body=None, size=None,
               hidden=None, system=None, archived=None, delete=None,
               writable=None, readable=None, executable=None,
               *args, **kw):
    super(FileItem, self).__init__(*args, **kw)
    self.name        = name
    self.parent      = parent
    self.created     = created
    self.modified    = modified
    self.accessed    = accessed
    self.contentType = contentType
    self.body        = body
    self.size        = size
    # attributes
    self.hidden      = hidden
    self.system      = system
    self.archived    = archived
    self.delete      = delete
    self.writable    = writable
    self.readable    = readable
    self.executable  = executable

  #----------------------------------------------------------------------------
  def dump(self, stream, contentType=None, version=None):
    # TODO: check contentType...
    # TODO: check version...
    root = ET.Element('File')
    if self.name is not None:
      ET.SubElement(root, 'name').text = self.name
    for attr in ('created', 'modified', 'accessed'):
      if getattr(self, attr) is None:
        continue
      ET.SubElement(root, attr).text = common.ts_iso(getattr(self, attr))
    if self.contentType is not None:
      ET.SubElement(root, 'cttype').text = self.contentType
    attrs = [attr
             for attr in ('hidden', 'system', 'archived', 'delete', 'writable', 'readable', 'executable')
             if getattr(self, attr) is not None]
    if len(attrs) > 0:
      xa = ET.SubElement(root, 'attributes')
      for attr in attrs:
        ET.SubElement(xa, attr[0]).text = 'true' if getattr(self, attr) else 'false'
    if self.body is not None:
      ET.SubElement(root, 'body').text = self.body
    if self.size is not None:
      ET.SubElement(root, 'size').text = self.size
    if len(self.extensions) > 0:
      xe = ET.SubElement(root, 'Ext')
      for name, values in self.extensions.items():
        ET.SubElement(xe, 'XNam').text = name
        for value in values:
          ET.SubElement(xe, 'XVal').text = value
    ET.ElementTree(root).write(stream)

  #----------------------------------------------------------------------------
  @staticmethod
  def fromFilesystem(path):
    stat = os.stat(path)
    ret = FileItem()
    ret.name       = os.path.basename(path)
    ret.accessed   = stat.st_atime
    ret.modified   = stat.st_mtime
    ret.created    = stat.st_ctime # TODO: this is only correct on windows!...
    # TODO: load folder attributes as well...
    return ret

#------------------------------------------------------------------------------
# end of $Id: file.py 34 2012-07-03 02:48:00Z griff1n $
#------------------------------------------------------------------------------
