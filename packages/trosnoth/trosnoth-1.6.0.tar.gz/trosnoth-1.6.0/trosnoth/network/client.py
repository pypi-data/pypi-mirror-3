# Trosnoth (UberTweak Platform Game)
# Copyright (C) 2006-2011 Joshua D Bartlett
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2 as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.

import logging

from trosnoth.utils import netmsg
from trosnoth.network.networkDefines import validServerVersions
from trosnoth.messages import (ChatMsg, TaggingZoneMsg, NotifyUDPStatusMsg,
        RequestUDPStatusMsg, PlayerStarsSpentMsg, PlayerHasUpgradeMsg,
        DeleteUpgradeMsg, CannotBuyUpgradeMsg, GameStartMsg, GameOverMsg,
        StartingSoonMsg, SetTeamNameMsg, SetGameModeMsg, ShotFiredMsg,
        KillShotMsg, RespawnMsg, PlayerKilledMsg, PlayerUpdateMsg,
        CannotRespawnMsg, AddPlayerMsg, JoinSuccessfulMsg, UpdatePlayerStateMsg,
        AimPlayerAtMsg, RemovePlayerMsg, CannotJoinMsg,
        InitClientMsg, ConnectionLostMsg, GrenadeExplosionMsg,
        SetWorldParametersMsg, MapBlockLayoutMsg, ZoneStateMsg, tcpMessages,
        AchievementUnlockedMsg, PlayerHitMsg, ShotAbsorbedMsg, WorldResetMsg,
        PlayerIsReadyMsg, PreferredTeamSelectedMsg, SetPreferredDurationMsg,
        SetPreferredSizeMsg, SetPlayerTeamMsg, CreateCollectableStarMsg,
        RemoveCollectableStarMsg, PlayerHasElephantMsg, ChangeNicknameMsg,
        MarkZoneMsg, SetGameSpeedMsg, FireShoxwaveMsg, AchievementProgressMsg,
        ReturnToLobbyMsg, ChangeTimeLimitMsg, GrenadeReboundedMsg,
        StarReboundedMsg, UpgradeChangedMsg)
from trosnoth.utils.components import Component, Plug
from trosnoth.utils.twist import WeakCallLater
from trosnoth.utils.unrepr import unrepr
from twisted.internet import defer
from twisted.python.failure import Failure

log = logging.getLogger('client')

clientMsgs = netmsg.MessageCollection(
    PlayerHasElephantMsg,
    NotifyUDPStatusMsg,
    InitClientMsg,
    SetWorldParametersMsg,
    MapBlockLayoutMsg,
    CannotJoinMsg,
    DeleteUpgradeMsg,
    GrenadeExplosionMsg,
    GameStartMsg,
    TaggingZoneMsg,
    PlayerStarsSpentMsg,
    PlayerHasUpgradeMsg,
    KillShotMsg,
    ShotFiredMsg,
    AddPlayerMsg,
    SetPlayerTeamMsg,
    RespawnMsg,
    UpdatePlayerStateMsg,
    AimPlayerAtMsg,
    PlayerKilledMsg,
    GameOverMsg,
    ReturnToLobbyMsg,
    StartingSoonMsg,
    SetTeamNameMsg,
    SetGameModeMsg,
    SetGameSpeedMsg,
    JoinSuccessfulMsg,
    RemovePlayerMsg,
    PlayerUpdateMsg,
    CannotRespawnMsg,
    CannotBuyUpgradeMsg,
    ChatMsg,
    ZoneStateMsg,
    AchievementUnlockedMsg,
    PlayerHitMsg,
    ShotAbsorbedMsg,
    AchievementProgressMsg,
    WorldResetMsg,
    PlayerIsReadyMsg,
    SetPreferredDurationMsg,
    PreferredTeamSelectedMsg,
    SetPreferredSizeMsg,
    CreateCollectableStarMsg,
    RemoveCollectableStarMsg,
    ChangeNicknameMsg,
    MarkZoneMsg,
    FireShoxwaveMsg,
    ChangeTimeLimitMsg,
    GrenadeReboundedMsg,
    StarReboundedMsg,
    UpgradeChangedMsg,
)

class ConnectionFailed(Exception):
    def __init__(self, reason):
        self.reason = reason

class ClientNetHandler(Component):
    requestPlug = Plug()
    eventPlug = Plug()

    greeting = 'Trosnoth1'
    messages = clientMsgs

    def __init__(self, netman):
        Component.__init__(self)
        self.netman = netman
        self.connId = None
        self.validated = False
        self._deferred = None
        self.udpWorks = True

    def newConnection(self, connId, ipAddr, port):
        'Should never happen.'

    def makeConnection(self, host, port, timeout=7):
        assert self._deferred is None, 'Already connecting.'
        self.connId = None
        self.validated = False
        self._deferred = result = defer.Deferred()
        self.netman.connect(self, host, port, timeout)
        WeakCallLater(timeout, self, '_timedOut')
        return result

    def _timedOut(self):
        if self.connId is None or not self.validated:
            if self._deferred is not None:
                try:
                    raise ConnectionFailed('Timed out.')
                except:
                    self._deferred.errback(Failure())
                self._deferred = None

    def cancelConnecting(self):
        if self.connId is not None:
            self.netman.closeConnection(self.connId)
            self.connId = None

    def disconnect(self):
        if self.connId is not None:
            self.netman.closeConnection(self.connId)
            self.connId = None

    def connectionComplete(self, connId):
        self.connId = connId

    def receiveMessage(self, connId, msg):
        if self._deferred is not None:
            if isinstance(msg, InitClientMsg):
                self._receiveInitClientMsg(msg)
        elif isinstance(msg, NotifyUDPStatusMsg):
            self._receiveNotifyUDPStatusMsg(msg)
        else:
            self.eventPlug.send(msg)

    def _receiveInitClientMsg(self, msg):
        # Settings from the server.
        settings = unrepr(msg.settings)

        # Check that we recognise the server version.
        svrVersion = settings.get('serverVersion', 'server.v1.0.0+')
        if svrVersion not in validServerVersions:
            log.info('Client: bad server version %s', svrVersion)
            try:
                raise ConnectionFailed('Incompatible server version.')
            except:
                self._deferred.errback(Failure())
            self._deferred = None
            self.netman.closeConnection(self.connId)
            self.connId = None
            return

        # Tell the client that the connection has been made.
        self.validated = True
        self._deferred.callback(None)
        self._deferred = None

        # Wait 10 seconds then check if UDP is working.
        WeakCallLater(10, self, '_checkUDP')

    def _checkUDP(self):
        '''
        Sends a message to the server asking whether UDP works or not.
        To prevent this message from flying around out of control, this method
        should only be called once after the connection is validated, and then
        from the receiveNotifyUDPStatusMsg method as need be.
        '''
        if self.connId is not None:
            self.netman.sendTCP(self.connId, RequestUDPStatusMsg())

    def _receiveNotifyUDPStatusMsg(self, msg):
        '''
        The server is sending notification as to whether or not UDP messages
        from the server can get through to the client.
        '''
        udpWorks = bool(msg.connected)
        if not udpWorks:
            # Check again in 10 seconds.
            WeakCallLater(10, self, '_checkUDP')

        # Notify the client.
        if udpWorks != self.udpWorks:
            self.eventPlug.send(msg)

        self.udpWorks = udpWorks

    @requestPlug.defaultHandler
    def requestMsg(self, msg):
        if self.connId is not None:
            if msg.__class__ in tcpMessages:
                self.netman.sendTCP(self.connId, msg)
            else:
                self.netman.send(self.connId, msg)

    def receiveBadString(self, connId, line):
        if self._deferred is not None:
            try:
                raise ConnectionFailed('Remote host sent unexpected message: '
                        + repr(line))
            except:
                self._deferred.errback(Failure())
            self._deferred = None
            self.connId = None
            self.netman.closeConnection(connId)
            return
        log.warning('Client: Unknown message: %r', line,)
        log.warning('      : Did you invent a new network message and forget')
        log.warning('      : to add it to trosnoth.network.client.clientMsgs?')

    def connectionLost(self, connId):
        self.connId = None
        if self._deferred is not None:
            try:
                raise ConnectionFailed('Remote server dropped connection.')
            except:
                self._deferred.errback(Failure())
            self._deferred = None
            return
        self.eventPlug.send(ConnectionLostMsg())

    def connectionFailed(self, connId):
        if self._deferred is not None:
            try:
                raise ConnectionFailed('Timed out.')
            except:
                self._deferred.errback(Failure())
            self._deferred = None
            self.connId = None

