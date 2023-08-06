# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id: test_file.py 21 2012-06-03 17:30:49Z griff1n $
# lib:  pysyncml.items.test_file
# auth: griffin <griffin@uberdev.org>
# date: 2012/05/19
# copy: (C) CopyLoose 2012 UberDev <hardcore@uberdev.org>, No Rights Reserved.
#------------------------------------------------------------------------------

import unittest, logging
from .file import FileItem

# kill logging
logging.disable(logging.CRITICAL)

#------------------------------------------------------------------------------
class TestFile(unittest.TestCase):

  #----------------------------------------------------------------------------
  def test_xml_simple(self):
    fi = FileItem(id='0', name='filename.ext', body='some text.\n')
    self.assertEqual('<File><name>filename.ext</name><body>some text.\n</body></File>', fi.dumps())

  #----------------------------------------------------------------------------
  def test_xml_attributes(self):
    fi = FileItem(id='0', name='n', hidden=True, system=False)
    self.assertEqual('<File><name>n</name><attributes><h>true</h><s>false</s></attributes></File>', fi.dumps())

  #----------------------------------------------------------------------------
  def test_xml_dates(self):
    fi = FileItem(id='0', name='n', created=1234567890)
    self.assertEqual('<File><name>n</name><created>20090213T233130Z</created></File>', fi.dumps())

#------------------------------------------------------------------------------
# end of $Id: test_file.py 21 2012-06-03 17:30:49Z griff1n $
#------------------------------------------------------------------------------
