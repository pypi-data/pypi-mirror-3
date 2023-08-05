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

import random
import pygame

from trosnoth.gui.framework import framework, hotkey, console
from trosnoth.gui.framework.elements import TextElement
from trosnoth.gui import keyboard
from trosnoth.gui.common import Region, Screen, Location, Canvas

from trosnoth.gamerecording.achievementlist import availableAchievements

from trosnoth.trosnothgui.ingame import viewManager
from trosnoth.trosnothgui.ingame.replayInterface import (ReplayMenu,
        ViewControlInterface)
from trosnoth.trosnothgui.ingame.gameMenu import GameMenu
from trosnoth.trosnothgui.ingame.detailsInterface import DetailsInterface
from trosnoth.trosnothgui.ingame.observerInterface import ObserverInterface
from trosnoth.trosnothgui.ingame.playerInterface import PlayerInterface

from trosnoth import keymap

from trosnoth.data import user, getPath

from trosnoth.utils.components import Component, Plug, handler

from trosnoth.model.universe import Abort

from trosnoth.utils.math import distance
from trosnoth.utils.event import Event
from trosnoth.utils.twist import WeakCallLater

from trosnoth.messages import (TaggingZoneMsg, ChatFromServerMsg, ChatMsg,
        GameStartMsg, GameOverMsg,
        StartingSoonMsg, ShotFiredMsg, RespawnMsg, CannotRespawnMsg,
        PlayerKilledMsg, JoinRequestMsg, JoinSuccessfulMsg, CannotJoinMsg,
        AddPlayerMsg, RemovePlayerMsg, PlayerHasUpgradeMsg,
        WorldParametersReceived, PlayerStarsSpentMsg, DeleteUpgradeMsg,
        CannotBuyUpgradeMsg, ConnectionLostMsg, NotifyUDPStatusMsg,
        GrenadeExplosionMsg, AchievementUnlockedMsg, WorldResetMsg,
        SetPlayerTeamMsg, PlayerHasElephantMsg, FireShoxwaveMsg, MarkZoneMsg)

from twisted.internet import defer

class GameInterface(framework.CompoundElement, Component):
    '''Interface for when we are connected to a game.'''

    controller = Plug()
    eventPlug = Plug()

    achievementDefs = availableAchievements

    def __init__(self, app, game, onDisconnectRequest=None,
            onConnectionLost=None, replay=False, authTag=0):
        framework.CompoundElement.__init__(self, app)
        Component.__init__(self)
        self.authTag = authTag

        self.onDisconnectRequest = Event()
        if onDisconnectRequest is not None:
            self.onDisconnectRequest.addListener(onDisconnectRequest)

        self.onConnectionLost = Event()
        if onConnectionLost is not None:
            self.onConnectionLost.addListener(onConnectionLost)
        self.game = game
        self.gameController = game.gameController
        self.world = game.world

        self.keyMapping = keyboard.KeyboardMapping(keymap.default_game_keys)
        self.updateKeyMapping()
        self.gameViewer = viewManager.GameViewer(self.app, self, game, replay)
        if replay:
            self.gameMenu = ReplayMenu(self.app, self.world)
            closeReplay = self.onDisconnectRequest.execute
            self.gameMenu.onDisconnectRequest.addListener(closeReplay)
        else:
            self.gameMenu = GameMenu(self.app, self, self.game)
        self.detailsInterface = DetailsInterface(self.app, self)
        self.runningPlayerInterface = None
        self.observerInterface = ObserverInterface(self.app, self)
        self.menuHotkey = hotkey.MappingHotkey(self.app, 'menu',
                mapping=self.keyMapping)
        self.menuHotkey.onActivated.addListener(self.showMenu)
        self.winnerMsg = TextElement(app, '',
                app.screenManager.fonts.winMessageFont, Location(
                Canvas(512, 30), 'midtop'), (128, 128, 128))
        self.elements = [
                         self.gameViewer, self.gameMenu,
                         self.menuHotkey, self.detailsInterface,
                         self.winnerMsg
                        ]
        self.hotkeys = hotkey.Hotkeys(self.app, self.keyMapping,
                self.detailsInterface.doAction)
        self.menuShowing = True
        self.terminal = None

        self.joiningDeferred = None

        self.vcInterface = None
        if replay:
            self.vcInterface = ViewControlInterface(self.app, self)
            self.elements.append(self.vcInterface)
            self.hideMenu()

    @eventPlug.defaultHandler
    def ignoreMessage(self, msg):
        pass

    @handler(WorldResetMsg, eventPlug)
    def gotWorldReset(self, msg):
        self.winnerMsg.setText('')

    def updateKeyMapping(self):
        # Set up the keyboard mapping.
        try:
            # Try to load keyboard mappings from the user's personal settings.
            config = open(getPath(user, 'keymap'), 'rU').read()
            self.keyMapping.load(config)
        except IOError:
            pass

    @handler(ConnectionLostMsg, eventPlug)
    def connectionLost(self, msg):
        self.cleanUp()
        self.gameMenu.cleanUp()
        self.onConnectionLost.execute()

    @handler(WorldParametersReceived, eventPlug)
    def gotWorldParamsMsg(self, msg):
        self.gameMenu.gotWorldParameters()

    def joined(self, player):
        '''Called when joining of game is successful.'''

        pygame.key.set_repeat()
        self.runningPlayerInterface = pi = PlayerInterface(self.app, self,
                player.id)
        self.detailsInterface.setPlayer(player)
        self.elements = [self.gameViewer,
                         pi, self.menuHotkey, self.hotkeys,
                         self.detailsInterface, self.winnerMsg]

    def showMenu(self):
        if self.runningPlayerInterface is not None:
            if self.runningPlayerInterface.player is not None:
                # Can't get to this particular menu after you've joined the
                # game.
                return
        self.elements = [self.gameViewer, self.gameMenu]
        self.menuShowing = True
        if self.vcInterface is not None:
            self.elements.insert(2, self.vcInterface)

    def hideMenu(self):
        if self.runningPlayerInterface is not None:
            self.elements = [self.gameViewer, self.runningPlayerInterface,
                    self.gameMenu, self.menuHotkey, self.hotkeys,
                    self.detailsInterface, self.winnerMsg]
        else:
            self.elements = [self.gameViewer, self.observerInterface,
                    self.gameMenu, self.menuHotkey, self.hotkeys,
                    self.detailsInterface, self.winnerMsg]
        if self.vcInterface is not None:
            self.elements.insert(2, self.vcInterface)

        self.menuShowing = False

    def toggleTerminal(self):
        if self.terminal is None:
            locs = {'app': self.app}
            if hasattr(self.app, 'getConsoleLocals'):
                locs.update(self.app.getConsoleLocals())
            self.terminal = console.TrosnothInteractiveConsole(self.app,
                self.app.screenManager.fonts.consoleFont,
                Region(size=Screen(1, 0.4), bottomright=Screen(1, 1)),
                locals=locs)
            self.terminal.interact().addCallback(self._terminalQuit)

        from trosnoth.utils.utils import timeNow
        if self.terminal in self.elements:
            if timeNow() > self._termWaitTime:
                self.elements.remove(self.terminal)
        else:
            self._termWaitTime = timeNow() + 0.1
            self.elements.append(self.terminal)
            self.setFocus(self.terminal)

    def _terminalQuit(self, result):
        if self.terminal in self.elements:
            self.elements.remove(self.terminal)
        self.terminal = None

    def disconnect(self):
        self.cleanUp()
        self.onDisconnectRequest.execute()

    def joinGame(self, nick, team, timeout=5):
        result = defer.Deferred()
        if self.joiningDeferred is not None:
            result.errback(AssertionError('Already in process of joining.'))
            return result

        if team is None:
            teamId = '\x00'
        else:
            teamId = team.id

        self.controller.send(JoinRequestMsg(teamId, random.randrange(1<<32),
                nick=nick.encode(), authTag=self.authTag, bot=False))
        self.joiningDeferred = result
        WeakCallLater(timeout, self, '_joinTimedOut')

        return result

    @handler(JoinSuccessfulMsg, eventPlug)
    def joinedOk(self, msg):
        WeakCallLater(0, self, '_joinedOk', msg)

    def _joinedOk(self, msg):
        d = self.joiningDeferred
        if d is None:
            return

        try:
            player = self.world.playerWithId[msg.playerId]
        except KeyError:
            # Retry until the timeout cancels it.
            WeakCallLater(0.5, self, '_joinedOk', msg)
        else:
            d.callback(('success', player))
            self.joiningDeferred = None

    @handler(CannotJoinMsg, eventPlug)
    def joinFailed(self, msg):
        d = self.joiningDeferred
        if d is None:
            return
        r = msg.reasonId
        if r == 'F':
            d.callback(['full'])
        elif r == 'O':
            d.callback(['over'])
        elif r == 'W':
            d.callback(['wait', str(round(msg.waitTime, 1))])
        elif r == 'N':
            d.callback(['nick'])
        elif r == 'B':
            d.callback(['badn'])
        elif r == 'A':
            d.callback(['auth'])
        elif r == 'U':
            d.callback(['user'])
        else:
            d.callback(['unknown reason code: %s' % (r,)])
        self.joiningDeferred = None

    def _joinTimedOut(self):
        if self.joiningDeferred is None:
            return
        self.joiningDeferred.callback(['timeout'])
        self.joiningDeferred = None

    def cleanUp(self):
        if self.gameViewer.timerBar is not None:
            self.gameViewer.timerBar.kill()
            self.gameViewer.timerBar = None
        pygame.key.set_repeat(300, 30)

    def gameOver(self, winningTeam):
        if winningTeam:
            self.winnerMsg.setText('%s win' % (winningTeam,))
            self.winnerMsg.setColour(
                    self.app.theme.colours.chatColour(winningTeam))

            self.playSound('gameLose')
        else:
            self.winnerMsg.setText('Game drawn')
            self.winnerMsg.setColour((128, 128, 128))

    @handler(PlayerStarsSpentMsg, eventPlug)
    def discard(self, msg):
        pass

    @handler(PlayerHasElephantMsg, eventPlug)
    def gotElephant(self, msg, _lastElephantPlayer=[None]):
        try:
            player = self.world.getPlayer(msg.playerId)
            if player != _lastElephantPlayer[0]:
                message = '%s now has Jerakeen!' % (player.nick,)
                self.detailsInterface.newMessage(message)
                _lastElephantPlayer[0] = player
        except Abort:
            pass

    @handler(MarkZoneMsg, eventPlug)
    def markZone(self, msg):
        try:
            if msg.value:
                player = self.world.getPlayer(msg.playerId)
                zone = self.world.getZone(msg.zoneId)
                self.detailsInterface.newMessage('%s has marked %s' % (player,
                        zone))
        except Abort:
            pass

    @handler(AddPlayerMsg, eventPlug)
    def addPlayer(self, msg):
        try:
            player = self.world.getPlayer(msg.playerId)
            message = '%s has joined %s' % (player.nick, player.team)
            self.detailsInterface.newMessage(message)
        except Abort:
            pass

    @handler(SetPlayerTeamMsg, eventPlug)
    def changeTeam(self, msg):
        try:
            player = self.world.getPlayer(msg.playerId)
            message = '%s has joined %s' % (player.nick,
                    self.world.getTeamName(msg.teamId))
            self.detailsInterface.newMessage(message)
        except Abort:
            pass

    @handler(RemovePlayerMsg, eventPlug)
    def removePlayer(self, msg):
        try:
            player = self.world.getPlayer(msg.playerId)
            message = '%s has left the game' % (player.nick,)
            self.detailsInterface.newMessage(message)
        except Abort:
            pass

    @handler(GameStartMsg, eventPlug)
    def gameStart(self, msg):
        message = 'The game is now on!!'
        self.detailsInterface.newMessage(message)
        if self.gameViewer.timerBar:
            self.gameViewer.timerBar.loop()
        self.playSound('startGame', 1)

    @handler(GameOverMsg, eventPlug)
    def gameIsOver(self, msg):
        try:
            team = self.world.teamWithId[msg.teamId]
        except KeyError:
            team = None
        self.gameOver(team)
        if msg.timeOver:
            message2 = 'Game time limit has expired'
            self.detailsInterface.newMessage(message2)
        if self.gameViewer.timerBar:
            self.gameViewer.timerBar.gameFinished()
        #self.playSound('end', 1)

    def getChatColour(self, team):
        return self.app.theme.colours.chatColour(team)

    @handler(CannotBuyUpgradeMsg, eventPlug)
    def notEnoughStars(self, msg):
        if self.detailsInterface.player.id == msg.playerId:
            if msg.reasonId == 'N':
                text = 'Your team does not have enough stars.'
            elif msg.reasonId == 'A':
                text = 'You already have an upgrade.'
            elif msg.reasonId == 'D':
                text = 'You cannot buy an upgrade while dead.'
            elif msg.reasonId == 'P':
                text = 'You cannot buy an upgrade before the game starts.'
            elif msg.reasonId == 'T':
                text = 'There is already a turret in this zone.'
            elif msg.reasonId == 'E':
                text = 'You are too close to the zone edge.'
            elif msg.reasonId == 'O':
                text = 'You are too close to the orb.'
            elif msg.reasonId == 'F':
                text = 'You are not in a dark friendly zone.'
            elif msg.reasonId == 'I':
                text = 'Upgrade not recognised by server.'
            else:
                text = 'You cannot buy that upgrade at this time.'
            self.detailsInterface.newMessage(text)

    @handler(PlayerHasUpgradeMsg, eventPlug)
    def gotUpgrade(self, msg):
        try:
            player = self.world.getPlayer(msg.playerId)
            self.detailsInterface.upgradeUsed(player)

            if (self.detailsInterface.player is None or
                    self.detailsInterface.player.isFriendsWith(player)):
                if msg.upgradeType == 't':
                    self.playSound('turret')
                else:
                    self.playSound('buyUpgrade')
        except Abort:
            pass

    @handler(DeleteUpgradeMsg, eventPlug)
    def deleteUpgradeMsg(self, msg):
        try:
            player = self.world.getPlayer(msg.playerId)
            self.detailsInterface.upgradeDestroyed(player, player.upgrade)
        except Abort:
            pass

    @handler(ChatFromServerMsg, eventPlug)
    def gotChatFromServer(self, msg):
        self.detailsInterface.newMessage(msg.text.decode())

    @handler(StartingSoonMsg, eventPlug)
    def startingSoon(self, msg):
        self.detailsInterface.newMessage('Both teams are ready. '
                'Game starting in %d seconds' % msg.delay)

    @handler(TaggingZoneMsg, eventPlug)
    def zoneTagged(self, msg):
        try:
            zoneId = self.world.zoneWithId[msg.zoneId].id
        except KeyError:
            zoneId = '<?>'

        if msg.playerId == '\x00':
            message = 'Zone %s rendered neutral' % (zoneId,)
        else:
            try:
                player = self.world.playerWithId[msg.playerId]
            except KeyError:
                nick = '<?>'
            else:
                nick = player.nick
                # Draw a star.
                rect = self.gameViewer.worldgui.getPlayerSprite(player.id).rect
                self.detailsInterface.starGroup.star(rect.center)
            message = '%s tagged zone %s' % (nick, zoneId)

        self.detailsInterface.newMessage(message)
        #self.playSound('tag', 1)

    @handler(PlayerKilledMsg, eventPlug)
    def playerKilled(self, msg):
        try:
            target = self.world.getPlayer(msg.targetId)
            try:
                killer = self.world.playerWithId[msg.killerId]
            except KeyError:
                killer = None
                message = '%s was killed' % (target.nick,)
                self.detailsInterface.newMessage(message)
            else:
                message = '%s killed %s' % (killer.nick, target.nick)
                self.detailsInterface.newMessage(message)
                if (self.runningPlayerInterface is not None and
                        self.runningPlayerInterface.player == killer):
                    rect = self.gameViewer.worldgui.getPlayerSprite(target.id
                            ).rect
                    self.detailsInterface.starGroup.star(rect.center)
        except Abort:
            pass

    @handler(RespawnMsg, eventPlug)
    def playerRespawn(self, msg):
        try:
            player = self.world.getPlayer(msg.playerId)
            message = '%s is back in the game' % (player.nick,)
            self.detailsInterface.newMessage(message)
            #dist = self.distance(msg.player.pos)
            #self.playSound('respawn', self.getSoundVolume(dist))
        except Abort:
            pass

    @handler(CannotRespawnMsg, eventPlug)
    def respawnFailed(self, msg):
        if msg.reasonId == 'P':
            message = 'The game has not started yet.'
        elif msg.reasonId == 'A':
            message = 'You are already alive.'
        elif msg.reasonId == 'T':
            message = 'You cannot respawn yet.'
        elif msg.reasonId == 'E':
            message = 'Cannot respawn outside friendly zone.'
        else:
            message = 'You cannot respawn here.'
        self.detailsInterface.newMessage(message,
                self.app.theme.colours.errorMessageColour)

    def sendPrivateChat(self, player, targetId, text):
        self.controller.send(ChatMsg(player.id, 'p', targetId, text.encode()))

    def sendTeamChat(self, player, text):
        self.controller.send(ChatMsg(player.id, 't', player.teamId,
                text.encode()))

    def sendPublicChat(self, player, text):
        self.controller.send(ChatMsg(player.id, 'o', '\x00', text.encode()))

    @handler(ChatMsg, eventPlug)
    def chat(self, msg):
        if msg.kind == 's':
            self.detailsInterface.newServerChat(msg.text.decode())
            return

        try:
            sender = self.world.getPlayer(msg.playerId)
            if msg.kind == 't':
                target = self.world.getTeam(msg.targetId)
            elif msg.kind == 'p':
                target = self.world.getPlayer(msg.targetId)
            else:
                target = None
            self.detailsInterface.newChat(msg.text.decode(), sender, target)
            #self.playSound('chat', 1)
        except Abort:
            pass

    @handler(AchievementUnlockedMsg, eventPlug)
    def achievementUnlocked(self, msg):
        try:
            player = self.world.getPlayer(msg.playerId)
        except Abort:
            return
        achievementName = self.achievementDefs.getAchievementDetails(
                msg.achievementId)[0]
        self.detailsInterface.newMessage('%s has unlocked "%s"!' %
                (player.nick, achievementName),
                self.app.theme.colours.achievementMessageColour)

        focusPlayer = self.detailsInterface.player
        if (focusPlayer is not None and focusPlayer.id == msg.playerId):
            self.detailsInterface.localAchievement(msg.achievementId)
            #self.playSound('achievement', 1)


    @handler(ShotFiredMsg, eventPlug)
    def shotFired(self, msg):
        try:
            shot = self.world.getShot(msg.playerId, msg.shotId)
            pos = shot.pos
            dist = self.distance(pos)
            self.playSound('shoot', self.getSoundVolume(dist))
        except Abort:
            pass

    @handler(GrenadeExplosionMsg, eventPlug)
    def grenadeExploded(self, msg):
        self.gameViewer.worldgui.addExplosion((msg.xpos, msg.ypos))
        dist = self.distance((msg.xpos, msg.ypos))
        self.playSound('explodeGrenade', self.getSoundVolume(dist))

    @handler(FireShoxwaveMsg, eventPlug)
    def shoxwaveExplosion(self, msg):
    	self.gameViewer.worldgui.addShoxwaveExplosion((msg.xpos, msg.ypos))

    @handler(NotifyUDPStatusMsg, eventPlug)
    def udpStatusChanged(self, msg):
        if msg.connected:
            self.detailsInterface.udpNotifier.hide()
        else:
            self.detailsInterface.udpNotifier.show()

    def distance(self, pos):
        return distance(self.gameViewer.viewManager.getTargetPoint(), pos)

    def getSoundVolume(self, distance):
        'The volume for something that far away from the player'
        # Up to 500px away is within the "full sound zone" - full sound
        distFromScreen = max(0, distance - 500)
        # 1000px away from "full sound zone" is 0 volume:
        return 1 - min(1, (distFromScreen / 1000.))

    def playSound(self, action, volume=1):
        self.app.soundPlayer.play(action, volume)

