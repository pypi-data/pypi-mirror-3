# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id: test_helpers.py 26 2012-06-24 18:19:40Z griff1n $
# lib:  pysyncml.test_helpers
# auth: griffin <griffin@uberdev.org>
# date: 2012/06/16
# copy: (C) CopyLoose 2012 UberDev <hardcore@uberdev.org>, No Rights Reserved.
#------------------------------------------------------------------------------

import unittest, sys, re, types, difflib, xml.dom, xml.dom.minidom

#------------------------------------------------------------------------------
class MultiLineEqual:

  #----------------------------------------------------------------------------
  def assertMultiLineEqual(self, chk, tgt, msg=None):
    try:
      self.assertEqual(chk, tgt)
      return
    except Exception:
      if not type(chk) in types.StringTypes \
         or not type(tgt) in types.StringTypes:
        raise
    print '%s, diff:' % (msg or 'FAIL',)
    print '--- expected'
    print '+++ received'
    differ = difflib.Differ()
    diff = list(differ.compare(chk.split('\n'), tgt.split('\n')))
    cdiff = []
    need = -1
    for idx, line in enumerate(diff):
      if line[0] != ' ':
        need = idx + 2
      if idx > need \
         and line[0] == ' ' \
         and ( len(diff) <= idx + 1 or diff[idx + 1][0] == ' ' ) \
         and ( len(diff) <= idx + 2 or diff[idx + 2][0] == ' ' ):
        continue
      if idx > need:
        cdiff.append('@@ %d @@' % (idx + 1,))
        need = idx + 2
      # if line.startswith('?'):
      #   cdiff.append(line.strip())
      # else:
      #   cdiff.append(line)
      cdiff.append(line.rstrip())
    for line in cdiff:
      print line
    self.assertEqual('expected', 'received')

#------------------------------------------------------------------------------
def removeIgnorableWhitespace(node):
  rem = []
  for n in node.childNodes:
    if n.nodeType == xml.dom.Node.ELEMENT_NODE:
      removeIgnorableWhitespace(n)
    if n.nodeType != xml.dom.Node.TEXT_NODE:
      continue
    if re.match('^\s*$', n.nodeValue):
      rem.append(n)
  for n in rem:
    node.removeChild(n)

#------------------------------------------------------------------------------
def canonicalXml(data):
  try:
    ret = xml.dom.minidom.parseString(data)
    removeIgnorableWhitespace(ret)
    return ret.toxml(encoding='utf-8').encode('utf-8')
  except Exception:
    # most likely, the input was not valid XML...
    return data

#------------------------------------------------------------------------------
class XmlEqual(MultiLineEqual):

  #----------------------------------------------------------------------------
  def assertEqualXml(self, expected, received, msg=None, tryCanonical=True):
    try:
      self.assertEqual(chk, tgt)
      return
    except Exception:
      if tryCanonical:
        return self.assertEqualXml(canonicalXml(expected), canonicalXml(received),
                                   msg, False)
      def n(s):
        return s.replace('><', '>\n<').replace('>$', '>\n$').replace(')<', ')\n<')
      self.maxDiff = None
      self.assertMultiLineEqual(n(str(expected)), n(str(received)), msg)

#------------------------------------------------------------------------------
# end of $Id: test_helpers.py 26 2012-06-24 18:19:40Z griff1n $
#------------------------------------------------------------------------------
