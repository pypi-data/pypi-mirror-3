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
import random
from trosnoth.model.universe import Universe
from trosnoth.model.gameController import GameController
from trosnoth.model.map import MapLayout
from trosnoth.messages import (AddPlayerMsg, QueryWorldParametersMsg,
        SetWorldParametersMsg, RequestMapBlockLayoutMsg, MapBlockLayoutMsg,
        RequestPlayersMsg, PlayerUpdateMsg, RequestZonesMsg, ZoneStateMsg,
        PlayerHasUpgradeMsg, WorldResetMsg, WorldParametersReceived,
        PreferredTeamSelectedMsg, SetPreferredDurationMsg, SetPreferredSizeMsg,
        PlayerIsReadyMsg, RequestGameModeMsg, RequestGameSpeedMsg,
        SetGameSpeedMsg, SetGameModeMsg, SetTeamNameMsg)
from trosnoth.utils.components import Component, Plug, queueMessage, handler
from trosnoth.utils.twist import WeakCallLater
from trosnoth.utils.unrepr import unrepr

log = logging.getLogger(__name__)

TIMEOUT = 5

class Isolator(Component):
    '''
    This component is designed to sit between an agent and a game engine in the
    case where the agent can't see the game engine's actual world. The isolator
    creates a world which reflects the game engine's world by sending
    appropriate query messages.
    '''

    # agentEvents <- Isolator <- gameEvents
    gameEvents = Plug()
    agentEvents = Plug()

    # agentRequests -> Isolator -> gameRequests
    agentRequests = Plug()
    gameRequests = Plug()

    def __init__(self, layoutDatabase, useRealWorld=True):
        Component.__init__(self)
        if useRealWorld:
            self.world = Universe(clientOptimised=True)
            self.gameController = GameController(layoutDatabase, self.world)
        else:
            self.world = None
        self.layoutDatabase = layoutDatabase
        self.gotParams = False
        self.unknownKeys = None
        self.mapSpec = None
        self.timer = None
        self.blockPassTags = {}

    def begin(self):
        '''
        Instructs this isolator to begin getting the world information from the
        server.
        '''
        self.gameRequests.send(QueryWorldParametersMsg(random.randrange(1<<32)))

    @handler(WorldResetMsg, gameEvents)
    def gotWorldReset(self, msg):
        self.begin()
        self.agentEvents.send(msg)

    @handler(QueryWorldParametersMsg, agentRequests)
    def gotParamsQueryFromAgent(self, msg):
        self.gameRequests.send(msg)

    @handler(SetWorldParametersMsg, gameEvents)
    def gotWorldParams(self, msg):
        data = unrepr(msg.settings)
        self.mapSpec = mapSpec = data.pop('worldMap')
        if self.world is not None:
            self.gameController.applyWorldParameters(data)

            self.gotParams = True
            keys = MapLayout.unknownBlockKeys(self.layoutDatabase, mapSpec)
            self.unknownKeys = keys
            if len(keys) == 0:
                self._applyMapLayout()
            else:
                self._sendBlockRequests()
        else:
            self._requestPlayersAndZones()

        self.agentEvents.send(msg)
        self.agentEvents.send(WorldParametersReceived())

    def _applyMapLayout(self):
        layout = MapLayout.fromString(self.layoutDatabase, self.mapSpec)
        self.world.setLayout(layout)
        self._requestPlayersAndZones()
        self._requestGameSpeed()
        self._requestGameMode()

    def _requestPlayersAndZones(self):
        self._requestPlayers()
        self._requestZoneOwners()

    def _requestPlayers(self):
        self.gameRequests.send(RequestPlayersMsg())

    def _requestZoneOwners(self):
        self.gameRequests.send(RequestZonesMsg())

    def _requestGameMode(self):
        self.gameRequests.send(RequestGameModeMsg())

    def _requestGameSpeed(self):
        self.gameRequests.send(RequestGameSpeedMsg())

    def _sendBlockRequests(self):
        '''
        Sends the world requests for the map blocks unknown by our layout
        database.
        '''
        for key in self.unknownKeys:
            self.gameRequests.send(RequestMapBlockLayoutMsg(
                    random.randrange(1<<32), repr(key)))

    @handler(RequestMapBlockLayoutMsg, agentRequests)
    def gotBlockQueryFromAgent(self, msg):
        self.blockPassTags[msg.tag] = WeakCallLater(TIMEOUT,
                self, '_discardBlockTag', msg.tag)

    def _discardBlockTag(self, tag):
        if tag in self.blockPassTags:
            del self.blockPassTags[tag]

    @handler(MapBlockLayoutMsg, gameEvents)
    def gotMapBlock(self, msg):
        if msg.tag in self.blockPassTags:
            # Request came from further downstream.
            self.blockPassTags[msg.tag].cancel()
            del self.blockPassTags[msg.tag]
            self.agentEvents.send(msg)

        key, contents, graphics = unrepr(msg.data)
        self.layoutDatabase.addDownloadedBlock(key, contents, graphics)
        self.unknownKeys.remove(key)
        if len(self.unknownKeys) == 0:
            self._applyMapLayout()

    @handler(PlayerUpdateMsg, gameEvents)
    def gotPlayerUpdate(self, msg):
        if self.world is not None:
            queueMessage(self.world.orderPlug, msg)
        self.agentEvents.send(msg)

    @gameEvents.defaultHandler
    def passToAgent(self, msg):
        if self.world is not None:
            queueMessage(self.world.orderPlug, msg)
            queueMessage(self.gameController.orderPlug, msg)
        self.agentEvents.send(msg)

    @agentRequests.defaultHandler
    def passToGame(self, msg):
        self.gameRequests.send(msg)

class WorldSettingsResponder(Component):
    '''
    This component is designed to sit between an agent and a game engine in the
    case where the world is a local world, and respond to requests from the
    isolator.
    '''

    # agentEvents <- Isolator <- gameEvents
    gameEvents = Plug()
    agentEvents = Plug()

    # agentRequests -> Isolator -> gameRequests
    agentRequests = Plug()
    gameRequests = Plug()

    def __init__(self, world, gameController, layoutDatabase):
        Component.__init__(self)
        self.gameController = gameController
        self.world = world
        self.layoutDatabase = layoutDatabase

    @gameEvents.defaultHandler
    def passToAgent(self, msg):
        self.agentEvents.send(msg)

    @agentRequests.defaultHandler
    def passToGame(self, msg):
        self.gameRequests.send(msg)

    @handler(QueryWorldParametersMsg, agentRequests)
    def queryWorldParams(self, msg):
        data = self.gameController._getWorldParameters()
        data['worldMap'] = self.world.map.layout.toString()
        self.agentEvents.send(SetWorldParametersMsg(msg.tag,
                repr(data)))
        for team in self.world.teams:
            self.agentEvents.send(SetTeamNameMsg(team.id,
                    team.teamName.encode('utf-8')))

    @handler(RequestMapBlockLayoutMsg, agentRequests)
    def queryMapBlock(self, msg):
        key = unrepr(msg.key)
        layout = self.layoutDatabase.getLayoutByKey(key)
        if layout is None:
            # We do not know the key.
            contents = None
            graphics = None
        else:
            contents = open(layout.filename, 'rU').read()
            graphics = layout.getGraphicsData()
        data = (key, contents, graphics)
        self.agentEvents.send(MapBlockLayoutMsg(msg.tag, repr(data)))

    @handler(RequestPlayersMsg, agentRequests)
    def queryPlayers(self, msg):
        for player in self.world.players:
            self.agentEvents.send(AddPlayerMsg(player.id, player.teamId,
                    player.currentZone.id, player.ghost, player.bot,
                    player.nick.encode()))
            self.agentEvents.send(player.makePlayerUpdate())
            if not player.bot:
                self.agentEvents.send(PreferredTeamSelectedMsg(player.id,
                        player.prefersTournamentTeam,
                        player.preferredTeam.encode()))
                self.agentEvents.send(SetPreferredSizeMsg(player.id,
                        player.preferredSize[0], player.preferredSize[1]))
                self.agentEvents.send(SetPreferredDurationMsg(player.id,
                        player.preferredDuration))
                self.agentEvents.send(PlayerIsReadyMsg(player.id,
                        player.readyToStart, player.readyForTournament))

        self.queryUpgrades()

    @handler(RequestZonesMsg, agentRequests)
    def queryZones(self, msg):
        for zone in self.world.zones:
            if zone.orbOwner is None:
                owner = '\x00'
            else:
                owner = zone.orbOwner.id
            dark = zone.zoneOwner != None
            marks = ''
            for team, value in zone.markedBy.iteritems():
                if value:
                    if team is not None:
                        marks += team.id
                    else:
                        marks += '\x00'
            self.agentEvents.send(ZoneStateMsg(zone.id, owner, dark, marks))

    @handler(RequestGameModeMsg, agentRequests)
    def queryGameMode(self, msg):
        self.agentEvents.send(SetGameModeMsg(self.world.gameMode.encode()))

    @handler(RequestGameSpeedMsg, agentRequests)
    def queryGameSpeed(self, msg):
        self.agentEvents.send(SetGameSpeedMsg(self.world._gameSpeed))

    def queryUpgrades(self):
        for player in self.world.players:
            if player.upgrade is not None:
                self.agentEvents.send(PlayerHasUpgradeMsg(player.id,
                        player.upgrade.upgradeType, 'X'))
