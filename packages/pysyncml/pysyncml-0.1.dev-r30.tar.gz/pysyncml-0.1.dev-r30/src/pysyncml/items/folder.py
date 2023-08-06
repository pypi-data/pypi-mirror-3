# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id: folder.py 24 2012-06-19 19:35:12Z griff1n $
# lib:  pysyncml.items.folder
# auth: griffin <griffin@uberdev.org>
# date: 2012/05/13
# copy: (C) CopyLoose 2012 UberDev <hardcore@uberdev.org>, No Rights Reserved.
#------------------------------------------------------------------------------

'''
The ``pysyncml.items.file`` module defines the abstract interface to an
OMA DS Folder object via the :class:`pysyncml.items.folder.FolderItem` class.

For more information and links to documentation, please go to::

  http://pypi.python.org/pypi/pysyncml/

'''

import os
import elementtree.ElementTree as ET
from .base import Item, Ext
from .. import constants, common

#------------------------------------------------------------------------------
class FolderItem(Item, Ext):

  #----------------------------------------------------------------------------
  def __init__(self, name=None, parent=None,
               created=None, modified=None, accessed=None,
               role=None,
               hidden=None, system=None, archived=None, delete=None,
               writable=None, readable=None, executable=None,
               *args, **kw):
    super(FolderItem, self).__init__(*args, **kw)
    self.name        = name
    self.parent      = parent
    self.created     = created
    self.modified    = modified
    self.accessed    = accessed
    self.role        = role
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
    # TBD: check contentType...
    # TBD: check version...
    root = ET.Element('Folder')
    if self.name is not None:
      ET.SubElement(root, 'name').text = self.name
    for attr in ('created', 'modified', 'accessed'):
      if getattr(self, attr) is None:
        continue
      ET.SubElement(root, attr).text = common.ts_iso(getattr(self, attr))
    if self.role is not None:
      ET.SubElement(root, 'role').text = self.role
    attrs = [attr
             for attr in ('hidden', 'system', 'archived', 'delete', 'writable', 'readable', 'executable')
             if getattr(self, attr) is not None]
    if len(attrs) > 0:
      xa = ET.SubElement(root, 'attributes')
      for attr in attrs:
        ET.SubElement(xa, attr[0]).text = 'true' if getattr(self, attr) else 'false'
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
    ret = FolderItem()
    ret.name       = os.path.basename(path)
    ret.accessed   = stat.st_atime
    ret.modified   = stat.st_mtime
    ret.created    = stat.st_ctime # TBD: this is only correct on windows!...
    # TBD: load folder attributes as well...
    return ret

#------------------------------------------------------------------------------
# end of $Id: folder.py 24 2012-06-19 19:35:12Z griff1n $
#------------------------------------------------------------------------------
