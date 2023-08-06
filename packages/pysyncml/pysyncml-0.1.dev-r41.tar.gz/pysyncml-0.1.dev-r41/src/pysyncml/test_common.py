# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id: test_common.py 38 2012-07-21 17:38:23Z griff1n $
# lib:  pysyncml.test_common
# auth: griffin <griffin@uberdev.org>
# date: 2012/05/30
# copy: (C) CopyLoose 2012 UberDev <hardcore@uberdev.org>, No Rights Reserved.
#------------------------------------------------------------------------------

import unittest, re
from StringIO import StringIO as sio
from . import common, constants, test_helpers
from .common import adict

#------------------------------------------------------------------------------
class TestCommon(unittest.TestCase, test_helpers.MultiLineEqual):

  #----------------------------------------------------------------------------
  def test_indent(self):
    buf = sio()
    out = common.IndentStream(buf, '>>')
    out.write('hi')
    self.assertEqual('>>hi', buf.getvalue())
    out.write(', there!\nhow are you?\n')
    self.assertEqual('>>hi, there!\n>>how are you?\n', buf.getvalue())

  #----------------------------------------------------------------------------
  def test_version(self):
    # ensure that the version is always "MAJOR.MINOR.SOMETHING"
    self.assertTrue(re.match(r'^[0-9]+\.[0-9]+\.[0-9a-z.-]*$', common.versionString)
                    is not None)

  #----------------------------------------------------------------------------
  def test_describeStats(self):
    buf = sio()
    stats = dict(note=adict(
      mode=constants.SYNCTYPE_TWO_WAY,conflicts=0,
      hereAdd=10,hereMod=0,hereDel=0,hereErr=0,
      peerAdd=0,peerMod=0,peerDel=2,peerErr=0))
    common.describeStats(stats, buf)
    chk = '''
+--------+------+-----------------------+-----------------------+-----+
|        |      |         Local         |        Remote         |     |
| Source | Mode | Add | Mod | Del | Err | Add | Mod | Del | Err | Con |
+--------+------+-----+-----+-----+-----+-----+-----+-----+-----+-----+
|   note |  <>  |  10 |  -  |  -  |  -  |  -  |  -  |   2 |  -  |  -  |
+--------+------+-----+-----+-----+-----+-----+-----+-----+-----+-----+
'''.lstrip()
    self.assertMultiLineEqual(chk, buf.getvalue())

  #----------------------------------------------------------------------------
  def test_describeStats_title(self):
    buf = sio()
    stats = dict(note=adict(
      mode=constants.SYNCTYPE_TWO_WAY,conflicts=0,
      hereAdd=10,hereMod=0,hereDel=0,hereErr=0,
      peerAdd=0,peerMod=0,peerDel=2,peerErr=0))
    common.describeStats(stats, buf, title='Synchronization Summary')
    chk = '''
+---------------------------------------------------------------------+
|                       Synchronization Summary                       |
+--------+------+-----------------------+-----------------------+-----+
|        |      |         Local         |        Remote         |     |
| Source | Mode | Add | Mod | Del | Err | Add | Mod | Del | Err | Con |
+--------+------+-----+-----+-----+-----+-----+-----+-----+-----+-----+
|   note |  <>  |  10 |  -  |  -  |  -  |  -  |  -  |   2 |  -  |  -  |
+--------+------+-----+-----+-----+-----+-----+-----+-----+-----+-----+
'''.lstrip()
    self.assertMultiLineEqual(chk, buf.getvalue())

  #----------------------------------------------------------------------------
  def test_describeStats_multiwide(self):
    buf = sio()
    stats = dict(note=adict(
      mode=constants.SYNCTYPE_SLOW_SYNC,conflicts=0,
      hereAdd=1308,hereMod=0,hereDel=2,hereErr=0,
      peerAdd=0,peerMod=0,peerDel=0,peerErr=0),
                 contacts=adict(
      mode=constants.SYNCTYPE_REFRESH_FROM_SERVER,conflicts=0,
      hereAdd=0,hereMod=0,hereDel=0,hereErr=0,
      peerAdd=10387,peerMod=0,peerDel=0,peerErr=0))
    common.describeStats(stats, buf)
    chk = '''
+----------+------+-------------------------+--------------------------+-----+
|          |      |          Local          |          Remote          |     |
|   Source | Mode |  Add  | Mod | Del | Err |  Add   | Mod | Del | Err | Con |
+----------+------+-------+-----+-----+-----+--------+-----+-----+-----+-----+
| contacts |  <=  |   -   |  -  |  -  |  -  | 10,387 |  -  |  -  |  -  |  -  |
|     note |  SS  | 1,308 |  -  |   2 |  -  |   -    |  -  |  -  |  -  |  -  |
+----------+------+-------+-----+-----+-----+--------+-----+-----+-----+-----+
'''.lstrip()
    self.assertMultiLineEqual(chk, buf.getvalue())

#------------------------------------------------------------------------------
# end of $Id: test_common.py 38 2012-07-21 17:38:23Z griff1n $
#------------------------------------------------------------------------------
