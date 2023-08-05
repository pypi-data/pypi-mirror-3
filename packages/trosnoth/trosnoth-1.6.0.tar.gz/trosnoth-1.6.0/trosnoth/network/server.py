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

from trosnoth.network.networkDefines import serverVersion
from trosnoth.utils import netmsg
from trosnoth.utils.components import DynamicPlug, UnhandledMessage

from trosnoth.messages import (ChatMsg, InitClientMsg,
        QueryWorldParametersMsg, RequestMapBlockLayoutMsg, RequestPlayersMsg,
        RequestUDPStatusMsg, NotifyUDPStatusMsg, DeleteUpgradeMsg,
        BuyUpgradeMsg, ShootMsg, RespawnRequestMsg, JoinRequestMsg,
        UpdatePlayerStateMsg, AimPlayerAtMsg,
        RequestZonesMsg, tcpMessages, PlayerIsReadyMsg, SetPreferredDurationMsg,
        SetPreferredTeamMsg, SetPreferredSizeMsg, RemovePlayerMsg,
        ChangeNicknameMsg, MarkZoneMsg, RequestGameSpeedMsg,
        RequestGameModeMsg)
from trosnoth.utils.event import Event

log = logging.getLogger('server')

# The set of messages that the server expects to receive.
serverMsgs = netmsg.MessageCollection(
    RequestUDPStatusMsg,
    QueryWorldParametersMsg,
    RequestMapBlockLayoutMsg,
    ShootMsg,
    DeleteUpgradeMsg,
    UpdatePlayerStateMsg,
    AimPlayerAtMsg,
    BuyUpgradeMsg,
    RespawnRequestMsg,
    JoinRequestMsg,
    RequestPlayersMsg,
    RequestZonesMsg,
    RequestGameSpeedMsg,
    RequestGameModeMsg,
    ChatMsg,
    PlayerIsReadyMsg,
    SetPreferredDurationMsg,
    SetPreferredTeamMsg,
    SetPreferredSizeMsg,
    RemovePlayerMsg,
    ChangeNicknameMsg,
    MarkZoneMsg,
)
class ServerNetHandler(object):
    '''
    A network message handler designed for use with trosnoth.network.netman.
    '''
    greeting = 'Trosnoth1'
    messages = serverMsgs

    def __init__(self, netman, game, authTagManager=None):
        self.netman = netman
        self.authTagManager = authTagManager
        self.connectedClients = {}      # connId -> IP addr
        self.agents = {}                # connId -> agent
        self.agentPlugs = {}            # connId -> plug

        self.onShutdown = Event()       # ()

        self.game = game

        self.running = True
        self._alreadyShutdown = False

    def connectionComplete(self, connId):
        'Should never be called'
    def connectionFailed(self, connId):
        'Should never be called'

    def receiveBadString(self, connId, line):
        log.warning('Server: Unrecognised network data: %r' % (line,))
        log.warning('      : Did you invent a new network message and forget')
        log.warning('      : to add it to trosnoth.network.server.serverMsgs?')

    def newConnection(self, connId, ipAddr, port):
        '''
        Called by the network manager when a new incoming connection is
        completed.
        '''
        # Remember that this connection's ready for transmission.
        self.connectedClients[connId] = ipAddr
        agent = self.game.addAgent(*self._makeRemoteAgent(connId))
        self.agents[connId] = agent

        # Send the setting information.
        self.netman.sendTCP(connId,
                InitClientMsg(self._getClientSettings()))

    def _makeRemoteAgent(self, connId):
        '''
        Returns (eventPlug, controller) for the remote agent.
        '''
        def sendMessage(msg):
            try:
                if msg.__class__ in tcpMessages:
                    self.netman.sendTCP(connId, msg)
                else:
                    self.netman.send(connId, msg)
            except ValueError:
                pass
        eventPlug = DynamicPlug(sendMessage)
        requestPlug = DynamicPlug(self._sendBackToRequestPlug)

        self.agentPlugs[connId] = requestPlug
        return eventPlug, requestPlug

    def _sendBackToRequestPlug(self, msg):
        raise UnhandledMessage('Server will not send %r backwards over '
                'request plug' % (msg,))

    def receiveMessage(self, connId, msg):
        if isinstance(msg, RequestUDPStatusMsg):
            # Client has requested info as to whether server is sending UDP.
            self.netman.sendTCP(connId, NotifyUDPStatusMsg(
                    self.netman.getUDPStatus(connId)))
            return

        try:
            plug = self.agentPlugs[connId]
        except KeyError:
            return
        plug.send(msg)

    def _getClientSettings(self):
        '''Returns a string representing the settings which must be sent to
        clients that connect to this server.'''

        result = {
            'serverVersion': serverVersion,
        }

        return repr(result)

    def connectionLost(self, connId):
        if connId in self.connectedClients:
            self.game.detachAgent(self.agents[connId])

        del self.connectedClients[connId]

        # Check for game over and no connections left.
        if (len(self.connectedClients) == 0 and not
                self.game.world.gameIsInProgress()):
            # Don't shut down if local player is connected.
            for p in self.game.world.players:
                if not p.bot:
                    break
            else:
                # Shut down the server.
                self.shutdown()

    def shutdown(self):
        if self._alreadyShutdown:
            return
        self._alreadyShutdown = True

        # Kill server
        self.running = False
        self.game.stop()
        self.game.gameController.stopClock()
        self.onShutdown.execute()
