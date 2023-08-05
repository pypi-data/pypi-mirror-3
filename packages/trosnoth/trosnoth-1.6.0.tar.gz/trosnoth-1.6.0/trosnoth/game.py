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

from email.mime.text import MIMEText
import logging
import random

from trosnoth.ai import makeAIAgent, listAIs
from trosnoth.model import modes
from trosnoth.model.universe import Universe
from trosnoth.model.gameController import GameController
from trosnoth.model.idmanager import IdManager
from trosnoth.model.validator import Validator
from trosnoth.model.agentfilter import AgentFilter
from trosnoth.model.universe_base import GameState
from trosnoth.model.isolator import Isolator, WorldSettingsResponder
from trosnoth.messages import (SetTeamNameMsg, GameStartMsg, GameOverMsg,
        SetGameModeMsg, RemovePlayerMsg, PlayerHasUpgradeMsg,
        SetGameSpeedMsg, ChangeTimeLimitMsg, ChangePlayerLimitsMsg,
        DeleteUpgradeMsg, UpgradeChangedMsg, ChatMsg)
from trosnoth.model.upgrades import allUpgrades, upgradeOfType
from trosnoth.gamerecording.gamerecorder import makeGameRecorder
from trosnoth.utils.twist import WeakLoopingCall

log = logging.getLogger('game')

def makeLocalGame(gameName, layoutDatabase, halfMapWidth, mapHeight, duration=0,
        maxPlayers=8, authTagManager=None, alertSettings=None, onceOnly=False,
        bootServer=True):
    '''
    Makes and returns a local game.
    layoutDatabase may be a LayoutDatabase, or None. If None, the game will not
    be queryable by remote games.
    '''
    alerter = Alerter(alertSettings)
    idManager = IdManager()
    world = Universe(authTagManager=authTagManager, gameName=gameName)
    gameController = GameController(layoutDatabase, world, duration=duration,
                                    onceOnly=onceOnly)
    validator = Validator(world, maxPlayers, authTagManager, alerter=alerter)

    world.eventPlug.connectPlug(idManager.inPlug)
    world.orderPlug.connectPlug(idManager.outPlug)
    gameController.eventPlug.connectPlug(idManager.inPlug)
    gameController.orderPlug.connectPlug(idManager.outPlug)

    validator.gameRequests.connectPlug(idManager.inPlug)
    validator.gameEvents.connectPlug(idManager.outPlug)

    gameRecorder = makeGameRecorder(world, gameController, layoutDatabase,
            idManager)

    if layoutDatabase is None:
        game = Game(world, gameController, validator.agentEvents,
                validator.agentRequests, gameRecorder, bootServer=bootServer)
    else:
        game = QueryableGame(world, gameController, validator.agentEvents,
                validator.agentRequests, gameRecorder, layoutDatabase,
                bootServer=bootServer)
    layout = layoutDatabase.generateRandomMapLayout(halfMapWidth, mapHeight)
    world.setLayout(layout)
    gameRecorder.begin()
    return game

def makeIsolatedGame(layoutDatabase):
    '''
    Returns game, eventPlug, controller where game is a Game object and
    eventPlug and controller are plugs which allow this game to be connected
    into another game as an agent.

    This is here to test that having separate universes talking to each other
    works, without having to set up a server over the network.
    '''
    game = IsolatedGame(layoutDatabase)

    return game, game.eventPlug, game.requestPlug

class Game(object):
    def __init__(self, world, gameController, outPlug, inPlug, gameRecorder,
            bootServer=False):
        self.gameController = gameController
        self.world = world
        self._outPlug = outPlug
        self._inPlug = inPlug
        self.gameRecorder = gameRecorder
        if bootServer:
            self.aiInjector = AIInjector(self)
        else:
            self.aiInjector = None

    @property
    def name(self):
        return self.world.gameName

    def addAgent(self, eventPlug, controller):
        '''
        Connects an agent to this game. An agent may be a user interface,
        an AI player, or anything that wants to receive events from the game
        and potentially send actions to it.

        Returns a value which can be passed to game.detachAgent() to detach this
        agent.
        '''
        f = AgentFilter()
        f.gameEvents.connectPlug(self._outPlug)
        f.agentEvents.connectPlug(eventPlug)
        f.agentRequests.connectPlug(controller)
        f.gameRequests.connectPlug(self._inPlug)

        return f

    def addAI(self, aiName='alpha', team=None):
        ai = makeAIAgent(self.world, aiName)
        self.addAgent(ai.eventPlug, ai.requestPlug)

        if team is not None:
            team = self.world.teams[team]
        ai.start(team)
        return ai

    def detachAgent(self, f):
        f.agentRequests.disconnectAll()
        f.agentEvents.disconnectAll()
        f.disconnect()
        f.gameEvents.disconnectAll()
        f.gameRequests.disconnectAll()

    def getGameMode(self):
        '''
        Returns the current game mode.
        '''
        return self.world.gameMode

    def setGameMode(self, gameMode):
        '''
        Changes the current game mode of the world.

        @returns: True if the specified game mode was valid, False otherwise.
        '''
        if self.world.physics.hasMode(gameMode):
            self.world.eventPlug.send(SetGameModeMsg(gameMode.encode()))
            return True
        return False

    def listGameModes(self):
        '''
        Returns a list of valid game modes.
        '''
        return [m[len('setMode'):] for m in dir(modes.PhysicsConstants) if
                m.startswith('setMode') if m != 'setMode']

    def getSpeed(self):
        '''
        Returns the current speed of the world as a float, where 1.0 is
        the normal game speed.
        '''

        return self.world._gameSpeed

    def setSpeed(self, gameSpeed):
        '''
        Changes the speed of the world, where 1.0 is normal speed.

        @param gameSpeed: A positive number
        '''
        self.world.eventPlug.send(SetGameSpeedMsg(gameSpeed))

    def kickPlayer(self, playerId):
        '''
        Removes the player with the specified ID from the game.
        '''
        self.world.eventPlug.send(RemovePlayerMsg(playerId))

    def startGame(self, countdown = False):
        '''
        Starts the game.

        @param countdown: A boolean which determines whether to countdown first
        (giving the players a notification) or start immediately. Skipping the
        countdown in lobby mode will result in unexpected behaviour.
        '''
        if countdown:
            self.gameController._gameStarter.startNewGame()
        else:
            self.world.eventPlug.send(GameStartMsg(
                    self.gameController._duration))

    def endGame(self, teamId):
        '''
        Immediately ends the game in favour of the specified team.

        @param team: The ID of the winning time, or None for a draw.
        '''
        if teamId is None:
            self.world.eventPlug.send(GameOverMsg('\x00', False))
        else:
            if teamId in self.world.teamWithId.keys():
                self.world.eventPlug.send(GameOverMsg(teamId, False))

    def giveUpgrade(self, player, upgradeCode):
        '''
        Gives an upgrade to a player, which is used immediately.

        @param player: Player object
        @param upgradeCode: Single character upgrade code
        '''
        self.world.eventPlug.send(PlayerHasUpgradeMsg(player.id, upgradeCode,
                'S'))

    def removeUpgrade(self, player):
        '''
        Removes the specified player's current upgrade.

        @param player: Player object
        '''
        currentUpgrade = player.upgrade
        if currentUpgrade is not None:
            self.world.eventPlug.send(DeleteUpgradeMsg(player.id,
                        currentUpgrade.upgradeType, 'X'))

    def getPlayers(self):
        '''
        Returns a mapping of player name to player object.
        '''
        return dict((p.nick, p) for p in self.world.players)

    def getTimeRemaining(self):
        '''
        If the game hasn't yet started, return None.
        If the game has no time limit, return False.
        If the game is running, get the amount of time left in the game.
        If the game has finished, get the amount of time that was left when
        the game finished.
        '''
        return self.gameController.getTimeLeft()

    def setTimeRemaining(self, time):
        '''
        Sets the remaining game time to the given number of seconds or, if None
        is given, to be unlimited.
        '''
        if time is None or time == 0:
            timeLimit = 0
        else:
            timeLimit = time

        self.world.eventPlug.send(ChangeTimeLimitMsg(timeLimit))

    def setPlayerLimits(self, maxPerTeam, maxTotal=0):
        '''
        Changes the player limits in the current game. Note that this does not
        affect players who are already in the game.

        @param maxPerTeam: Maximum number of players per team at once
        @param maxTotal: Maximum number of players in the game at once
        '''
        self.world.eventPlug.send(ChangePlayerLimitsMsg(maxPerTeam, maxTotal))

    def setTeamName(self, teamId, teamName):
        '''
        Changes the name of the specified team.

        @param teamId: The id of the team ('A' or 'B')
        @param teamName: The next team name
        '''
        try:
            team = self.world.teamWithId[teamId]
        except KeyError:
            return
        self.world.eventPlug.send(SetTeamNameMsg(team.id, teamName.encode()))

    def getTeamNames(self):
        '''
        Returns the name of both teams as a tuple.
        '''
        return (
            self.world.teams[0].teamName,
            self.world.teams[1].teamName
        )

    def getGameState(self):
        '''
        Returns the current state of the game as a string.

        @returns: One of ('PreGame', 'Lobby', 'Starting', 'InProgress', 'Ended',
        'Unknown')
        '''
        currentGameState = self.gameController.state()
        if currentGameState == GameState.PreGame:
            return 'PreGame'
        if currentGameState == GameState.Lobby:
            return 'Lobby'
        if currentGameState == GameState.Starting:
            return 'Starting'

        if currentGameState == GameState.InProgress:
            return 'InProgress'
        if currentGameState == GameState.Ended:
            return 'Ended'

        return 'Unknown'

    def getWinningTeam(self):
        '''
        Returns the winning team.

        If the game hasn't finished yet, the behaviour is undefined.
        @returns: The ID of the winning team or None if it was a draw
        '''
        if self.world.getWinningTeam() is None:
            return None

        return self.world.getWinningTeam().id

    def getOrbCounts(self):
        '''
        Returns the number of zones owned by each team as a tuple.
        '''
        return (
            self.world.teams[0].numOrbsOwned,
            self.world.teams[1].numOrbsOwned
        )

    def getUpgrades(self):

        upgrades = []

        for key, upgrade in upgradeOfType.iteritems():
            newUpgrade = {
                "id": key,
                "name": upgrade.name,
                "starCost": upgrade.requiredStars,
                "timeLimit": upgrade.timeRemaining,
                "order": upgrade.order,
                "icon": "upgrade_blank",
                "special": False
            }

            if upgrade not in allUpgrades:
                newUpgrade["order"] += 1000
                newUpgrade["special"] = True

            if upgrade.iconPath is not None:
                newUpgrade["icon"] = upgrade.iconPath.replace("-", "_")[:-4]

            upgrades.append(newUpgrade)

        upgrades.sort(key=lambda upgrade: upgrade["order"])

        return upgrades

    def setUpgradeCost(self, upgradeId, cost):
        '''
        Changes how many stars are required to purchase a particular upgrade.

        @param upgradeId: The single character ID of the upgrade
        @param cost: The new number of stars required.
        '''
        if cost < 0:
            return

        for upgradeClass in allUpgrades:
            if upgradeClass.upgradeType == upgradeId:
                upgradeClass.requiredStars = cost
                break
        self.world.eventPlug.send(UpgradeChangedMsg(upgradeId, 'S', cost))

    def setUpgradeTime(self, upgradeId, time):
        '''
        Changes how long a particular upgrade lasts.

        @param upgradeId: The single character ID of the upgrade
        @param time: The time (in seconds) that the upgrade will last for.
            Setting this to 0 will make the upgrade never naturally run out.
        '''
        if time < 0:
            return

        for upgradeClass in allUpgrades:
            if upgradeClass.upgradeType == upgradeId:
                upgradeClass.timeRemaining = time
                break
        self.world.eventPlug.send(UpgradeChangedMsg(upgradeId, 'T', time))

    def sendServerMessage(self, message):
        self.world.eventPlug.send(ChatMsg('\x00', 's', '\x00', message))

    def reset(self, halfMapWidth=None, mapHeight=None, gameDuration=None):
        if halfMapWidth is None:
            halfMapWidth = self.world.map.layout.halfMapWidth
        if mapHeight is None:
            mapHeight = self.world.map.layout.mapHeight
        layout = self.layoutDatabase.generateRandomMapLayout(halfMapWidth,
                mapHeight)
        self.gameController.reset(layout, gameDuration)

    def stop(self):
        if self.gameRecorder is not None:
            self.gameRecorder.stop()
        if self.aiInjector is not None:
            self.aiInjector.stop()

class QueryableGame(Game):
    '''
    Represents a game which may be queried about its state by agents. This is
    used for network servers so that the client universe can be updated to
    reflect the server universe.
    '''

    def __init__(self, world, gameController, outPlug, inPlug, gameRecorder,
            layoutDatabase, bootServer=False):
        Game.__init__(self, world, gameController, outPlug, inPlug,
                gameRecorder, bootServer=bootServer)
        self.layoutDatabase = layoutDatabase

    def addAgent(self, eventPlug, controller):
        wsr = WorldSettingsResponder(self.world, self.gameController,
                self.layoutDatabase)
        f = Game.addAgent(self, wsr.gameEvents, wsr.gameRequests)
        wsr.agentEvents.connectPlug(eventPlug)
        wsr.agentRequests.connectPlug(controller)

        return (f, wsr)

    def detachAgent(self, (f, wsr)):
        wsr.agentRequests.disconnectAll()
        wsr.agentEvents.disconnectAll()
        Game.detachAgent(self, f)

class IsolatedGame(Game):
    '''
    Used to encapsulate a game where we have no world, only streams of events
    (e.g. over the network). Behaves like a standard Game object, with the
    following additional attributes:
        .eventPlug, .requestPlug - plugs by which this game can communicate with
            the game it is mirroring.
        .syncWorld() - instructs this game to begin to syncronise its world with
            the remote world. Only call this method after eventPlug and
            requestPlug have been connected.
    '''
    def __init__(self, layoutDatabase):
        self._isolator = isolator = Isolator(layoutDatabase)
        Game.__init__(self, isolator.world, isolator.gameController,
                isolator.agentEvents, isolator.agentRequests, None)
        self.eventPlug = isolator.gameEvents
        self.requestPlug = isolator.gameRequests

    def syncWorld(self):
        self._isolator.begin()


class Alerter(object):
    '''
    Sends email alerts to a nominated email address.
    '''
    def __init__(self, settings):
        self.settings = settings

    def send(self, event, message):
        if self.settings is None or self.settings.recipientAddress is None:
            return
        alertSetting = getattr(self.settings, 'alertOn%s' % (event,))
        if not alertSetting:
            return

        from twisted.mail.smtp import sendmail

        msg = MIMEText(message)
        msg['Subject'] = self.settings.subject
        msg['From'] = sender = self.settings.senderAddress
        if isinstance(alertSetting, (str, unicode)):
            msg['To'] = recipient = alertSetting
        else:
            msg['To'] = recipient = self.settings.recipientAddress

        sendmail(self.settings.smtpServer, sender, [recipient], msg.as_string())

class AIInjector(object):
    def __init__(self, game, playerCount=6):
        self.game = game
        self.playerCount = playerCount
        self.loop = WeakLoopingCall(self, 'tick')
        self.loop.start(3, False)
        self.agents = []
        self.newAgents = set()
        self.aiNames = listAIs(playableOnly=True)

    def stop(self):
        if self.loop.running:
            self.loop.stop()

    def tick(self):
        self._graduateNewAgents()

        if self.game.gameController.state() != GameState.Lobby:
            self._stopAllAgents()
        else:
            self._adjustAgentsToTarget()

    def _graduateNewAgents(self):
        for agent in list(self.newAgents):
            if agent.playerId is not None:
                self.agents.append(agent)
                self.newAgents.remove(agent)

    def _stopAllAgents(self):
        if len(self.agents) != 0:
            log.info('AIInjector: Stopping all agents')
        for agent in self.agents:
            agent.stop()
            if agent.playerId is not None:
                try:
                    self.game.kickPlayer(agent.playerId)
                except Exception, e:
                    log.exception(str(e))
        self.agents = []

    def _adjustAgentsToTarget(self):
        worldPlayers = len(self.game.world.players)
        newAgents = len(self.newAgents)
        if self.playerCount > worldPlayers + newAgents:
            self._addAgents(self.playerCount - worldPlayers - newAgents)
        else:
            self._removeAgents(worldPlayers + newAgents - self.playerCount)

    def _addAgents(self, count):
        log.info('AIInjector: Adding %d agents', count)
        for i in xrange(count):
            self.newAgents.add(self.game.addAI(random.choice(self.aiNames)))

    def _removeAgents(self, count):
        if count != 0:
            log.info('AIInjector: Removing %d agents', count)
        for i in xrange(count):
            if len(self.agents) == 0:
                break
            agent = self.agents.pop(0)
            agent.stop()
            self.game.kickPlayer(agent.playerId)

