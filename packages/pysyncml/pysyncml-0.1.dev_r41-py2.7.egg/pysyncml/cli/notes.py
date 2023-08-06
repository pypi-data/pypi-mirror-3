#!/usr/bin/env python
# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id: notes.py 40 2012-07-22 18:53:36Z griff1n $
# lib:  pysyncml.cli.notes
# auth: griffin <griffin@uberdev.org>
# date: 2012/05/19
# copy: (C) CopyLoose 2012 UberDev <hardcore@uberdev.org>, No Rights Reserved.
#------------------------------------------------------------------------------

'''
A "note" synchronization adapter that stores notes in a
directory. Each note is stored in a separate file - although the
filename is tracked, it may be lost depending on the SyncML server
that is being contacted (if it supports content-type
"text/x-s4j-sifn", then the filename will be preserved).

This program is capable of running as either a client or as a server -
for now however, for any given note directory it is recommended to
only be used as one or the other, not both. When run in server mode,
it currently only supports a single optional authenticated username.

Brief first-time usage (see "--help" for details) as a client::

  sync-notes --remote https://example.com/funambol/ds \
             --username guest --password guest \
             NOTE_DIRECTORY

Follow-up synchronizations::

  sync-notes NOTE_DIRECTORY

Brief first-time usage as a server (listen port defaults to 80)::

  sync-notes --server --listen 8080 NOTE_DIRECTORY

Follow-up synchronizations::

  sync-notes --server NOTE_DIRECTORY

'''

#------------------------------------------------------------------------------
# IMPORTS
#------------------------------------------------------------------------------

import sys, os, re, time, uuid, hashlib, logging, getpass, pysyncml, traceback
import BaseHTTPServer, Cookie, urlparse, urllib
from optparse import OptionParser
from elementtree import ElementTree as ET
import sqlalchemy
from sqlalchemy import orm
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound

#------------------------------------------------------------------------------
# GLOBALS
#------------------------------------------------------------------------------

# create a default device ID that is fairly certain to be globally unique. for
# example, the IMEI number for a mobile phone. in this case, we are using
# uuid.getnode() which generates a hash based on the local MAC address.
# note that this is only used the first time `sync-notes` is used with a
# directory - after that, the device ID is retrieved from the sync database.
defaultDevID = 'pysyncml.cli.notes:%x:%x' % (uuid.getnode(), time.time())

# todo: is having a global dbengine and dbsession really the best way?...
dbengine  = None
dbsession = None

# setup a logger
log = logging.getLogger(__name__)

#------------------------------------------------------------------------------
class LogFormatter(logging.Formatter):
  levelString = {
    logging.DEBUG:       '[  ] DEBUG   ',
    logging.INFO:        '[--] INFO    ',
    logging.WARNING:     '[++] WARNING ',
    logging.ERROR:       '[**] ERROR   ',
    logging.CRITICAL:    '[**] CRITICAL',
    }
  def __init__(self, logsource, *args, **kw):
    logging.Formatter.__init__(self, *args, **kw)
    self.logsource = logsource
  def format(self, record):
    msg = record.getMessage()
    pfx = '%s|%s: ' % (LogFormatter.levelString[record.levelno], record.name) \
          if self.logsource else \
          '%s ' % (LogFormatter.levelString[record.levelno],)
    if msg.find('\n') < 0:
      return '%s%s' % (pfx, record.getMessage())
    return pfx + ('\n' + pfx).join(msg.split('\n'))

#------------------------------------------------------------------------------
# STORAGE MODEL
#------------------------------------------------------------------------------

# `sync-notes` uses sqlalchemy to store state information. there are two main
# ORM objects:
#   Server: when `sync-notes` is used in server-mode, this stores details
#           about what port to listen on, authentication info, default
#           conflict policy, etc.
#   Note:   tracks note state so that changes can be detected.

#------------------------------------------------------------------------------
class DatabaseObject(object):
  @declared_attr
  def __tablename__(cls):
    return cls.__name__.lower()
  id = sqlalchemy.Column(sqlalchemy.Integer, autoincrement=True, primary_key=True)
  @classmethod
  def q(cls, **kw):
    return dbsession.query(cls).filter_by(**kw)

DatabaseObject = declarative_base(cls=DatabaseObject)

#------------------------------------------------------------------------------
class Server(DatabaseObject):
  port     = sqlalchemy.Column(sqlalchemy.Integer)
  username = sqlalchemy.Column(sqlalchemy.String)
  password = sqlalchemy.Column(sqlalchemy.String)
  policy   = sqlalchemy.Column(sqlalchemy.Integer)

#------------------------------------------------------------------------------
class Note(DatabaseObject, pysyncml.NoteItem):
  # note: attributes inherited from NoteItem: id, extensions, name, body
  #       attributes then overriden by DatabaseObject (i hope): id
  #       and then attributes overriden here: name
  # note: the `deleted` attribute exists only to ensure ID's are not recycled
  #       ugh. i need a better solution to that...
  inode   = sqlalchemy.Column(sqlalchemy.Integer, index=True)
  name    = sqlalchemy.Column(sqlalchemy.String)
  sha256  = sqlalchemy.Column(sqlalchemy.String(64))
  deleted = sqlalchemy.Column(sqlalchemy.Boolean)
  @classmethod
  def q(cls, deleted=False, **kw):
    if deleted is not None:
      kw['deleted'] = deleted
    return dbsession.query(cls).filter_by(**kw)
  def __init__(self, *args, **kw):
    self.deleted = False
    DatabaseObject.__init__(self, *args, **kw)
    # TODO: check this...
    # NOTE: not calling NoteItem.__init__ as it can conflict with the
    #       sqlalchemy stuff done here...
    # todo: is this really necessary?...
    skw = dict()
    skw.update(kw)
    for key in self.__table__.c.keys():
      if key in skw:
        del skw[key]
    pysyncml.Ext.__init__(self, *args, **skw)
  @orm.reconstructor
  def __dbinit__(self):
    # note: not calling ``NoteItem.__init__`` - see ``__init__`` notes.
    pysyncml.Ext.__init__(self)
  def __str__(self):
    return 'Note "%s"' % (self.name,)
  def __repr__(self):
    return '<Note "%s": inode=%s; sha256=%s>' \
           % (self.name, '-' if self.inode is None else str(self.inode),
              self.sha256)
  def dump(self, stream, contentType, version, rootdir):
    # TODO: convert this to a .body @property...
    with open(os.path.join(rootdir, self.name), 'rb') as fp:
      self.body = fp.read()
    pysyncml.NoteItem.dump(self, stream, contentType, version)
    self.body = None
    return self
  @classmethod
  def load(cls, stream, contentType=None, version=None):
    base = pysyncml.NoteItem.load(stream, contentType, version)
    if contentType == pysyncml.TYPE_TEXT_PLAIN:
      # remove special characters, windows illegal set: \/:*?"<>|
      base.name = re.sub(r'[^a-zA-Z0-9,_+=!@#$%^&() -]+', '', base.name)
      # collapse white space and replace with '_'
      base.name = re.sub(r'\s+', '_', base.name) + '.txt'
    ret = Note(name=base.name, sha256=hashlib.sha256(base.body).hexdigest())
    # temporarily storing the content in "body" attribute (until addItem()
    # is called)
    ret.body = base.body
    return ret

#------------------------------------------------------------------------------
# STORAGE CONTROLLER
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
def hashstream(hash, stream):
  while True:
    buf = stream.read(8192)
    if len(buf) <= 0:
      break
    hash.update(buf)
  return hash

#------------------------------------------------------------------------------
class FilesystemNoteAgent(pysyncml.BaseNoteAgent):
  '''
  The `FilesystemNoteAgent` is the implementation of the `pysyncml.Agent`
  interface that provides the glue between the SyncML synchronization engine
  (i.e. the `pysyncml.Adapter`) and the local datastore. This allows the
  SyncML Adapter to be agnostic about how the items are actually stored.

  It subclasses `pysyncml.BaseNoteAgent` (instead of `pysyncml.Agent`) in
  order to take advantage of the "note"-aware functionality already provided
  by pysyncml.
  '''

  #----------------------------------------------------------------------------
  def __init__(self, root, ignoreRoot=None, ignoreAll=None,
               syncstore=None, *args, **kw):
    '''
    The `FilesystemNoteAgent` constructor accepts the following parameters:

    :param root:

      (required) the root directory that the notes are stored in.

    :param ignoreRoot:

      (optional) a regular expression string that specifies files that should
      be ignored in the root directory (but not in subdirectories). This is
      primarily useful so that synchronization state can be stored in a SQLite
      database within the note directory itself without being itself sync\'d.

    :param ignoreAll:

      (optional) similar to `ignoreRoot` except this expression is matched
      against all files, even files in sub-directories. This is primarily
      useful if you want to ignore temporary files, such as "~" emacs files
      and dot-files.

    :param syncstore:

      (optional) specifies the `pysyncml.Store` object that represents the
      SyncML datastore within the pysyncml framework. If specified, will
      automatically scan for local changes and report them to the store.
      If not specified, the caller must eventually manually call the
      :meth:`scan` methed.

    '''
    super(FilesystemNoteAgent, self).__init__(*args, **kw)
    self.rootdir    = root
    self.ignoreRoot = re.compile(ignoreRoot) if ignoreRoot is not None else None
    self.ignoreAll  = re.compile(ignoreAll) if ignoreAll is not None else None
    if syncstore is not None:
      self.scan(syncstore)
    # the pysyncml.BaseNoteAgent specifies a set of content-types that it
    # knows how to serialize/deserialize, which includes version "1.0" and
    # "1.1" of text/plain. it is fairly unclear what the difference is,
    # but it causes problems when sync'ing with funambol, because it does
    # not like the multiple "VerCT" nodes that results from it. thus overriding
    # BaseNoteAgent here for funambol compatibility.
    # TODO: perhaps the pysyncml framework can be reworked to issue multiple
    #       <Tx> or <Rx> nodes instead of multiple <VerCT> nodes?...
    self.contentTypes = [
      pysyncml.ContentTypeInfo(pysyncml.TYPE_SIF_NOTE, '1.1', True),
      pysyncml.ContentTypeInfo(pysyncml.TYPE_SIF_NOTE, '1.0'),
      # pysyncml.ContentTypeInfo(pysyncml.TYPE_TEXT_PLAIN, ['1.1', '1.0']),
      pysyncml.ContentTypeInfo(pysyncml.TYPE_TEXT_PLAIN, '1.0'),
      ]

  #----------------------------------------------------------------------------
  def scan(self, store):
    '''
    Scans the local notes for changes (either additions, modifications or
    deletions) and reports them to the `store` object, which is expected to
    implement the :class:`pysyncml.Store` interface.
    '''
    # todo: this scan assumes that the note index (not the bodies) will
    #       comfortably fit in memory... this is probably a good assumption,
    #       but ideally it would not need to depend on that.
    # `reg` is a registry of notes, along with the note's state (which can
    # be one of OK, ADDED, MODIFIED, or DELETED). the _scandir() populates
    # it with all the files currently in the root directory, and _scanindex()
    # searches for entries that are missing (i.e. the files have been removed).
    reg = dict()
    if store.peer is not None:
      # if the store is already bound to a remote peer, then we may have
      # already reported some changes (for example, if option "--local" was
      # used). therefore pre-populate the registry with any changes that we
      # have already registered.
      reg = dict((c.itemID, c.state) for c in store.peer.getRegisteredChanges())
    self._scandir('.', store, reg)
    self._scanindex(store, reg)

  #----------------------------------------------------------------------------
  def _scanindex(self, store, reg):
    # IMPORTANT: this assumes that _scandir has completed and that all
    #            moved files have been recorded, etc. this function
    #            then searches for deleted files...
    # TODO: this is somewhat of a simplistic algorithm... this
    #       comparison should be done at the same time as the dirwalk
    #       to detect more complex changes such as: files "a" and "b"
    #       are synced. then "a" is deleted and "b" is moved to "a"...
    #       the current algorithm would incorrectly record that as a
    #       non-syncing change to "b", and "a" would not be
    #       deleted. or something like that.
    for note in Note.q():
      if str(note.id) in reg:
        continue
      log.debug('locally deleted note: %s', note.name)
      note.deleted = True
      store.registerChange(note.id, pysyncml.ITEM_DELETED)
      reg[str(note.id)] = pysyncml.ITEM_DELETED

  #----------------------------------------------------------------------------
  def _scandir(self, dirname, store, reg):
    curdir = os.path.normcase(os.path.normpath(os.path.join(self.rootdir, dirname)))
    log.debug('scanning directory "%s"...', curdir)
    for name in os.listdir(curdir):
      # apply the "ignoreRoot" and "ignoreAll" regex's - this is primarily to
      # ignore the pysyncml storage file in the root directory
      if dirname == '.':
        if self.ignoreRoot is not None and self.ignoreRoot.match(name):
          continue
      if self.ignoreAll is not None and self.ignoreAll.match(name):
        continue
      path = os.path.join(curdir, name)
      if os.path.islink(path):
        # todo: should i follow?...
        continue
      if os.path.isfile(path):
        self._scanfile(path, os.path.join(dirname, name), store, reg)
        continue
      if os.path.isdir(path):
        # and recurse!...
        self._scandir(os.path.join(dirname, name), store, reg)

  #----------------------------------------------------------------------------
  def _scanfile(self, path, name, store, reg):
    log.debug('analyzing file "%s"...', path)
    inode  = os.stat(path).st_ino
    name   = os.path.normpath(name)
    note   = None
    chksum = None
    try:
      note = Note.q(name=name).one()
      log.debug('  matched item %d by name ("%s")', note.id, note.name)
    except NoResultFound:
      try:
        with open(path,'rb') as fp:
          chksum = hashstream(hashlib.sha256(), fp).hexdigest()
        note = Note.q(sha256=chksum).one()
        log.debug('  matched item %d by checksum ("%s")', note.id, note.sha256)
      except NoResultFound:
        try:
          note = Note.q(inode=inode).one()
          log.debug('  matched item %d by inode (%d)', note.id, note.inode)
          if note.name != name and note.sha256 != chksum:
            log.debug('  looks like the inode was recycled... dropping match')
            raise NoResultFound()
        except NoResultFound:
          log.debug('locally added note: %s', path)
          note = Note(inode=inode, name=name, sha256=chksum)
          dbsession.add(note)
          dbsession.flush()
          store.registerChange(note.id, pysyncml.ITEM_ADDED)
          reg[str(note.id)] = pysyncml.ITEM_ADDED
          return
    if inode != note.inode:
      log.debug('locally recreated note with new inode: %d => %d (not synchronized)', note.inode, inode)
      note.inode = inode
    if name != note.name:
      # todo: a rename should prolly trigger an update... the lowest
      #       common denominator (text/plain) does not synchronize
      #       names though...
      log.debug('locally renamed note: %s => %s (not synchronized)', note.name, name)
      note.name = name
    # TODO: i *should* store the last-modified and check that instead of
    #       opening and sha256-digesting every single file... if that gets
    #       implemented, however, there should be a "deep check" option
    #       that still checks the checksum since the last-modified can be
    #       unreliable.
    if chksum is None:
      with open(path,'rb') as fp:
        chksum = hashstream(hashlib.sha256(), fp).hexdigest()
    modified = None
    if chksum != note.sha256:
      modified = 'content'
      note.sha256 = chksum
    if modified is not None:
      log.debug('locally modified note: %s (%s)', path, modified)
      if reg.get(str(note.id)) == pysyncml.ITEM_ADDED:
        return
      store.registerChange(note.id, pysyncml.ITEM_MODIFIED)
      reg[str(note.id)] = pysyncml.ITEM_MODIFIED
    else:
      reg[str(note.id)] = pysyncml.ITEM_OK

  #----------------------------------------------------------------------------
  def getAllItems(self):
    for note in Note.q():
      yield note

  #----------------------------------------------------------------------------
  def dumpItem(self, item, stream, contentType=None, version=None):
    item.dump(stream, contentType, version, self.rootdir)

  #----------------------------------------------------------------------------
  def loadItem(self, stream, contentType=None, version=None):
    return Note.load(stream, contentType, version)

  #----------------------------------------------------------------------------
  def getItem(self, itemID, includeDeleted=False):
    if includeDeleted:
      return Note.q(id=int(itemID), deleted=None).one()
    return Note.q(id=int(itemID)).one()

  #----------------------------------------------------------------------------
  def addItem(self, item):
    path = os.path.join(self.rootdir, item.name)
    if '.' not in item.name:
      pbase = item.name
      psufx = ''
    else:
      pbase = item.name[:item.name.rindex('.')]
      psufx = item.name[item.name.rindex('.'):]
    count = 0
    while os.path.exists(path):
      count += 1
      item.name = '%s(%d)%s' % (pbase, count, psufx)
      path = os.path.join(self.rootdir, item.name)
    with open(path, 'wb') as fp:
      fp.write(item.body)
    item.inode  = os.stat(path).st_ino
    delattr(item, 'body')
    dbsession.add(item)
    dbsession.flush()
    log.debug('added: %s', item)
    return item

  #----------------------------------------------------------------------------
  def replaceItem(self, item):
    curitem = self.getItem(item.id)
    path    = os.path.join(self.rootdir, curitem.name)
    with open(path, 'wb') as fp:
      fp.write(item.body)
    curitem.inode  = os.stat(path).st_ino
    curitem.sha256 = hashlib.sha256(item.body).hexdigest()
    delattr(item, 'body')
    dbsession.flush()
    log.debug('updated: %s', curitem)

  #----------------------------------------------------------------------------
  def deleteItem(self, itemID):
    item = self.getItem(itemID)
    path = os.path.join(self.rootdir, item.name)
    if os.path.exists(path):
      os.unlink(path)
    item.deleted = True
    # note: writing log before actual delete as otherwise object is invalid
    log.debug('deleted: %s', item)
    # note: not deleting from DB to ensure ID's are not recycled... ugh. i
    #       need a better solution to that... the reason that ID's must not
    #       be recycled is that soft-deletes will delete the object locally,
    #       but it's ID must not be used with a new object as otherwise this
    #       will result in conflicts on the server-side...
    # dbsession.delete(item)

#------------------------------------------------------------------------------
# ADAPTER INTEGRATION
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
def makeAdapter(opts):
  '''
  Creates a tuple of ( Context, Adapter, Agent ) based on the options
  specified by `opts`. The Context is the pysyncml.Context created for
  the storage location specified in `opts`, the Adapter is a newly
  created Adapter if a previously created one was not found, and Agent
  is a pysyncml.Agent implementation that is setup to interface
  between Adapter and the local note storage.
  '''

  # create a new pysyncml.Context. the main function that this provides is
  # to give the Adapter a storage engine to store state information across
  # synchronizations.

  context = pysyncml.Context(storage='sqlite:///%(rootdir)s%(storageName)s' %
                             dict(rootdir=opts.rootdir, storageName=opts.storageName),
                             owner=None, autoCommit=True)

  # create an Adapter from the current context. this will either create
  # a new adapter, or load the current local adapter for the specified
  # context storage location. if it is new, then lots of required
  # information (such as device info) will not be set, so we need to
  # check that and specify it if missing.

  adapter = context.Adapter()

  if opts.name is not None:
    adapter.name = opts.name + ' (pysyncml.cli.notes SyncML Adapter)'

  # TODO: stop ignoring ``opts.remoteUri``... (the router must first support
  #       manual routes...)
  # if opts.remoteUri is not None:
  #   adapter.router.addRoute(agent.uri, opts.remoteUri)

  if adapter.devinfo is None:
    log.info('adapter has no device info - registering new device')
  else:
    if opts.devid is not None and opts.devid != adapter.devinfo.devID:
      log.info('adapter has invalid device ID - overwriting with new device info')
      adapter.devinfo = None

  if adapter.devinfo is None:
    # setup some information about the local device, most importantly the
    # device ID, which the remote peer will use to uniquely identify this peer
    adapter.devinfo = context.DeviceInfo(
      devID             = opts.devid or defaultDevID,
      devType           = pysyncml.DEVTYPE_SERVER if opts.server else pysyncml.DEVTYPE_WORKSTATION,
      softwareVersion   = '0.1',
      manufacturerName  = 'pysyncml',
      modelName         = 'pysyncml.cli.notes',
      # TODO: adding this for funambol-compatibility...
      hierarchicalSync  = False,
      )

  if not opts.server:

    # servers don't have a fixed peer; i.e. the SyncML message itself
    # defines which peer is connecting.

    if adapter.peer is None:
      if opts.remote is None:
        opts.remote = raw_input('SyncML remote URL: ')
        if opts.username is None:
          opts.username = raw_input('SyncML remote username (leave empty if none): ')
          if len(opts.username) <= 0:
            opts.username = None
      log.info('adapter has no remote info - registering new remote adapter')
    else:
      if opts.remote is not None:
        if opts.remote != adapter.peer.url \
           or opts.username != adapter.peer.username \
           or opts.password != adapter.peer.password:
          #or opts.password is not None:
          log.info('adapter has invalid or rejected remote info - overwriting with new remote info')
          adapter.peer = None

    if adapter.peer is None:
      auth = None
      if opts.username is not None:
        auth = pysyncml.NAMESPACE_AUTH_BASIC
        if opts.password is None:
          opts.password = getpass.getpass('SyncML remote password: ')
      # setup the remote connection parameters, if not already stored in
      # the adapter sync tables or the URL has changed.
      adapter.peer = context.RemoteAdapter(
        url      = opts.remote,
        auth     = auth,
        username = opts.username,
        password = opts.password,
        )

  # add a datastore attached to the URI "note". the actual value of
  # the URI is irrelevant - it is only an identifier for this item
  # synchronization channel. it must be unique within this adapter
  # and must stay consistent across synchronizations.

  # TODO: this check should be made redundant... (ie. once the
  #       implementation of Store.merge() is fixed this will
  #       become a single "addStore()" call without the check first).
  if 'note' in adapter.stores:
    store = adapter.stores['note']
  else:
    store = adapter.addStore(context.Store(
      uri         = 'note',
      displayName = opts.name,
      # TODO: adding this for funambol-compatibility...
      maxObjSize  = None))

  # create a new agent, which will scan the files stored in the root directory,
  # looking for changed files, new files, and deleted files.

  agent = FilesystemNoteAgent(opts.rootdir,
                              ignoreRoot='^(%s)$' % (re.escape(opts.syncdir),),
                              syncstore=store)

  if store.peer is None:
    if opts.local:
      print 'no pending local changes (not associated yet)'
    else:
      log.info('no pending local changes (not associated yet)')
  else:
    changes = list(store.peer.getRegisteredChanges())
    if len(changes) <= 0:
      if opts.local:
        print 'no pending local changes to synchronize'
      else:
        log.info('no pending local changes to synchronize')
    else:
      if opts.local:
        print 'pending local changes:'
      else:
        log.info('pending local changes:')
      for c in changes:
        item = agent.getItem(c.itemID, includeDeleted=True)
        msg  = '  - %s: %s' % (item, pysyncml.state2string(c.state))
        if opts.local:
          print msg
        else:
          log.info(msg)

  store.agent = agent

  return (context, adapter, agent)

#------------------------------------------------------------------------------
def main_server(opts):
  try:
    sconf = Server.q().one()
  except NoResultFound:
    log.debug('no prior server - creating new server configuration')
    sconf = Server()
    dbsession.add(sconf)

  if opts.listen is not None:
    sconf.port = opts.listen
  if sconf.port is None:
    sconf.port = 80
  if opts.username is not None:
    if opts.password is None:
      opts.password = getpass.getpass('SyncML remote password: ')
    sconf.username = opts.username
    sconf.password = opts.password
  # todo: set server policy when pysyncml supports it...

  dbsession.commit()
  sessions = dict()

  class Handler(BaseHTTPServer.BaseHTTPRequestHandler):
    def version_string(self):
      return 'pysyncml/' + pysyncml.versionString
    def _parsePathParameters(self):
      self.path_params = dict()
      pairs = [e.split('=', 1) for e in self.path.split(';')[1:]]
      for pair in pairs:
        key = urllib.unquote_plus(pair[0])
        if len(pair) < 2:
          self.path_params[key] = True
        else:
          self.path_params[key] = urllib.unquote_plus(pair[1])
    def do_POST(self):
      self._parsePathParameters()
      log.debug('handling POST request to "%s" (parameters: %r)', self.path, self.path_params)
      sid = None
      self.session = None
      if 'Cookie' in self.headers:
        cks = Cookie.SimpleCookie(self.headers["Cookie"])
        if 'sessionid' in cks:
          sid = cks['sessionid'].value
          if sid in sessions:
            self.session = sessions[sid]
            self.session.count += 1
          else:
            sid = None
      if sid is None:
        log.debug('no valid session ID found in cookies - checking path parameters')
        sid = self.path_params.get('sessionid')
        if sid in sessions:
          self.session = sessions[sid]
          self.session.count += 1
        else:
          sid = None
      if sid is None:
        while sid is None or sid in sessions:
          sid = str(uuid.uuid4())
        log.debug('request without session ID: creating new session "%s" and setting cookie', sid)
        self.session = pysyncml.adict(id=sid, count=1, syncml=pysyncml.Session())
        sessions[sid] = self.session
      log.debug('session: id=%s, count=%d', self.session.id, self.session.count)
      try:
        response = self.handleRequest()
      except Exception, e:
        self.send_response(500)
        self.end_headers()
        self.wfile.write(traceback.format_exc())
        return
      self.send_response(200)
      if self.session.count <= 1:
        cks = Cookie.SimpleCookie()
        cks['sessionid'] = sid
        self.send_header('Set-Cookie', cks.output(header=''))
      if response.contentType is not None:
        self.send_header('Content-Type', response.contentType)
      self.send_header('Content-Length', str(len(response.body)))
      self.send_header('X-PySyncML-Session', 'id=%s, count=%d' % (self.session.id, self.session.count))
      self.end_headers()
      self.wfile.write(response.body)
    def handleRequest(self):
      global dbsession
      dbsession = sessionmaker(bind=dbengine)()
      context, adapter, agent = makeAdapter(opts)
      # TODO: enforce authentication info...
      # self.assertEqual(adict(auth=pysyncml.NAMESPACE_AUTH_BASIC,
      #                        username='guest', password='guest'),
      #                  pysyncml.Context.getAuthInfo(request, None))
      clen = 0
      if 'Content-Length' in self.headers:
        clen = int(self.headers['Content-Length'])
      request = pysyncml.adict(headers=dict((('content-type', 'application/vnd.syncml+xml'),)),
                               body=self.rfile.read(clen))
      self.session.syncml.effectiveID = pysyncml.Context.getTargetID(request)
      # todo: this should be a bit more robust...
      urlparts = list(urlparse.urlsplit(self.session.syncml.effectiveID))
      if self.path_params.get('sessionid') != self.session.id:
        urlparts[2] += ';sessionid=' + self.session.id
        self.session.syncml.returnUrl = urlparse.SplitResult(*urlparts).geturl()
      response = pysyncml.Response()
      self.stats = adapter.handleRequest(self.session.syncml, request, response)
      dbsession.commit()
      return response

  server = BaseHTTPServer.HTTPServer(('', sconf.port), Handler)
  log.info('starting server on port %d', sconf.port)
  server.serve_forever()

  return 0

#------------------------------------------------------------------------------
def main_client(opts):

  context, adapter, agent = makeAdapter(opts)

  if opts.local:
    context.save()
    dbsession.commit()
    return 0

  mode = {
    'sync':      pysyncml.SYNCTYPE_TWO_WAY,
    'full':      pysyncml.SYNCTYPE_SLOW_SYNC,
    'pull':      pysyncml.SYNCTYPE_ONE_WAY_FROM_SERVER,
    'push':      pysyncml.SYNCTYPE_ONE_WAY_FROM_CLIENT,
    'pull-over': pysyncml.SYNCTYPE_REFRESH_FROM_SERVER,
    'push-over': pysyncml.SYNCTYPE_REFRESH_FROM_CLIENT,
    }[opts.mode]

  if opts.config:
    sys.stdout.write('Note SyncML adapter configuration:\n')
    adapter.describe(pysyncml.IndentStream(sys.stdout, '  '))
  else:
    stats = adapter.sync(mode=mode)
    if not opts.quiet:
      pysyncml.describeStats(stats, sys.stdout, title='Synchronization Summary')

  context.save()
  dbsession.commit()

  return 0

#------------------------------------------------------------------------------
def main():

  #----------------------------------------------------------------------------
  # setup program parameters

  cli = OptionParser(usage='%prog [options] DIRNAME',
                     version='%prog ' + pysyncml.versionString,
                     )

  cli.add_option('-v', '--verbose',
                 dest='verbose', default=0, action='count',
                 help='enable verbose output to STDERR, mostly for diagnotic'
                 ' purposes (multiple invocations increase verbosity).')

  cli.add_option('-q', '--quiet',
                 dest='quiet', default=False, action='store_true',
                 help='do not display sync summary')

  cli.add_option('-c', '--config',
                 dest='config', default=False, action='store_true',
                 help='configure the local SyncML adapter, display a summary'
                 ' and exit without actually syncronizing')

  cli.add_option('-l', '--local',
                 dest='local', default=False, action='store_true',
                 help='display the pending local changes')

  cli.add_option('-i', '--id',
                 dest='devid', default=None, action='store',
                 help='overrides the default device ID, either the store'
                 ' value from a previous sync or the generated default'
                 ' (currently "%s" - generated based on local MAC address'
                 ' and current time)'
                 % (defaultDevID,))

  cli.add_option('-n', '--name',
                 dest='name', default=None, action='store',
                 help='sets the local note adapter/store name (no default)')

  cli.add_option('-m', '--mode',
                 dest='mode', default='sync', action='store',
                 help='set the synchronization mode - can be one of "sync"'
                 ' (for two-way synchronization), "full" (for a complete'
                 ' re-synchronization), "pull" (for fetching remote'
                 ' changes only), "push" (for pushing local changes only),'
                 ' or "pull-over" (to obliterate the local data and'
                 ' download the remote data) or "push-over" (to obliterate'
                 ' the remote data and upload the local data); the default'
                 ' is "%default".')

  cli.add_option('-r', '--remote',
                 dest='remote', default=None, action='store',
                 help='specifies the remote URL of the SyncML synchronization'
                 ' server - only required if the target ``DIRNAME`` has never'
                 ' been synchronized, or the synchronization meta information'
                 ' was lost.')

  cli.add_option('-R', '--remote-uri',
                 dest='remoteUri', default=None, action='store',
                 help='specifies the remote URI of the note datastore. if'
                 ' left unspecified, pysyncml will attempt to identify it'
                 ' automatically.')

  cli.add_option('-s', '--server',
                 dest='server', default=False, action='store_true',
                 help='enables HTTP server mode')

  cli.add_option('-L', '--listen',
                 dest='listen', default=None, action='store', type='int',
                 help='specifies the port to listen on for server mode'
                 ' (implies --server and defaults to port 80)')

  # todo: add a "policy" to configure how the server mode should handle
  #       conflicts...

  cli.add_option('-u', '--username',
                 dest='username', default=None, action='store',
                 help='specifies the remote server username to log in with'
                 ' (in client mode) or to require authorization for (in'
                 ' server mode)')

  cli.add_option('-p', '--password',
                 dest='password', default=None, action='store',
                 help='specifies the remote server password to log in with'
                 ' in client mode (if "--remote" and "--username" is'
                 ' specified, but not "--password", the password will be'
                 ' prompted for to avoid leaking the password into the'
                 ' local hosts environment, which is the recommended'
                 ' approach). in server mode, specifies the password for'
                 ' the required username (a present "--username" and missing'
                 ' "--password" is handled the same way as in client'
                 ' mode)')

  (opts, args) = cli.parse_args()

  if len(args) != 1:
    cli.error('expected exactly one argument DIRNAME - please see "--help" for details.')

  # setup logging (based on requested verbosity)
  rootlog = logging.getLogger()
  handler = logging.StreamHandler(sys.stderr)
  handler.setFormatter(LogFormatter(opts.verbose >= 2))
  rootlog.addHandler(handler)
  if opts.verbose >= 3:   rootlog.setLevel(logging.DEBUG)
  elif opts.verbose == 2: rootlog.setLevel(logging.INFO)
  elif opts.verbose == 1: rootlog.setLevel(logging.INFO)
  else:                   rootlog.setLevel(logging.FATAL)

  # setup storage locations for note tracking and pysyncml internal data
  opts.syncdir      = '.sync'
  opts.storageName  = os.path.join(opts.syncdir, 'syncml.db')
  opts.indexStorage = os.path.join(opts.syncdir, 'index.db')
  opts.rootdir      = args[0]
  if not opts.rootdir.startswith('/') and not opts.rootdir.startswith('.'):
    opts.rootdir = './' + opts.rootdir
  if not opts.rootdir.endswith('/'):
    opts.rootdir += '/'

  if not os.path.isdir(opts.rootdir):
    cli.error('note root directory "%s" does not exist' % (opts.rootdir,))

  if not os.path.isdir(os.path.join(opts.rootdir, opts.syncdir)):
    os.makedirs(os.path.join(opts.rootdir, opts.syncdir))

  #----------------------------------------------------------------------------
  # prepare storage

  global dbengine, dbsession
  dbengine  = sqlalchemy.create_engine('sqlite:///%s%s' % (opts.rootdir, opts.indexStorage))
  dbsession = sessionmaker(bind=dbengine)()
  # TODO: how to detect if my schema has changed?...
  if not os.path.isfile('%s%s' % (opts.rootdir, opts.indexStorage)):
    DatabaseObject.metadata.create_all(dbengine)

  if opts.server or opts.listen is not None:
    opts.server = True
    return main_server(opts)

  return main_client(opts)

#------------------------------------------------------------------------------
if __name__ == '__main__':
  sys.exit(main())

#------------------------------------------------------------------------------
# end of $Id: notes.py 40 2012-07-22 18:53:36Z griff1n $
#------------------------------------------------------------------------------
