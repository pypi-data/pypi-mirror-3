# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id: context.py 27 2012-06-27 02:26:15Z griff1n $
# lib:  pysyncml.context
# auth: griffin <griffin@uberdev.org>
# date: 2012/06/23
# copy: (C) CopyLoose 2012 UberDev <hardcore@uberdev.org>, No Rights Reserved.
#------------------------------------------------------------------------------

'''
The ``pysyncml.context`` package provides the entry point into most
pysyncml operations via the :class:`pysyncml.context.Context` class.

For more information and links to documentation, please go to::

  http://pypi.python.org/pypi/pysyncml/

'''

import sqlalchemy.ext.declarative
from sqlalchemy.orm.exc import NoResultFound
from . import model, codec, router, protocol, synchronizer

#------------------------------------------------------------------------------
class Context(object):

  #----------------------------------------------------------------------------
  def __init__(self,
               engine=None, storage=None, prefix='pysyncml', owner=None,
               autoCommit=None,
               router=None, protocol=None, synchronizer=None, codec=None,
               ):
    '''
    Constructs a new Context object. Accepts the following parameters,
    of which all are optional:

      :param owner:

        an integer owner ID. necessary primarily when the adapter
        storage is shared between multiple users/adapter agents
        (i.e. in server contexts). if it is not shared, `owner` can be
        left as None (the default).

      :param storage:

        the sqlalchemy storage specification where all the SyncML-
        related data should be stored.

        NOTE: overridden by parameter `engine`.

        NOTE: the storage driver *MUST* support cascading deletes;
        this is done automatically for connections created directly by
        pysyncml for mySQL and sqlite, but it is up to the calling
        program to ensure this for other databases or if the database
        engine is passed in via parameter `engine`. Specifically,
        InnoDB is requested for mySQL tables and ``PRAGMA
        foreign_keys=ON`` is issued for sqlite databases.

      :param engine:

        the sqlalchemy storage engine where all the SyncML-related
        data should be stored.

        NOTE: overrides parameter `storage`.

        NOTE: see notes under parameter `storage` for details on
        cascading delete support.

      :param prefix:

        sets a database table name prefix. this is primarily useful
        when using the `engine` parameter, as multiple pysyncml contexts
        can then be defined within the same database namespace.
        defaults to ``pysyncml``.

      :param autoCommit:

        whether or not to execute a storage engine "commit" when syncing
        is complete. the default behavior is dependent on if `dbEngine`
        is provided: if non-None, then autoCommit defaults to False,
        otherwise, defaults to True.

      :param router:

        overrides the default router with an object that must implement
        the interface specified by :class:`pysyncml.router.Router`.

      :param protocol:

        sets the semantic objective to/from protocol evaluation and
        resolution object, which must implement the
        :class:`pysyncml.protocol.Protocol` interface.

      :param synchronizer:

        this is the engine for handling sync requests and dispatching
        them to the various agents. if specified, the object must
        implement the :class:`pysyncml.synchronizer.Synchronizer`
        interface.

      :param codec:

        specify the codec used to encode the SyncML commands -
        typically either \'xml\' (the default) or \'wbxml\'. it can
        also be an object that implements the
        :class:`pysyncml.codec.Codec` interface.

    '''
    self.autoCommit = autoCommit if autoCommit is not None else engine is None
    self._model = model.createModel(
      engine     = engine,
      storage    = storage,
      prefix     = prefix,
      owner_id   = owner,
      context    = self,
      )
    self.router       = router
    self.protocol     = protocol
    self.synchronizer = synchronizer
    self.codec        = codec
    for attr in dir(self._model):
      if attr in ('DatabaseObject', 'RawDatabaseObject', 'Version', 'Adapter'):
        continue
      value = getattr(self._model, attr)
      if issubclass(value.__class__, sqlalchemy.ext.declarative.DeclarativeMeta) \
         and value != self._model.DatabaseObject:
        setattr(self, attr, value)

  #----------------------------------------------------------------------------
  # TBD: add a method to delete all entries with a specific owner...
  #----------------------------------------------------------------------------

  #----------------------------------------------------------------------------
  def Adapter(self, **kw):
    try:
      ret = self._model.Adapter.q(isLocal=True).one()
      for k, v in kw.items():
        setattr(ret, k, v)
    except NoResultFound:
      ret = self._model.Adapter(**kw)
      ret.isLocal = True
      self._model.session.add(ret)
      if ret.devID is not None:
        self._model.session.flush()
    # tbd: is this really the best place to do this?...
    ret.router        = self.router or router.Router(ret)
    ret.protocol      = self.protocol or protocol.Protocol(ret)
    ret.synchronizer  = self.synchronizer or synchronizer.Synchronizer(ret)
    ret.codec         = self.codec or 'xml'
    if isinstance(ret.codec, basestring):
      ret.codec = codec.Codec.factory(ret.codec)
    if ret.devID is not None:
      peers = ret.getKnownPeers()
      if len(peers) == 1 and peers[0].url is not None:
        ret._peer = peers[0]
    return ret

  #----------------------------------------------------------------------------
  def RemoteAdapter(self, **kw):
    # TBD: is this really the right way?...
    ret = self._model.Adapter(isLocal=False, **kw)
    self._model.session.add(ret)
    if ret.devID is not None:
      self._model.session.flush()
    return ret

  #----------------------------------------------------------------------------
  @staticmethod
  def getAuthInfo(request, authorizer):
    xtree = codec.Codec.autoDecode(request.headers['content-type'], request.body)
    return protocol.Protocol.getAuthInfo(xtree, None, authorizer)

  #----------------------------------------------------------------------------
  def save(self):
    # TBD: is this just here for the test classes?... might this be better
    #      marked as an internal method?...
    # tbd: is the "flush" really necessary?...
    if self.autoCommit:
      self._model.session.flush()
      self._model.session.commit()

#------------------------------------------------------------------------------
# end of $Id: context.py 27 2012-06-27 02:26:15Z griff1n $
#------------------------------------------------------------------------------
