# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id: common.py 38 2012-07-21 17:38:23Z griff1n $
# lib:  pysyncml.common
# auth: griffin <griffin@uberdev.org>
# date: 2012/05/19
# copy: (C) CopyLoose 2012 UberDev <hardcore@uberdev.org>, No Rights Reserved.
#------------------------------------------------------------------------------

'''
The ``pysyncml.common`` package provides some commonly used helper routines
and classes used throughout the pysyncml package.
'''

import sys, time, inspect, StringIO, pkg_resources
from elementtree import ElementTree as ET
from . import constants

#------------------------------------------------------------------------------
class SyncmlError(Exception): pass
class ProtocolError(SyncmlError): pass
class InternalError(SyncmlError): pass
class ConflictError(SyncmlError): pass
class FeatureNotSupported(SyncmlError): pass
class LogicalError(SyncmlError): pass
class InvalidContext(SyncmlError): pass
class InvalidAdapter(SyncmlError): pass
class InvalidStore(SyncmlError): pass
class InvalidContentType(SyncmlError): pass
class InvalidAgent(SyncmlError): pass
class UnknownCodec(SyncmlError): pass
class NoSuchRoute(SyncmlError): pass
class UnknownAuthType(SyncmlError): pass
class UnknownFormatType(SyncmlError): pass

#------------------------------------------------------------------------------
def ts():
  return int(time.time())

#------------------------------------------------------------------------------
def ts_iso(ts=None):
  if ts is None:
    ts = int(time.time())
  return time.strftime('%Y%m%dT%H%M%SZ', time.gmtime(ts))

#------------------------------------------------------------------------------
def state2string(state):
  return {
    constants.ITEM_OK:          'ok',
    constants.ITEM_ADDED:       'added',
    constants.ITEM_MODIFIED:    'modified',
    constants.ITEM_DELETED:     'deleted',
    constants.ITEM_SOFTDELETED: 'soft-deleted',
    }.get(state, 'UNKNOWN')

#------------------------------------------------------------------------------
def mode2string(mode):
  return {
    constants.ALERT_TWO_WAY:                           'two-way',
    constants.ALERT_SLOW_SYNC:                         'slow-sync',
    constants.ALERT_ONE_WAY_FROM_CLIENT:               'one-way-from-client',
    constants.ALERT_REFRESH_FROM_CLIENT:               'refresh-from-client',
    constants.ALERT_ONE_WAY_FROM_SERVER:               'one-way-from-server',
    constants.ALERT_REFRESH_FROM_SERVER:               'refresh-from-server',
    constants.ALERT_TWO_WAY_BY_SERVER:                 'two-way-by-server',
    constants.ALERT_ONE_WAY_FROM_CLIENT_BY_SERVER:     'one-way-from-client-by-server',
    constants.ALERT_REFRESH_FROM_CLIENT_BY_SERVER:     'refresh-from-client-by-server',
    constants.ALERT_ONE_WAY_FROM_SERVER_BY_SERVER:     'one-way-from-server-by-server',
    constants.ALERT_REFRESH_FROM_SERVER_BY_SERVER:     'refresh-from-server-by-server',
    }.get(mode, 'UNKNOWN')

#------------------------------------------------------------------------------
def auth2string(auth):
  # todo: this is really a silly implementation... it is in the end just
  #      returning the same string!... LOL.
  return {
    constants.NAMESPACE_AUTH_BASIC:                    'syncml:auth-basic',
    constants.NAMESPACE_AUTH_MD5:                      'syncml:auth-md5',
    }.get(auth, 'UNKNOWN')

#------------------------------------------------------------------------------
synctype2alert_lut = {
  constants.SYNCTYPE_TWO_WAY             : constants.ALERT_TWO_WAY,
  constants.SYNCTYPE_SLOW_SYNC           : constants.ALERT_SLOW_SYNC,
  constants.SYNCTYPE_ONE_WAY_FROM_SERVER : constants.ALERT_ONE_WAY_FROM_SERVER,
  constants.SYNCTYPE_ONE_WAY_FROM_CLIENT : constants.ALERT_ONE_WAY_FROM_CLIENT,
  constants.SYNCTYPE_REFRESH_FROM_SERVER : constants.ALERT_REFRESH_FROM_SERVER,
  constants.SYNCTYPE_REFRESH_FROM_CLIENT : constants.ALERT_REFRESH_FROM_CLIENT,
  }

#------------------------------------------------------------------------------
def synctype2alert(synctype):
  if synctype not in synctype2alert_lut:
    raise TypeError('unknown/unsupported sync type "%r"' % (synctype,))
  return synctype2alert_lut[synctype]

#------------------------------------------------------------------------------
def alert2synctype(alert):
  for s, a in synctype2alert_lut.items():
    if a == alert:
      return s
  return None

#------------------------------------------------------------------------------
class IndentStream:
  def __init__(self, stream, indent='  ', stayBlank=False):
    self.stream    = stream
    self.indent    = indent
    self.cleared   = True
    self.stayBlank = stayBlank
  def write(self, data):
    if len(data) <= 0:
      return
    lines = data.split('\n')
    if self.cleared:
      self.stream.write(self.indent)
    self.cleared = False
    for idx, line in enumerate(lines):
      if line == '':
        if idx + 1 >= len(lines):
          self.cleared = True
        else:
          # todo: maybe create an option about whether or not blank lines
          #      should include the indent?...
          if not self.stayBlank:
            self.stream.write(self.indent)
      else:
        if idx != 0 or self.cleared:
          self.stream.write(self.indent)
        self.stream.write(line)
      if idx + 1 < len(lines):
        self.stream.write('\n')

#------------------------------------------------------------------------------
class adict(dict):
  def __getattr__(self, key):
    return self.get(key, None)
  def __setattr__(self, key, value):
    self[key] = value
    return self
  def __delattr__(self, key):
    if key in self:
      del self[key]
    return self

# #------------------------------------------------------------------------------
# def dbattrs(dbobj, libobj):
#   dblist = dbobj.__table__.c.keys()
#   return [attr
#           for attr in inspect.getargspec(libobj.__init__).args
#           if attr in dblist]

#------------------------------------------------------------------------------
def getIntSize():
  '''Returns the number of bits that can be stored in an integer.'''
  count = 1
  start = sys.maxint
  while start > 0:
    count += 1
    start >>= 1
  return count

#------------------------------------------------------------------------------
# TODO: this does *NOT* seem like the /right/ way of doing this... LOL.
class _Singleton:
  @property
  def versionString(self):
    dist = pkg_resources.get_distribution('pysyncml')
    return dist.version
Singleton = _Singleton()
versionString = Singleton.versionString

#------------------------------------------------------------------------------
def num2str(num):
  # TODO: i18n...
  # TODO: this is *UGLY*
  # TODO: OMG, i'm *so* embarrassed
  # TODO: but it works... sort of.
  if num == 0:
    return '-'
  s = list(reversed(str(num)))
  for idx in reversed(range(3, len(s), 3)):
    s.insert(idx, ',')
  return ''.join(reversed(s))

#------------------------------------------------------------------------------
def describeStats(stats, stream, title=None, labels=None):
  from . import state
  modeStringLut = dict((
    (constants.SYNCTYPE_TWO_WAY,             '<>'),
    (constants.SYNCTYPE_SLOW_SYNC,           'SS'),
    (constants.SYNCTYPE_ONE_WAY_FROM_CLIENT, '->'),
    (constants.SYNCTYPE_REFRESH_FROM_CLIENT, '=>'),
    (constants.SYNCTYPE_ONE_WAY_FROM_SERVER, '<-'),
    (constants.SYNCTYPE_REFRESH_FROM_SERVER, '<='),
    ))
  # TODO: what about i18n?... maybe use "gettext()"?...
  if labels is None:
    labels = adict()
  if labels.source is None:   labels.source   = 'Source'
  if labels.mode is None:     labels.mode     = 'Mode'
  if labels.local is None:    labels.local    = 'Local'
  if labels.remote is None:   labels.remote   = 'Remote'
  if labels.states is None:   labels.states   = ['Add', 'Mod', 'Del', 'Err' ]
  if labels.conflict is None: labels.conflict = 'Con'

  # OBJECTIVE:
  # +----------------------------------------------------------------------------+
  # |                                   TITLE                                    |
  # +----------+------+-------------------------+--------------------------+-----+
  # |          |      |          Local          |          Remote          |     |
  # |   Source | Mode |  Add  | Mod | Del | Err |   Add  | Mod | Del | Err | Con |
  # +----------+------+-------+-----+-----+-----+--------+-----+-----+-----+-----+
  # | contacts |  <=  |   -   |  -  |  -  |  -  | 10,387 |  -  |  -  |  -  |  -  |
  # |     note |  SS  | 1,308 |  -  |   2 |  -  |    -   |  -  |  -  |  -  |  -  |
  # +----------+------+-------+-----+-----+-----+--------+-----+-----+-----+-----+

  wSrc  = len(labels.source)
  wMode = len(labels.mode)
  wCon  = len(labels.conflict)
  wHereAdd = wPeerAdd = len(labels.states[0])
  wHereMod = wPeerMod = len(labels.states[1])
  wHereDel = wPeerDel = len(labels.states[2])
  wHereErr = wPeerErr = len(labels.states[3])

  for key in stats.keys():
    wSrc  = max(wSrc, len(key))
    wMode = max(wMode, len(modeStringLut.get(stats[key].mode)))
    wCon  = max(wCon, len(num2str(stats[key].conflicts)))
    wHereAdd = max(wHereAdd, len(num2str(stats[key].hereAdd)))
    wPeerAdd = max(wPeerAdd, len(num2str(stats[key].peerAdd)))
    wHereMod = max(wHereMod, len(num2str(stats[key].hereMod)))
    wPeerMod = max(wPeerMod, len(num2str(stats[key].peerMod)))
    wHereDel = max(wHereDel, len(num2str(stats[key].hereDel)))
    wPeerDel = max(wPeerDel, len(num2str(stats[key].peerDel)))
    wHereErr = max(wHereErr, len(num2str(stats[key].hereErr)))
    wPeerErr = max(wPeerErr, len(num2str(stats[key].peerErr)))

  # TODO: i'm 100% sure there is a python library that can do this for me...

  if title is not None:
    tWid = ( wSrc + 3 + wMode + 3
             + wHereAdd + wHereMod + wHereDel + wHereErr + 9 + 3
             + wPeerAdd + wPeerMod + wPeerDel + wPeerErr + 9 + 3
             + wCon )
    stream.write('+-' + '-' * tWid + '-+\n')
    stream.write('| {0: ^{w}}'.format(title, w=tWid))
    stream.write(' |\n')

  hline = '+-' \
          + '-' * wSrc \
          + '-+-' \
          + '-' * wMode \
          + '-+-' \
          + '-' * ( wHereAdd + wHereMod + wHereDel + wHereErr + 9 ) \
          + '-+-' \
          + '-' * ( wPeerAdd + wPeerMod + wPeerDel + wPeerErr + 9 )  \
          + '-+-' \
          + '-' * wCon \
          + '-+\n'

  stream.write(hline)

  stream.write('| ' + ' ' * wSrc)
  stream.write(' | ' + ' ' * wMode)
  stream.write(' | {0: ^{w}}'.format(labels.local, w=( wHereAdd + wHereMod + wHereDel + wHereErr + 9 )))
  stream.write(' | {0: ^{w}}'.format(labels.remote, w=( wPeerAdd + wPeerMod + wPeerDel + wPeerErr + 9 )))
  stream.write(' | ' + ' ' * wCon)
  stream.write(' |\n')

  stream.write('| {0: >{w}}'.format(labels.source, w=wSrc))
  stream.write(' | {0: >{w}}'.format(labels.mode, w=wMode))
  stream.write(' | {0: ^{w}}'.format(labels.states[0], w=wHereAdd))
  stream.write(' | {0: ^{w}}'.format(labels.states[1], w=wHereMod))
  stream.write(' | {0: ^{w}}'.format(labels.states[2], w=wHereDel))
  stream.write(' | {0: ^{w}}'.format(labels.states[3], w=wHereErr))
  stream.write(' | {0: ^{w}}'.format(labels.states[0], w=wPeerAdd))
  stream.write(' | {0: ^{w}}'.format(labels.states[1], w=wPeerMod))
  stream.write(' | {0: ^{w}}'.format(labels.states[2], w=wPeerDel))
  stream.write(' | {0: ^{w}}'.format(labels.states[3], w=wPeerErr))
  stream.write(' | {0: ^{w}}'.format(labels.conflict, w=wCon))
  stream.write(' |\n')

  hsline = '+-' + '-' * wSrc \
           + '-+-' + '-' * wMode \
           + '-+-' + '-' * wHereAdd \
           + '-+-' + '-' * wHereMod \
           + '-+-' + '-' * wHereDel \
           + '-+-' + '-' * wHereErr \
           + '-+-' + '-' * wPeerAdd \
           + '-+-' + '-' * wPeerMod \
           + '-+-' + '-' * wPeerDel \
           + '-+-' + '-' * wPeerErr \
           + '-+-' + '-' * wCon \
           + '-+\n'

  stream.write(hsline)

  def numcol(val, wid):
    if val == 0:
      return ' | {0: ^{w}}'.format('-', w=wid)
    return ' | {0: >{w}}'.format(num2str(val), w=wid)

  for key in sorted(stats.keys(), key=lambda k: str(k).lower()):
    stream.write('| {0: >{w}}'.format(key, w=wSrc))
    stream.write(' | {0: ^{w}}'.format(modeStringLut.get(stats[key].mode), w=wMode))
    stream.write(numcol(stats[key].hereAdd, wHereAdd))
    stream.write(numcol(stats[key].hereMod, wHereMod))
    stream.write(numcol(stats[key].hereDel, wHereDel))
    stream.write(numcol(stats[key].hereErr, wHereErr))
    stream.write(numcol(stats[key].peerAdd, wPeerAdd))
    stream.write(numcol(stats[key].peerMod, wPeerMod))
    stream.write(numcol(stats[key].peerDel, wPeerDel))
    stream.write(numcol(stats[key].peerErr, wPeerErr))
    stream.write(numcol(stats[key].conflicts, wCon))
    stream.write(' |\n')

  stream.write(hsline)

  return

#------------------------------------------------------------------------------
# end of $Id: common.py 38 2012-07-21 17:38:23Z griff1n $
#------------------------------------------------------------------------------
