# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id: test_note.py 34 2012-07-03 02:48:00Z griff1n $
# lib:  pysyncml.agents.test_note
# auth: griffin <griffin@uberdev.org>
# date: 2012/06/03
# copy: (C) CopyLoose 2012 UberDev <hardcore@uberdev.org>, No Rights Reserved.
#------------------------------------------------------------------------------

import unittest, sys, logging, StringIO
import sqlalchemy
import pysyncml
from .note import BaseNoteAgent
from ..items.note import NoteItem
from .. import state
from ..common import adict

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------

# kill logging
logging.disable(logging.CRITICAL)

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------

# class LogFormatter(logging.Formatter):
#   levelString = {
#     logging.DEBUG:       '[  ] DEBUG   ',
#     logging.INFO:        '[--] INFO    ',
#     logging.WARNING:     '[++] WARNING ',
#     logging.ERROR:       '[**] ERROR   ',
#     logging.CRITICAL:    '[**] CRITICAL',
#     }
#   def __init__(self, logsource, *args, **kw):
#     logging.Formatter.__init__(self, *args, **kw)
#     self.logsource = logsource
#   def format(self, record):
#     msg = record.getMessage()
#     pfx = '%s|%s: ' % (LogFormatter.levelString[record.levelno], record.name) \
#           if self.logsource else \
#           '%s ' % (LogFormatter.levelString[record.levelno],)
#     if msg.find('\n') < 0:
#       return '%s%s' % (pfx, record.getMessage())
#     return pfx + ('\n' + pfx).join(msg.split('\n'))
# rootlog = logging.getLogger()
# handler = logging.StreamHandler(sys.stderr)
# handler.setFormatter(LogFormatter(True))
# rootlog.addHandler(handler)
# rootlog.setLevel(logging.DEBUG)

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
class ItemStorage:
  def __init__(self, nextID=1):
    self.nextID  = nextID
    self.entries = dict()
  def getAll(self):
    return self.entries.values()
  def add(self, item):
    item.id = self.nextID
    self.nextID += 1
    self.entries[item.id] = item
    return item
  def get(self, itemID):
    return self.entries[int(itemID)]
  def replace(self, item):
    self.entries[int(item.id)] = item
    return item
  def delete(self, itemID):
    del self.entries[int(itemID)]

#------------------------------------------------------------------------------
class Agent(BaseNoteAgent):
  def __init__(self, storage=None, *args, **kw):
    super(Agent, self).__init__(*args, **kw)
    self.storage = storage or ItemStorage()
  def getAllItems(self):           return self.storage.getAll()
  def addItem(self, item):         return self.storage.add(item)
  def getItem(self, itemID):       return self.storage.get(itemID)
  def replaceItem(self, item):     return self.storage.replace(item)
  def deleteItem(self, itemID):    return self.storage.delete(itemID)

#------------------------------------------------------------------------------
class BridgingOpener(object):

  #----------------------------------------------------------------------------
  def __init__(self, adapter=None, peer=None, returnUrl=None, refresher=None):
    self.peer = peer
    self.refresher = refresher
    if self.refresher is None:
      self.refresher = lambda peer: peer
    self.session = pysyncml.Session()
    if returnUrl is not None:
      self.session.returnUrl = returnUrl

  #----------------------------------------------------------------------------
  def open(self, req, data=None, timeout=None):
    self.peer = self.refresher(self.peer)
    self.log('request', data)
    request = adict(headers=dict(), body=data)
    request.headers['content-type'] = req.headers['Content-type']
    response = state.Request()
    self.peer.handleRequest(self.session, request, response)
    self.log('response', response.body)
    res = StringIO.StringIO(response.body)
    res.info = lambda: adict(headers=['content-type: %s' % (response.contentType,)])
    return res

  #----------------------------------------------------------------------------
  def log(self, iline, content):
    try:
      import utools.pxml
      from utools.common import Font
      with open('../' + __name__ + '.log', 'ab') as fp:
        if iline == 'request':
          color = Font.get(Font.Style.BRIGHT, Font.Fg.RED, Font.Bg.BLACK)
          symbol = '>'
        else:
          color = Font.get(Font.Style.BRIGHT, Font.Fg.GREEN, Font.Bg.BLACK)
          symbol = '<'
        fp.write('%s%s %s:%s %s%s\n'
                 % (color, symbol * 5, iline.upper(), self.peer.devID,
                    symbol * 5, Font.reset()))
        fp.write(utools.pxml.prettyXml(content, strict=False, color=True) or content)
    except Exception:
      return

#------------------------------------------------------------------------------
class TestNoteAgent(unittest.TestCase):

  #----------------------------------------------------------------------------
  def setUp(self):
    # create the databases
    self.serverSyncDb  = sqlalchemy.create_engine('sqlite://')
    self.desktopSyncDb = sqlalchemy.create_engine('sqlite://')
    self.mobileSyncDb  = sqlalchemy.create_engine('sqlite://')
    pysyncml.enableSqliteCascadingDeletes(self.serverSyncDb)
    pysyncml.enableSqliteCascadingDeletes(self.desktopSyncDb)
    pysyncml.enableSqliteCascadingDeletes(self.mobileSyncDb)
    self.serverItems   = ItemStorage(nextID=1000)
    self.desktopItems  = ItemStorage(nextID=2000)
    self.mobileItems   = ItemStorage(nextID=3000)
    self.server        = None
    self.desktop       = None
    self.mobile        = None
    self.resetAdapters()

  #----------------------------------------------------------------------------
  def refreshServer(self, current=None):
    self.serverContext = pysyncml.Context(engine=self.serverSyncDb, owner=None, autoCommit=True)
    self.server = self.serverContext.Adapter()
    if self.server.name is None:
      self.server.name = 'In-Memory Test Server'
    if self.server.devinfo is None:
      self.server.devinfo = self.serverContext.DeviceInfo(
        devID             = 'http://www.example.com/sync',
        devType           = pysyncml.DEVTYPE_SERVER,
        manufacturerName  = 'pysyncml',
        modelName         = __name__ + '.server',
        )
    self.serverStore = self.server.addStore(self.serverContext.Store(
      uri='snote', displayName='Note Storage',
      agent=Agent(storage=self.serverItems)))
    return self.server

  #----------------------------------------------------------------------------
  def resetAdapters(self):
    self.server = self.refreshServer()
    #--------------------------------------------------------------------------
    # a "desktop" client
    self.desktopContext = pysyncml.Context(engine=self.desktopSyncDb, owner=None, autoCommit=True)
    self.desktop = self.desktopContext.Adapter()
    if self.desktop.name is None:
      self.desktop.name = 'In-Memory Test Desktop Client'
    if self.desktop.devinfo is None:
      self.desktop.devinfo = self.desktopContext.DeviceInfo(
        devID             = __name__ + '.desktop',
        devType           = pysyncml.DEVTYPE_WORKSTATION,
        manufacturerName  = 'pysyncml',
        modelName         = __name__ + '.desktop',
        )
    if self.desktop.peer is None:
      self.desktop.peer = self.desktopContext.RemoteAdapter(
        url='http://www.example.com/sync',
        auth=pysyncml.NAMESPACE_AUTH_BASIC, username='guest', password='guest')
    self.desktop.peer._opener = BridgingOpener(
      returnUrl='http://example.com/sync?s=123-DESKTOP',
      refresher=self.refreshServer,
      )
    self.desktopStore = self.desktop.addStore(self.desktopContext.Store(
      uri='dnote', displayName='Desktop Note Client',
      agent=Agent(storage=self.desktopItems)))
    #--------------------------------------------------------------------------
    # a "mobile" client
    self.mobileContext = pysyncml.Context(engine=self.mobileSyncDb, owner=None, autoCommit=True)
    self.mobile = self.mobileContext.Adapter(maxMsgSize=40960, maxObjSize=40960)
    if self.mobile.name is None:
      self.mobile.name = 'In-Memory Test Mobile Client'
    if self.mobile.devinfo is None:
      self.mobile.devinfo = self.mobileContext.DeviceInfo(
        devID             = __name__ + '.mobile',
        devType           = pysyncml.DEVTYPE_WORKSTATION,
        manufacturerName  = 'pysyncml',
        modelName         = __name__ + '.mobile',
        )
    if self.mobile.peer is None:
      self.mobile.peer = self.mobileContext.RemoteAdapter(
        url='http://www.example.com/sync',
        auth=pysyncml.NAMESPACE_AUTH_BASIC, username='guest', password='guest')
    self.mobile.peer._opener = BridgingOpener(
      returnUrl='http://example.com/sync?s=ABC-MOBILE',
      refresher=self.refreshServer,
      )
    self.mobileStore = self.mobile.addStore(self.mobileContext.Store(
      uri='mnote', displayName='Mobile Note Client',
      agent=Agent(storage=self.mobileItems)))

  #----------------------------------------------------------------------------
  def refreshAdapters(self):
    # this should be unnecessary - but paranoia is paranoia
    if self.serverContext is not None:
      self.serverContext.save()
    if self.desktopContext is not None:
      self.desktopContext.save()
    if self.mobileContext is not None:
      self.mobileContext.save()
    self.resetAdapters()

  #----------------------------------------------------------------------------
  def test_sync_refreshClient(self):
    self.serverItems.add(NoteItem(name='note1', body='note1'))
    self.desktopItems.add(NoteItem(name='note2', body='note2'))
    stats = self.desktop.sync(mode=pysyncml.SYNCTYPE_REFRESH_FROM_SERVER)
    self.assertEqual(['note1'], [e.body for e in self.serverItems.entries.values()])
    self.assertEqual(['note1'], [e.body for e in self.desktopItems.entries.values()])
    chk = dict(dnote=dict(mode=pysyncml.SYNCTYPE_REFRESH_FROM_SERVER, conflicts=0,
                          hereAdd=1, hereMod=0, hereDel=1, hereErr=0,
                          peerAdd=0, peerMod=0, peerDel=0, peerErr=0))
    self.assertEqual(chk, stats)

  #----------------------------------------------------------------------------
  def test_sync_addClient(self):
    # step 1: initial sync
    self.serverItems.add(NoteItem(name='note1', body='note1'))
    stats = self.desktop.sync(mode=pysyncml.SYNCTYPE_REFRESH_FROM_SERVER)
    chk = dict(dnote=dict(mode=pysyncml.SYNCTYPE_REFRESH_FROM_SERVER, conflicts=0,
                          hereAdd=1, hereMod=0, hereDel=0, hereErr=0,
                          peerAdd=0, peerMod=0, peerDel=0, peerErr=0))
    self.assertEqual(chk, stats)
    # step 2: make changes and register
    self.refreshAdapters()
    item2 = self.serverItems.add(NoteItem(name='note2', body='note2'))
    self.serverStore.registerChange(item2.id, pysyncml.ITEM_ADDED)
    # step 3: re-sync
    # TODO: look into why this "refreshAdapters()" is necessary...
    self.refreshAdapters()
    stats = self.desktop.sync(mode=pysyncml.SYNCTYPE_ONE_WAY_FROM_SERVER)
    self.assertEqual(['note1', 'note2'], [e.body for e in self.serverItems.entries.values()])
    self.assertEqual(['note1', 'note2'], [e.body for e in self.desktopItems.entries.values()])
    chk = dict(dnote=dict(mode=pysyncml.SYNCTYPE_ONE_WAY_FROM_SERVER, conflicts=0,
                          hereAdd=1, hereMod=0, hereDel=0, hereErr=0,
                          peerAdd=0, peerMod=0, peerDel=0, peerErr=0))
    self.assertEqual(chk, stats)

  #----------------------------------------------------------------------------
  def test_sync_modClient(self):
    # step 1: initial sync
    item = self.serverItems.add(NoteItem(name='note1', body='note1'))
    stats = self.desktop.sync(mode=pysyncml.SYNCTYPE_REFRESH_FROM_SERVER)
    self.assertEqual(['note1'], [e.body for e in self.serverItems.entries.values()])
    self.assertEqual(['note1'], [e.body for e in self.desktopItems.entries.values()])
    chk = dict(dnote=dict(mode=pysyncml.SYNCTYPE_REFRESH_FROM_SERVER, conflicts=0,
                          hereAdd=1, hereMod=0, hereDel=0, hereErr=0,
                          peerAdd=0, peerMod=0, peerDel=0, peerErr=0))
    self.assertEqual(chk, stats)
    # step 2: make changes and register
    self.refreshAdapters()
    self.serverItems.replace(NoteItem(name='note1.mod', body='note1.mod', id=item.id))
    self.serverStore.registerChange(item.id, pysyncml.ITEM_MODIFIED)
    # step 3: re-sync
    self.refreshAdapters()
    stats = self.desktop.sync(mode=pysyncml.SYNCTYPE_ONE_WAY_FROM_SERVER)
    self.assertEqual(['note1.mod'], [e.body for e in self.serverItems.entries.values()])
    self.assertEqual(['note1.mod'], [e.body for e in self.desktopItems.entries.values()])
    chk = dict(dnote=dict(mode=pysyncml.SYNCTYPE_ONE_WAY_FROM_SERVER, conflicts=0,
                          hereAdd=0, hereMod=1, hereDel=0, hereErr=0,
                          peerAdd=0, peerMod=0, peerDel=0, peerErr=0))
    self.assertEqual(chk, stats)

  #----------------------------------------------------------------------------
  def test_sync_delClient(self):
    # step 1: initial sync
    item = self.serverItems.add(NoteItem(name='note1', body='note1'))
    stats = self.desktop.sync(mode=pysyncml.SYNCTYPE_REFRESH_FROM_SERVER)
    self.assertEqual(['note1'], [e.body for e in self.serverItems.entries.values()])
    self.assertEqual(['note1'], [e.body for e in self.desktopItems.entries.values()])
    chk = dict(dnote=dict(mode=pysyncml.SYNCTYPE_REFRESH_FROM_SERVER, conflicts=0,
                          hereAdd=1, hereMod=0, hereDel=0, hereErr=0,
                          peerAdd=0, peerMod=0, peerDel=0, peerErr=0))
    self.assertEqual(chk, stats)
    # step 2: make changes and register
    self.refreshAdapters()
    self.serverItems.delete(item.id)
    self.serverStore.registerChange(item.id, pysyncml.ITEM_DELETED)
    # step 3: re-sync
    self.refreshAdapters()
    stats = self.desktop.sync(mode=pysyncml.SYNCTYPE_ONE_WAY_FROM_SERVER)
    self.assertEqual([], [e.body for e in self.serverItems.entries.values()])
    self.assertEqual([], [e.body for e in self.desktopItems.entries.values()])
    chk = dict(dnote=dict(mode=pysyncml.SYNCTYPE_ONE_WAY_FROM_SERVER, conflicts=0,
                          hereAdd=0, hereMod=0, hereDel=1, hereErr=0,
                          peerAdd=0, peerMod=0, peerDel=0, peerErr=0))
    self.assertEqual(chk, stats)

  #----------------------------------------------------------------------------
  def test_sync_refreshServer(self):
    # step 1: initial sync
    self.desktopItems.add(NoteItem(name='note1', body='note1'))
    stats = self.desktop.sync(mode=pysyncml.SYNCTYPE_REFRESH_FROM_CLIENT)
    self.assertEqual(['note1'], [e.body for e in self.serverItems.entries.values()])
    self.assertEqual(['note1'], [e.body for e in self.desktopItems.entries.values()])
    chk = dict(dnote=dict(mode=pysyncml.SYNCTYPE_REFRESH_FROM_CLIENT, conflicts=0,
                          hereAdd=0, hereMod=0, hereDel=0, hereErr=0,
                          peerAdd=1, peerMod=0, peerDel=0, peerErr=0))
    self.assertEqual(chk, stats)

#------------------------------------------------------------------------------
# end of $Id: test_note.py 34 2012-07-03 02:48:00Z griff1n $
#------------------------------------------------------------------------------
