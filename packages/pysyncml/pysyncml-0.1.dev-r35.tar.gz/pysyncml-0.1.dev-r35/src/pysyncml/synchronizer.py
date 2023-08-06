# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id: synchronizer.py 34 2012-07-03 02:48:00Z griff1n $
# lib:  pysyncml.synchronizer
# auth: griffin <griffin@uberdev.org>
# date: 2012/05/20
# copy: (C) CopyLoose 2012 UberDev <hardcore@uberdev.org>, No Rights Reserved.
#------------------------------------------------------------------------------

'''
The ``pysyncml.synchronizer`` is an internal package that does all of the actual
"work" for the SyncML Adapter.
'''

import sys, base64, logging
from elementtree import ElementTree as ET
from sqlalchemy.orm.exc import NoResultFound
from . import common, constants, model, state

log = logging.getLogger(__name__)

#------------------------------------------------------------------------------
class Synchronizer(object):

  #----------------------------------------------------------------------------
  def __init__(self, adapter, *args, **kw):
    super(Synchronizer, self).__init__(*args, **kw)
    self.adapter = adapter

  #----------------------------------------------------------------------------
  def actions(self, adapter, session):
    ret = []
    for uri, dsstate in session.dsstates.items():
      if dsstate.action == 'done':
        continue
      method = getattr(self, 'action_' + dsstate.action, None)
      if method is None:
        raise common.InternalError('unexpected datastore action "%s"' % (dsstate.action,))
      # todo: trap errors...
      ret += method(adapter, session, uri, dsstate) or []
    return ret

  #----------------------------------------------------------------------------
  def action_alert(self, adapter, session, uri, dsstate):
    src = adapter.stores[uri]
    tgt = adapter.peer.stores[dsstate.peerUri] 

    # TODO: ensure that mode is acceptable...

    # todo: perhaps i should only specify maxObjSize if it differs from
    #       adapter.maxObjSize?...

    return [state.Command(
      cmd         = constants.CMD_ALERT,
      cmdID       = session.nextCmdID,
      data        = dsstate.mode,
      source      = src.uri,
      target      = tgt.uri,
      lastAnchor  = dsstate.lastAnchor,
      nextAnchor  = dsstate.nextAnchor,
      maxObjSize  = src.maxObjSize,
      )]

  #----------------------------------------------------------------------------
  def action_send(self, adapter, session, uri, dsstate):
    store = adapter.stores[uri]
    agent = store.agent
    peerStore = adapter.peer.stores[adapter.router.getTargetUri(uri)]

    cmd = state.Command(
      cmd    = constants.CMD_SYNC,
      cmdID  = session.nextCmdID,
      source = uri,
      # target = adapter.router.getTargetUri(uri),
      target = dsstate.peerUri,
      )

    # todo: this should really be a negative match...
    if dsstate.mode not in (
      constants.ALERT_TWO_WAY,
      constants.ALERT_SLOW_SYNC,
      constants.ALERT_ONE_WAY_FROM_CLIENT,
      constants.ALERT_REFRESH_FROM_CLIENT,
      constants.ALERT_ONE_WAY_FROM_SERVER,
      constants.ALERT_REFRESH_FROM_SERVER,
      # todo: these should only be received out-of-band, right?...
      # constants.ALERT_TWO_WAY_BY_SERVER,
      # constants.ALERT_ONE_WAY_FROM_CLIENT_BY_SERVER,
      # constants.ALERT_REFRESH_FROM_CLIENT_BY_SERVER,
      # constants.ALERT_ONE_WAY_FROM_SERVER_BY_SERVER,
      # constants.ALERT_REFRESH_FROM_SERVER_BY_SERVER,
      ):
      raise common.InternalError('unexpected sync mode "%s"' % (common.mode2string(dsstate.mode),))

    log.debug('sending sync commands for URI "%s" in %s mode (anchor: %s)',
              uri, common.mode2string(dsstate.mode),
              dsstate.lastAnchor or '-')

    if ( session.isServer and dsstate.mode in (constants.ALERT_REFRESH_FROM_CLIENT,
                                               constants.ALERT_ONE_WAY_FROM_CLIENT) ) \
       or ( not session.isServer and dsstate.mode in (constants.ALERT_REFRESH_FROM_SERVER,
                                                      constants.ALERT_ONE_WAY_FROM_SERVER) ):
      # nothing to send (wrong side of the receiving end of one-way sync) and
      # nothing to do (refreshes get performed on "reaction" side of a sync)
      return [cmd]

    if dsstate.mode in (
      constants.ALERT_TWO_WAY,
      constants.ALERT_ONE_WAY_FROM_CLIENT,  # when not session.isServer
      constants.ALERT_ONE_WAY_FROM_SERVER,  # when session.isServer
      ):
      # send local changes
      changes  = adapter._context._model.Change.q(store_id=peerStore.id)
      cmd.data = []
      ctype    = adapter.router.getBestTransmitContentType(uri)

      for change in changes:
        scmdtype = {
          constants.ITEM_ADDED    : constants.CMD_ADD,
          constants.ITEM_MODIFIED : constants.CMD_REPLACE,
          constants.ITEM_DELETED  : constants.CMD_DELETE,
          }.get(change.state)
        if scmdtype is None:
          log.error('could not resolve item state %d to sync command', change.state)
          continue
        scmd = state.Command(
          cmd     = scmdtype,
          cmdID   = session.nextCmdID,
          format  = constants.FORMAT_AUTO,
          type    = ctype[0],
          uri     = uri,
          )
        # TODO: need to add hierarchical addition support here...
        if scmdtype != constants.CMD_DELETE:
          scmd.data = agent.dumpsItem(agent.getItem(change.itemID), ctype[0], ctype[1])
        if scmdtype == constants.CMD_ADD:
          scmd.source = change.itemID
        else:
          if session.isServer:
            try:
              # todo: this is a bit of an abstraction violation...
              query = adapter._context._model.Mapping.q(store_id=peerStore.id, guid=change.itemID)
              scmd.target = query.one().luid
            except NoResultFound:
              scmd.source = change.itemID
          else:
            scmd.source = change.itemID
        cmd.data.append(scmd)

      cmd.noc  = len(cmd.data)
      return [cmd]

    if dsstate.mode in (
      constants.ALERT_SLOW_SYNC,
      constants.ALERT_REFRESH_FROM_SERVER,  # when session.isServer
      constants.ALERT_REFRESH_FROM_CLIENT,  # when not session.isServer
      ):
      cmd.data = []
      for item in agent.getAllItems():

        # TODO: these should all be non-deleted items, right?...

        # log.critical('TODO: correct state detection...')
        scmd = constants.CMD_ADD

        # if item.state == constants.ITEM_DELETED:
        #   # NOTE: i would *like* to send a 'Delete' command to the server,
        #   #       for this item, but some servers (funambol) just ignore
        #   #       the request... so, we'll delete it client-side, and hope
        #   #       that the server doesn't send it again...
        #   # TODO: AS A WORKAROUND to the above note, i *could* keep the
        #   #       item around, and if i receive an 'Add' instruction, then
        #   #       just ignore it... this means, however, that i would need
        #   #       to be able to map an added item back to a local current
        #   #       item, which opens a can of worms...
        #   agent.deleteItem(item.id)
        #   continue
        # scmd = {
        #   constants.ITEM_OK       : constants.CMD_ADD,
        #   constants.ITEM_ADDED    : constants.CMD_ADD,
        #   constants.ITEM_MODIFIED : constants.CMD_ADD,
        #   constants.ITEM_DELETED  : constants.CMD_DELETE,
        #   }.get(item.state)
        # if scmd is None:
        #   log.error('could not resolve item state %d to sync command', item.state)
        #   continue

        ctype = adapter.router.getBestTransmitContentType(uri)
        cmd.data.append(state.Command(
          cmd     = scmd,
          cmdID   = session.nextCmdID,
          format  = constants.FORMAT_AUTO,
          type    = ctype[0],
          uri     = uri,
          source  = str(item.id),
          data    = None if scmd == constants.CMD_DELETE else agent.dumpsItem(item, ctype[0], ctype[1]),
          ))
      cmd.noc = len(cmd.data)
      return [cmd]

    raise common.InternalError('unexpected sync situation (action=%s, mode=%s, isServer=%s)'
                               % (dsstate.action, common.mode2string(dsstate.mode),
                                  '1' if session.isServer else '0'))

  #----------------------------------------------------------------------------
  def action_save(self, adapter, session, uri, dsstate):
    if not session.isServer:
      # TODO: for now, only servers should take the "save" action - the client
      #       will explicitly do this at the end of the .sync() method.
      #       ... mostly because clients don't call synchronizer.actions()
      #       one final time ...
      #       *BUT* perhaps that should be changed?... for example, .sync()
      #       could call synchronizer.actions() to cause action_save's to occur
      #       *AND* verify that synchronizer.actions() does not return anything...
      raise common.InternalError('unexpected sync situation (action=%s, isServer=%s)'
                                 % (dsstate.action, '1' if session.isServer else '0'))
    log.debug('storing anchors: peer=%s; source=%s/%s; target=%s/%s',
              adapter.peer.devID, uri, dsstate.nextAnchor,
              dsstate.peerUri, dsstate.peerNextAnchor)
    peerStore = adapter.peer.stores[dsstate.peerUri]
    peerStore.binding.sourceAnchor = dsstate.nextAnchor
    peerStore.binding.targetAnchor = dsstate.peerNextAnchor

  #----------------------------------------------------------------------------
  def reactions(self, adapter, session, commands):
    ret = []
    for cmd in commands:
      method = getattr(self, 'reaction_' + cmd.cmd.lower(), None)
      if method is None:
        raise common.InternalError('unexpected reaction requested to command "%s"'
                                   % (cmd.cmd,))
      ret.extend(method(adapter, session, cmd) or [])
    return ret

  #----------------------------------------------------------------------------
  def reaction_sync(self, adapter, session, command):
    ret = [state.Command(
      cmd        = constants.CMD_STATUS,
      cmdID      = session.nextCmdID,
      msgRef     = command.msgID,
      cmdRef     = command.cmdID,
      targetRef  = command.target,
      sourceRef  = command.source,
      statusOf   = command.cmd,
      statusCode = constants.STATUS_OK,
      )]
    store = adapter.stores[adapter.cleanUri(command.target)]
    dsstate = session.dsstates[store.uri]
    if ( not session.isServer and dsstate.mode == constants.ALERT_REFRESH_FROM_SERVER ) \
       or ( session.isServer and dsstate.mode == constants.ALERT_REFRESH_FROM_CLIENT ):
      # delete all local items
      for item in store.agent.getAllItems():
        store.agent.deleteItem(item.id)
        dsstate.stats.hereDel += 1
        # TODO: register change for other peers... i.e.
        # store.registerChange(item.id, constants.ITEM_DELETED, excludePeer=adapter.peer.id)

    for cmd in command.data:
      method = getattr(self, 'reaction_sync_' + cmd.cmd.lower(), None)
      if method is None:
        raise common.InternalError('unexpected reaction requested to sync command "%s"'
                                   % (cmd.cmd,))
      ret.extend(method(adapter, session, cmd, store) or [])
    return ret

  #----------------------------------------------------------------------------
  def reaction_sync_add(self, adapter, session, cmd, store):
    item = store.agent.addItem(cmd.data)
    session.dsstates[store.uri].stats.hereAdd += 1
    # TODO: register change for other peers... i.e.
    # store.registerChange(item.id, constants.ITEM_ADDED, excludePeer=adapter.peer.id)
    ret = [state.Command(
      cmd        = constants.CMD_STATUS,
      cmdID      = session.nextCmdID,
      msgRef     = cmd.msgID,
      cmdRef     = cmd.cmdID,
      sourceRef  = cmd.source,
      statusOf   = cmd.cmd,
      statusCode = constants.STATUS_ITEM_ADDED,
      )]
    if session.isServer:
      peerStore = adapter.peer.stores[session.dsstates[store.uri].peerUri]
      adapter._context._model.Mapping.q(store_id=peerStore.id, guid=item.id).delete()
      newmap = adapter._context._model.Mapping(store_id=peerStore.id, guid=item.id, luid=cmd.source)
      adapter._context._model.session.add(newmap)
    else:
      ret.append(state.Command(
        cmd        = constants.CMD_MAP,
        cmdID      = session.nextCmdID,
        source     = store.uri,
        target     = adapter.router.getTargetUri(store.uri),
        sourceItem = item.id,
        targetItem = cmd.source,
        ))
    return ret

  #----------------------------------------------------------------------------
  def reaction_sync_replace(self, adapter, session, cmd, store):
    item = cmd.data
    item.id = cmd.target
    store.agent.replaceItem(item)
    session.dsstates[store.uri].stats.hereMod += 1
    # TODO: register change for other peers... i.e.
    # store.registerChange(item.id, constants.ITEM_MODIFIED, excludePeer=adapter.peer.id)
    return [state.Command(
      cmd        = constants.CMD_STATUS,
      cmdID      = session.nextCmdID,
      msgRef     = cmd.msgID,
      cmdRef     = cmd.cmdID,
      targetRef  = cmd.target,
      statusOf   = cmd.cmd,
      statusCode = constants.STATUS_OK,
      )]

  #----------------------------------------------------------------------------
  def reaction_sync_delete(self, adapter, session, cmd, store):
    store.agent.deleteItem(cmd.target)
    session.dsstates[store.uri].stats.hereDel += 1
    # TODO: register change for other peers... i.e.
    # store.registerChange(item.id, constants.ITEM_DELETED, excludePeer=adapter.peer.id)
    return [state.Command(
      cmd        = constants.CMD_STATUS,
      cmdID      = session.nextCmdID,
      msgRef     = cmd.msgID,
      cmdRef     = cmd.cmdID,
      targetRef  = cmd.target,
      statusOf   = cmd.cmd,
      statusCode = constants.STATUS_OK,
      )]

#------------------------------------------------------------------------------
# end of $Id: synchronizer.py 34 2012-07-03 02:48:00Z griff1n $
#------------------------------------------------------------------------------
