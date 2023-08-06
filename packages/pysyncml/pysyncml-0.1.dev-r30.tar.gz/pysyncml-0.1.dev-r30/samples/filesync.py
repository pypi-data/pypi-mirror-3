# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id: filesync.py 20 2012-06-03 04:14:27Z griff1n $
# auth: griffin <griffin@uberdev.org>
# date: 2012/05/13
# copy: (C) CopyLoose 2012 UberDev <hardcore@uberdev.org>, No Rights Reserved.
#------------------------------------------------------------------------------

'''
A sample file synchronization client that uses the local inode number
as the file\'s LUID (local unique ID). Usage::

  filesync.py { sync | pull | push | pull-over | push-over } ROOT_DIR [ REMOTE_URL ]

The sample program executes the following steps (logically, this is a
bottom-up approach to setting up the components):

* Load the entire directory structure into memory (this is for simplicity
  only - in production systems a more efficient approach is imperative).

* Create a SyncML agent that can manipulate the filesystem as necessary for
  SyncML integration.

* Create a SyncML adapter that communicates with the remote SyncML server.

* Provide SyncML device information if not already stored previously by
  the client adapter.

* Launch a synchronization according to the mode defined on the command line.

'''

import sys, os, logging, uuid, mimetypes, hashlib, pysyncml

mode    = sys.argv[1]
rootdir = sys.argv[2]
remote  = sys.argv[3] if len(sys.argv) >= 4 else None

# resolve the rootdir to an absolute path
rootdir = os.path.abspath(rootdir)
if not rootdir.endswith('/'):
  rootdir += '/'

# configure verbose logging
log = logging.getLogger()
log.addHandler(logging.StreamHandler(sys.stderr))
log.setLevel(logging.DEBUG)

#------------------------------------------------------------------------------
# create a device ID, which should be globally unique. for example, the
# IMEI number for a mobile phone. in this case, we are using the local host's
# MAC address combined with the inode of the directory we want to sync.

devID       = 'pysyncml.samples.filesync:%s.%d' % (uuid.getnode(), os.stat(rootdir).st_ino)

# the storageName is the filename that the pysyncml adapter will use to
# store pysyncml private data (used to maintain session info, etc).

storageName = '.sync.db'

#------------------------------------------------------------------------------
# load all file & directory data into memory
# NOTE: *obviously* this is NOT the way to do this for a production system!

entries = dict()

def makeEntry(path):
  if os.path.islink(path):
    entry = pysyncml.FileItem()
    entry.id          = str(os.lstat(path).st_ino)
    entry.name        = os.path.basename(path)
    entry.body        = 'link: ' + os.readlink(path)
    entry.size        = len(entry.body)
    entry.contentType = 'special/symlink'
    return entry
  if os.path.isdir(path):
    entry = pysyncml.FolderItem.fromFilesystem(path)
    entry.id = str(os.stat(path).st_ino)
    return entry
  if os.path.isfile(path):
    entry = pysyncml.FileItem.fromFilesystem(path)
    entry.id = str(os.stat(path).st_ino)
    with open(path, 'rb') as fp:
      entry.body = fp.read()
    entry.size = len(entry.body)
    entry.contentType = mimetypes.guess_type(entry.name)
    return entry
  raise Exception('filesystem entry "%s" is neither a directory, file or symlink' % (path,))

def dirwalk(dir, parent):
  for name in os.listdir(dir):
    # ignore the pysyncml storage file in the root directory
    if parent.parent is None and name == storageName:
      continue
    fullpath = os.path.join(dir, name)
    entry = makeEntry(fullpath)
    entry.parent = parent.id
    entries[entry.id] = entry
    if isinstance(entry, pysyncml.FolderItem):
      # and recurse!...
      dirwalk(fullpath, entry)

# load the root entry
root = makeEntry(rootdir)
if not isinstance(root, pysyncml.FolderItem):
  raise Exception('root directory "%s" must be a directory' % (rootdir,))
root.name = ''
entries[root.id] = root

# and recursively load all others
dirwalk(rootdir, root)

#------------------------------------------------------------------------------
def entryNames(entries, entry):
  'a generator to return all names up until the filesync root directory'
  if entry.parent is not None:
    for name in entryNames(entries, entries[entry.parent]):
      yield name
  if entry.parent is None:
    return
  yield entry.name

# for k,v in entries.items():
#   print '%s: %s%s' % (k, rootdir, '/'.join(entryNames(entries, v)))

#------------------------------------------------------------------------------
# setup the synchronization agent that will do the actual work

class SyncAgent(pysyncml.BaseFileAgent):
  def __init__(self, entries, *args, **kwargs):
    super(SyncAgent, self).__init__(*args, **kwargs)
    self.entries = entries
  # # in a production system, a real getChanges() is needed in order to
  # # avoid a slow-sync at every sync.
  # def getChanges(self):
  #   raise NotImplementedError()
  def getAllItems(self):
    return self.entries.values()
  def addItem(self, item):
    fullpath = os.path.join(rootdir, *list(entryNames(self.entries, item)))
    if isinstance(item, pysyncml.FolderItem):
      os.mkdir(fullpath)
    else:
      with open(fullpath, 'wb') as fp:
        fp.write(item.body)
    ret = makeEntry(fullpath)
    ret.parent = item.parent
    self.entries[ret.id] = ret
    return ret
  def getItem(self, item):
    return self.entries[item.id]
  def replaceItem(self, item):
    if isinstance(item, pysyncml.FolderItem):
      raise Exception('error: folders cannot be replaced')
    fullpath = os.path.join(rootdir, *list(entryNames(self.entries, item)))
    print 'before:', str(os.stat(fullpath).st_ino)
    with open(fullpath, 'rb') as fp: print fp.read()
    with open(fullpath, 'wb') as fp:
      fp.write(item.body)
    print 'after:', str(os.stat(fullpath).st_ino)
    with open(fullpath, 'rb') as fp: print fp.read()
    self.entries[item.id] = item
    return item
  def deleteItem(self, item):
    fullpath = os.path.join(rootdir, *list(entryNames(self.entries, item)))
    if isinstance(item, pysyncml.FolderItem):
      os.rmdir(fullpath)
    else:
      os.unlink(fullpath)
    del self.entries[item.id]

agent = SyncAgent(entries)

#------------------------------------------------------------------------------
# setup the client adapter, with a local SyncML storage set to the sqlite
# database ".sync.db" in the root directory. we will need to ensure that
# .sync.db is excluded from the synchronized content...

adapter = pysyncml.Adapter(storage='sqlite:///%(rootdir)s%(storageName)s' %
                           dict(rootdir=rootdir, storageName=storageName))

# add the synchronization agent to accept OMA file and folder
# objects in the abstract "files" local datastore. note that this
# URI is just a channel identifier.

adapter.addAgent(agent, uri='./files', label='Local Files')

# let the adapter know that it can now load any state information, such
# as pre-registered device info, device ID, etc.

adapter.load()

#------------------------------------------------------------------------------
# setup the device configuration, if not already loaded from the storage

if adapter.devinfo is None or adapter.devinfo.devID != devID:

  # setup some information about the local device, most importantly the
  # device ID, which the server will use to uniquely identify this client.
  adapter.devinfo = pysyncml.DeviceInfo(
    devID             = devID,
    devType           = 'workstation',
    hardwareVersion   = '0.1',
    firmwareVersion   = '0.1',
    softwareVersion   = '0.1',
    manufacturerName  = 'pysyncml',
    modelName         = 'samples.filesync',
    )

#------------------------------------------------------------------------------
# setup the remote adapter, if not already loaded from serialized storage

if adapter.target is None:

  adapter.target = pysyncml.RemoteAdapter(
    url      = remote,
    auth     = pysyncml.NAMESPACE_AUTH_BASIC,
    username = 'sample',
    password = 'sample',
    )

#------------------------------------------------------------------------------
# launch the synchronization

mode = {
  'sync':      pysyncml.SYNCTYPE_TWO_WAY,
  'full':      pysyncml.SYNCTYPE_SLOW_SYNC,
  'pull':      pysyncml.SYNCTYPE_ONE_WAY_FROM_SERVER,
  'push':      pysyncml.SYNCTYPE_ONE_WAY_FROM_CLIENT,
  'pull-over': pysyncml.SYNCTYPE_REFRESH_FROM_SERVER,
  'push-over': pysyncml.SYNCTYPE_REFRESH_FROM_CLIENT,
  }[mode]

adapter.sync(mode=mode)

#------------------------------------------------------------------------------
# end of $Id: filesync.py 20 2012-06-03 04:14:27Z griff1n $
#------------------------------------------------------------------------------
