# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# folder: $Id: test_folder.py 21 2012-06-03 17:30:49Z griff1n $
# lib:  pysyncml.items.test_folder
# auth: griffin <griffin@uberdev.org>
# date: 2012/05/19
# copy: (C) CopyLoose 2012 UberDev <hardcore@uberdev.org>, No Rights Reserved.
#------------------------------------------------------------------------------

import unittest, logging
from .folder import FolderItem

# kill logging
logging.disable(logging.CRITICAL)

#------------------------------------------------------------------------------
class TestFolder(unittest.TestCase):

  #----------------------------------------------------------------------------
  def test_xml_simple(self):
    fi = FolderItem(id='0', name='foldername')
    self.assertEqual('<Folder><name>foldername</name></Folder>', fi.dumps())

  #----------------------------------------------------------------------------
  def test_xml_attributes(self):
    fi = FolderItem(id='0', name='n', hidden=True, system=False)
    self.assertEqual('<Folder><name>n</name><attributes><h>true</h><s>false</s></attributes></Folder>', fi.dumps())

  #----------------------------------------------------------------------------
  def test_xml_dates(self):
    fi = FolderItem(id='0', name='n', created=1234567890)
    self.assertEqual('<Folder><name>n</name><created>20090213T233130Z</created></Folder>', fi.dumps())

#------------------------------------------------------------------------------
# end of $Id: test_folder.py 21 2012-06-03 17:30:49Z griff1n $
#------------------------------------------------------------------------------
