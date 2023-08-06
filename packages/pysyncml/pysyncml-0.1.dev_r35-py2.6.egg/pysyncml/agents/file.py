# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id: file.py 34 2012-07-03 02:48:00Z griff1n $
# auth: griffin <griffin@uberdev.org>
# date: 2012/05/13
# copy: (C) CopyLoose 2012 UberDev <hardcore@uberdev.org>, No Rights Reserved.
#------------------------------------------------------------------------------

'''
The ``pysyncml.agents.file`` module provides helper routines and classes to
deal with SyncML file and folder object types.
'''

from . import base
from .. import constants
from ..items import FileItem, FolderItem

#------------------------------------------------------------------------------
class BaseFileAgent(base.Agent):

  #----------------------------------------------------------------------------
  def __init__(self, *args, **kw):
    super(BaseFileAgent, self).__init__(*args, **kw)
    self.contentTypes = [
      base.ContentTypeInfo(constants.TYPE_OMADS_FILE, '1.2', True),
      base.ContentTypeInfo(constants.TYPE_OMADS_FOLDER, '1.2', True),
      ]

  #----------------------------------------------------------------------------
  def loadItem(self, stream, contentType=None, version=None):
    if contentType is not None and contentType.startswith(constants.TYPE_OMADS_FOLDER):
      return FolderItem.load(stream, contentType, version)
    return FileItem.load(stream, contentType, version)

  #----------------------------------------------------------------------------
  def dumpItem(self, item, stream, contentType=None, version=None):
    # todo: is this "getItem" really necessary?...
    return self.getItem(item.id).dump(stream, contentType, version)

#------------------------------------------------------------------------------
# end of $Id: file.py 34 2012-07-03 02:48:00Z griff1n $
#------------------------------------------------------------------------------
