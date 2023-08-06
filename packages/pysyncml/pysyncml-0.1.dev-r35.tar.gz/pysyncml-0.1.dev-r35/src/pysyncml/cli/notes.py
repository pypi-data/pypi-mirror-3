#!/usr/bin/env python
# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id: notes.py 34 2012-07-03 02:48:00Z griff1n $
# lib:  pysyncml.cli.notes
# auth: griffin <griffin@uberdev.org>
# date: 2012/05/19
# copy: (C) CopyLoose 2012 UberDev <hardcore@uberdev.org>, No Rights Reserved.
#------------------------------------------------------------------------------

import sys, os, re, time, uuid, hashlib, logging, getpass, pysyncml
from optparse import OptionParser
from elementtree import ElementTree as ET
import sqlalchemy
from sqlalchemy import orm
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound

log = logging.getLogger(__name__)

#------------------------------------------------------------------------------
class DatabaseObject(object):
  # todo: is having a "global" Note._db really the best way?...
  _db    = None
  @declared_attr
  def __tablename__(cls):
    return cls.__name__.lower()
  id = sqlalchemy.Column(sqlalchemy.Integer, autoincrement=True, primary_key=True)

DatabaseObject = declarative_base(cls=DatabaseObject)

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
    if deleted is None:
      return DatabaseObject._db.query(cls).filter_by(**kw)
    return DatabaseObject._db.query(cls).filter_by(deleted=deleted, **kw)
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
def hashstream(hash, stream):
  while True:
    buf = stream.read(8192)
    if len(buf) <= 0:
      break
    hash.update(buf)
  return hash

#------------------------------------------------------------------------------
class FilesystemNoteAgent(pysyncml.BaseNoteAgent):

  #----------------------------------------------------------------------------
  def __init__(self, root, index, options, ignoreRoot=None, ignoreAll=None,
               syncstore=None, *args, **kw):
    super(FilesystemNoteAgent, self).__init__(*args, **kw)
    self.rootdir    = root
    self.index      = index
    self.options    = options
    self.ignoreRoot = re.compile(ignoreRoot) if ignoreRoot is not None else None
    self.ignoreAll  = re.compile(ignoreAll) if ignoreAll is not None else None
    self.dbengine   = sqlalchemy.create_engine('sqlite:///%s%s' % (root, index))
    self.db         = sessionmaker(bind=self.dbengine)()
    # TODO: how to detect if my schema has changed?...
    if not os.path.isfile('%s%s' % (root, index)):
      DatabaseObject.metadata.create_all(self.dbengine)
    # todo: is having a global really the best way?...
    DatabaseObject._db = self.db
    if syncstore is not None:
      self.scan(syncstore)

    # TODO: adding this for funambol-compatibility (to remove multiple "VerCT" nodes)...
    self.contentTypes = [
      pysyncml.ContentTypeInfo(pysyncml.TYPE_SIF_NOTE, '1.1', True),
      pysyncml.ContentTypeInfo(pysyncml.TYPE_SIF_NOTE, '1.0'),
      # pysyncml.ContentTypeInfo(pysyncml.TYPE_TEXT_PLAIN, ['1.1', '1.0']),
      pysyncml.ContentTypeInfo(pysyncml.TYPE_TEXT_PLAIN, '1.0'),
      ]

  #----------------------------------------------------------------------------
  def scan(self, store):
    # todo: this scan assumes that the note index (not the bodies) will
    #       comfortably fit in memory... this is probably a good assumption,
    #       but ideally it would not need to depend on that.
    reg = dict()
    if store.peer is not None:
      reg = dict((c.itemID, c.state) for c in store.peer.getRegisteredChanges())
    self._scandir('.', store, reg)
    self._scanindex(store, reg)

  #----------------------------------------------------------------------------
  def _scanindex(self, store, reg):
    # IMPORTANT: this assumes that _scandir has completed and that all moved
    #            files have been recorded, etc. this function then searches
    #            for deleted files...
    # TODO: this is somewhat of a simplistic algorithm... this comparison
    #       should be done at the same time as the dirwalk to detect more
    #       complex changes such as: files "a" and "b" are synced. then
    #       "a" is deleted and "b" is moved to "a"...
    #       the current algorithm would incorrectly record that as a non-syncing
    #       change to "b", and "a" would not be deleted.
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
          self.db.add(note)
          self.db.flush()
          store.registerChange(note.id, pysyncml.ITEM_ADDED)
          reg[str(note.id)] = pysyncml.ITEM_ADDED
          return
    if inode != note.inode:
      log.debug('locally recreated note with new inode: %d => %d (not synchronized)', note.inode, inode)
      note.inode = inode
    if name != note.name:
      # todo: a rename should prolly trigger an update...
      log.debug('locally renamed note: %s => %s (not synchronized)', note.name, name)
      note.name = name
    # TODO: i *should* store the last-modified and check that instead of
    #       opening and sha256-digesting every single file...
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
  def save(self):
    self.db.commit()

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
    self.db.add(item)
    self.db.flush()
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
    self.db.flush()
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
    #       need a better solution to that...
    # self.db.delete(item)

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
def main():

  #----------------------------------------------------------------------------
  # setup program parameters

  defaultDevID = 'pysyncml.cli.notes:%x:%x' % (uuid.getnode(), time.time())

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

  cli.add_option('-u', '--username',
                 dest='username', default=None, action='store',
                 help='specifies the remote server username to log in with.')

  cli.add_option('-p', '--password',
                 dest='password', default=None, action='store',
                 help='specifies the remote server password to log in with'
                 ' (if "--remote" and "--username" is specified, but not,'
                 ' "--password", the password will be prompted for to avoid'
                 ' leaking the password into the local hosts environment,'
                 ' which is the recommended approach).')

  (opts, args) = cli.parse_args()

  if len(args) != 1:
    cli.error('expected exactly one argument DIRNAME - please see "--help" for details.')

  rootlog = logging.getLogger()
  handler = logging.StreamHandler(sys.stderr)
  handler.setFormatter(LogFormatter(opts.verbose >= 2))
  rootlog.addHandler(handler)
  if opts.verbose >= 3:   rootlog.setLevel(logging.DEBUG)
  elif opts.verbose == 2: rootlog.setLevel(logging.INFO)
  elif opts.verbose == 1: rootlog.setLevel(logging.INFO)
  else:                   rootlog.setLevel(logging.FATAL)

  syncdir      = '.sync'
  storageName  = os.path.join(syncdir, 'syncml.db')
  indexStorage = os.path.join(syncdir, 'index.db')
  # rootdir      = os.path.abspath(args[0])
  rootdir      = args[0]
  if not rootdir.startswith('/') and not rootdir.startswith('.'):
    rootdir = './' + rootdir
  if not rootdir.endswith('/'):
    rootdir += '/'

  if not os.path.isdir(rootdir):
    cli.error('note root directory "%s" does not exist' % (rootdir,))

  if not os.path.isdir(os.path.join(rootdir, syncdir)):
    os.makedirs(os.path.join(rootdir, syncdir))

  #----------------------------------------------------------------------------
  # setup the pysyncml adapter

  context = pysyncml.Context(storage='sqlite:///%(rootdir)s%(storageName)s' %
                             dict(rootdir=rootdir, storageName=storageName))

  adapter = context.Adapter()

  if opts.name is not None:
    adapter.name = opts.name + ' (pysyncml.cli.notes SyncML Adapter)'

  # # TODO: stop ignoring ``opts.remoteUri``...
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
    # device ID, which the server will use to uniquely identify this client.
    adapter.devinfo = context.DeviceInfo(
      devID             = opts.devid or defaultDevID,
      devType           = pysyncml.DEVTYPE_WORKSTATION,
      softwareVersion   = '0.1',
      manufacturerName  = 'pysyncml',
      modelName         = 'pysyncml.cli.notes',
      # TODO: adding this for funambol-compatibility...
      hierarchicalSync  = False,
      )

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

  # TODO: this check should be made redundant... (ie. once the
  #       implementation of Store.merge() is fixed this will go away)
  if 'note' in adapter.stores:
    store = adapter.stores['note']
  else:
    store = adapter.addStore(context.Store(
      uri         = 'note',
      displayName = opts.name,
      # TODO: adding this for funambol-compatibility...
      maxObjSize  = None))

  #----------------------------------------------------------------------------
  # create a new agent, which will scan the files stored in the root directory,
  # looking for changed files, new files, and deleted files.

  agent = FilesystemNoteAgent(rootdir, indexStorage, opts,
                              ignoreRoot='^(%s)$' % (re.escape(syncdir),),
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

  if opts.local:
    context.save()
    agent.save()
    return 0

  store.agent = agent

  #----------------------------------------------------------------------------
  # do the synchronization

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

  #----------------------------------------------------------------------------
  # and cleanup

  context.save()
  agent.save()
  return 0

#------------------------------------------------------------------------------
if __name__ == '__main__':
  sys.exit(main())

#------------------------------------------------------------------------------
# end of $Id: notes.py 34 2012-07-03 02:48:00Z griff1n $
#------------------------------------------------------------------------------
