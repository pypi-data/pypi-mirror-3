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

'''
gameController.py - Controls the starting and stopping of games
'''

import logging

from trosnoth.utils.utils import timeNow
from trosnoth.utils.components import Component, handler, Plug
from trosnoth.utils.twist import WeakCallLater, WeakLoopingCall
from trosnoth.model.universe_base import GameState, NeutralTeamId
from trosnoth.model.gameStates import (LobbyState, GameInProgressState,
                                       PreGameState, RabbitHuntState)
from trosnoth.model.voteArbiter import VoteArbiter

from trosnoth.messages import (PlayerIsReadyMsg, PreferredTeamSelectedMsg,
            SetPreferredSizeMsg, SetPreferredDurationMsg, ChangeTimeLimitMsg,
            StartingSoonMsg, GameOverMsg,
            ReturnToLobbyMsg, WorldResetMsg, GameStartMsg, RemovePlayerMsg)



log = logging.getLogger('gameController')

GAME_STATE_CHECK_PERIOD = 5
TICK_PERIOD = 0.02
RABBIT_CHASING_PERIOD = 90

class GameController(Component):
    # eventPlug is a sending plug
    eventPlug = Plug()

    # orderPlug is a receiving plug
    orderPlug = Plug()

    def __init__(self, layoutDatabase, universe, duration=0, onceOnly=False):
        super(GameController, self).__init__()
        self.layoutDatabase = layoutDatabase
        self.universe = universe
        self._duration = duration
        self._setToLobbyMode()
        self._onceOnly = onceOnly
        self._loop = None
        self._lastTime = timeNow()
        self._startClock()
        self._gameStartingAt = -1
        self._gameStartDelay = -1
        self._gameOverTime = None
        self._nextGameStateCheck = self.universe.getElapsedTime()

    def _setToLobbyMode(self):
        self._state = GameState.Lobby
        self.universe.setGameState(LobbyState())
        self._gameStarter = VoteArbiter(self.universe, self.eventPlug,
                self._startGame)

    def _startGame(self, duration, size):
        layout = self.layoutDatabase.generateRandomMapLayout(size[0],
                size[1])
        self.reset(layout, duration)
        WeakCallLater(0.1, self, '_startSoon', 12)

    def _setToPreGameState(self):
        self._state = GameState.PreGame
        self.universe.setGameState(PreGameState())

    def _setToInProgressState(self):
        self._state = GameState.InProgress
        self.universe.setGameState(GameInProgressState())
        self._gameStarter = None

    def _setToStartingState(self):
        self._state = GameState.Starting
        self.universe.setGameState(PreGameState())
        self._gameStarter = None

    def _setToRabbitState(self):
        self._state = GameState.Ended
        self.universe.setGameState(RabbitHuntState())
        self._gameStarter = None

    def _startSoon(self, delay=7):
        self.eventPlug.send(StartingSoonMsg(delay))
        WeakCallLater(delay, self.eventPlug, 'send',
                GameStartMsg(self._duration))

    def reset(self, layout, gameDuration=None):
        if gameDuration is not None:
            self._duration = gameDuration
        self.universe.setLayout(layout)

        self.eventPlug.send(WorldResetMsg())

        for player in self.getPlayers():
            self.universe._resetPlayer(player)

        self._setToPreGameState()

    @orderPlug.defaultHandler
    def ignoreMessage(self, msg):
        pass

    def tick(self):
        '''Advances all players and shots to their new positions.'''
        t = timeNow()
        deltaT = t - self._lastTime
        self._lastTime = t
        self.universe.advanceEverything(deltaT)
        self.checkForResult()
        self.changeGameStateIfNeeded()
        if self._state == GameState.Ended:
            self.checkForRabbitsAllDead()

    def getGameTime(self):
        return self.universe.getElapsedTime()

    def duration(self):
        return self._duration

    def state(self):
        return self._state

    def getPlayers(self):
        return self.universe.players

    def getPlayer(self, playerId):
        return self.universe.playerWithId[playerId]

    def startNewGameIfReady(self):
        if self.layoutDatabase is None:
            return
        self._gameStarter.startNewGameIfReady()

    @handler(StartingSoonMsg, orderPlug)
    def startingSoon(self, msg):
        self._gameStartingAt = timeNow() + msg.delay
        self._gameStartDelay = msg.delay
        self._setToStartingState()

        # Kick all AI players now, the game is about to begin.
        for p in list(self.getPlayers()):
            if p.bot:
                self.eventPlug.send(RemovePlayerMsg(p.id))


    def checkForResult(self):
        if not self._state == GameState.InProgress:
            return

        # Check first for timeout
        if self.hasTimeLimit() and self.getTimeLeft() <= 0:
            team = self.universe.teamWithMoreZones()
            if team is not None:
                self.eventPlug.send(GameOverMsg(team.id, True))
            else:
                self.eventPlug.send(GameOverMsg(NeutralTeamId, True))
        # Next check for an actual winning team
        else:
            team = self.universe.teamWithAllZones()
            if team == 'Draw':
                self.eventPlug.send(GameOverMsg(NeutralTeamId, False))
            elif team is not None:
                self.eventPlug.send(GameOverMsg(team.id, False))
            else:
                # No result yet
                pass

    @handler(GameOverMsg, orderPlug)
    def gameOver(self, msg):
        self._nextGameStateCheck = (self.universe.getElapsedTime() +
                RABBIT_CHASING_PERIOD)

        self._setToRabbitState()
        self.universe.setWinningTeamById(msg.teamId)
        self._gameOverTime = self.universe.getElapsedTime()


    def changeGameStateIfNeeded(self):
        if ((self._state not in (GameState.Lobby, GameState.Ended)) or
                self._onceOnly):
            return
        if self.universe.getElapsedTime() < self._nextGameStateCheck:
            return
        self._nextGameStateCheck = (self.universe.getElapsedTime() +
                GAME_STATE_CHECK_PERIOD)

        if self._state == GameState.Ended: # At least one rabbit survived!
            log.debug('Time to return to lobby')
            self.eventPlug.send(ReturnToLobbyMsg())
            return
        assert self._state == GameState.Lobby
        self.startNewGameIfReady()

    def hasTimeLimit(self):
        if self._state != GameState.InProgress:
            return False
        return self._duration != 0


    def checkForRabbitsAllDead(self):
        log.debug('checking for rabbits all dead')
        if all(p.team is None for p in self.getPlayers()):
            self.eventPlug.send(ReturnToLobbyMsg())

    @handler(ReturnToLobbyMsg, orderPlug)
    def returnToLobby(self, msg):
        self.lobbyTeamIds = {}
        self._setToLobbyMode()
        self._nextGameStateCheck = (self.universe.getElapsedTime() +
                GAME_STATE_CHECK_PERIOD)
        log.debug('Returning to lobby')

    def getTimeLeft(self):
        '''
        If the game has no time limit, return False.
        If the game is running, get the amount of time left in the game.
        If the game has finished, get the amount of time that was left when
        the game finished.
        If the game hasn't yet started, return None.
        '''
        if self._state in (GameState.Lobby, GameState.PreGame,
                GameState.Starting):
            return None
        if self._duration == 0:
            return False
        elif self._state == GameState.InProgress:
            return self._duration - self.universe.getElapsedTime()
        elif self._state == GameState.Ended:
            return self._duration - self._gameOverTime

    def _startClock(self):
        if self._loop is not None:
            self._loop.stop()
        self._loop = WeakLoopingCall(self, 'tick')
        self._loop.start(TICK_PERIOD, False)

    def stopClock(self):
        if self._loop is not None:
            self._loop.stop()
            self._loop = None

    @handler(WorldResetMsg, orderPlug)
    def gotWorldReset(self, msg):
        self._nextGameStateCheck = (self.universe.getElapsedTime() +
                GAME_STATE_CHECK_PERIOD)
        self._setToPreGameState()

    @handler(GameStartMsg, orderPlug)
    def gameStart(self, msg):
        time = msg.timeLimit
        self._duration = time
        self._setToInProgressState()

    def _getWorldParameters(self):
        '''Returns a dict representing the settings which must be sent to
        clients that connect to this server.'''
        result = self.universe._getWorldParameters()

        if self._state == GameState.PreGame:
            result['gameState'] = "PreGame"
        elif self._state == GameState.Lobby:
            result['gameState'] = "Lobby"
        elif self._state == GameState.Starting:
            result['gameState'] = 'Starting'
        elif self._state == GameState.InProgress:
            result['gameState'] = "InProgress"
            result['timeRunning'] = self.universe.getElapsedTime()
            result['timeLimit'] = self._duration
        else:
            result['gameState'] = "Ended"

        return result

    def applyWorldParameters(self, params):
        self.universe.applyWorldParameters(params)
        gs = params.get('gameState', None)
        if gs == 'PreGame':
            self._setToPreGameState()
        elif gs == 'Starting':
            self._setToStartingState()
        elif gs == 'InProgress':
            self._setToInProgressState()
            if 'timeRunning' in params:
                self.universe._setElapsedTime(params['timeRunning'])
            if 'timeLimit' in params:
                self._duration = params['timeLimit']
        elif gs == 'Lobby':
            self._setToLobbyMode()
        elif gs == 'Ended':
            self._setToRabbitState()

    def canVote(self):
        return self._state == GameState.Lobby and not self._onceOnly

    @handler(ChangeTimeLimitMsg, orderPlug)
    def changeTimeLimit(self, msg):
        self._duration = msg.timeLimit

    @handler(PlayerIsReadyMsg, orderPlug)
    def gotPlayerIsReady(self, msg):
        try:
            player = self.getPlayer(msg.playerId)
        except KeyError:
            return

        player.readyToStart = msg.ready
        player.readyForTournament = (msg.tournament and
                player.prefersTournamentTeam)

    @handler(PreferredTeamSelectedMsg, orderPlug)
    def gotPreferredTeam(self, msg):
        try:
            player = self.getPlayer(msg.playerId)
        except KeyError:
            return

        player.preferredTeam = msg.name.decode()
        player.prefersTournamentTeam = msg.tournament
        if not player.prefersTournamentTeam:
            player.readyForTournament = False

    @handler(SetPreferredSizeMsg, orderPlug)
    def gotPreferredSize(self, msg):
        try:
            player = self.getPlayer(msg.playerId)
        except KeyError:
            return

        player.preferredSize = (msg.halfMapWidth, msg.mapHeight)

    @handler(SetPreferredDurationMsg, orderPlug)
    def gotPreferredDuration(self, msg):
        try:
            player = self.getPlayer(msg.playerId)
        except KeyError:
            return

        player.preferredDuration = msg.duration
