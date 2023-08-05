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

import pygame

from trosnoth.gui.framework import framework
from trosnoth.gui.framework.elements import PictureElement
from trosnoth.gui.common import (Location, FullScreenAttachedPoint,
        ScaledSize, Area, Canvas)
from trosnoth.gui.framework.unobtrusiveValueGetter import YesNoGetter

from trosnoth.trosnothgui.ingame.messagebank import MessageBank
from trosnoth.trosnothgui.ingame.stars import StarGroup
from trosnoth.trosnothgui.ingame.udpnotify import UDPNotificationBar
from trosnoth.trosnothgui.ingame import mainMenu
from trosnoth.trosnothgui.ingame.gamevote import GameVoteMenu, NicknameBox
from trosnoth.trosnothgui.ingame.gauges import (TurretGauge, RespawnGauge,
        UpgradeGauge, GunGauge, StarGauge)
from trosnoth.trosnothgui.ingame.achievementBox import AchievementBox
from trosnoth.trosnothgui.ingame.chatBox import ChatBox
from trosnoth.gui.framework.dialogbox import DialogResult
from trosnoth.trosnothgui.settings.settings import SettingsMenu

from trosnoth.model.upgrades import (allUpgrades, Grenade, Ninja, Turret,
        Directatorship, Ricochet, Shoxwave)
from trosnoth.model.team import Team
from trosnoth.model.player import Player

from trosnoth.messages import (BuyUpgradeMsg, DeleteUpgradeMsg,
        RespawnRequestMsg, ChangeNicknameMsg, MarkZoneMsg)

log = logging.getLogger('detailsInterface')

class DetailsInterface(framework.CompoundElement):
    '''Interface containing all the overlays onto the screen:
    chat messages, player lists, gauges, stars, etc.'''
    def __init__(self, app, gameInterface):
        super(DetailsInterface, self).__init__(app)
        world = gameInterface.world
        self.gameController = gameInterface.gameController
        self.gameInterface = gameInterface

        # Maximum number of messages viewable at any one time
        maxView = 8

        self.world = world
        self.player = None
        font = app.screenManager.fonts.messageFont
        self.currentMessages = MessageBank(self.app, maxView, 50,
                Location(FullScreenAttachedPoint(ScaledSize(-40,-40),
                'bottomright'), 'bottomright'), 'right', 'bottom', font)

        # If we want to keep a record of all messages and their senders
        self.input = None
        self.inputText = None
        self.unobtrusiveGetter = None
        self.turretGauge = None
        self.reloadGauge = GunGauge(self.app, Area(
                FullScreenAttachedPoint(ScaledSize(0,-60), 'midbottom'),
                ScaledSize(100,30), 'midbottom'))
        self.respawnGauge = None
        self.upgradeGauge = None
        self.achievementBox = None
        self.currentUpgrade = None
        self.starGroup = StarGroup(self.app)
        self.udpNotifier = UDPNotificationBar(self.app)
        self.settingsMenu = SettingsMenu(app, onClose=self.hideSettings,
                showThemes=False)

        self.chatBox = ChatBox(app, self.world, self.gameInterface)

        menuloc = Location(FullScreenAttachedPoint((0,0), 'bottomleft'),
                'bottomleft')
        self.menuManager = mainMenu.MainMenu(self.app, menuloc, self,
                self.gameInterface.keyMapping)
        self.upgradeDisplay = UpgradeDisplay(app)
        self.gameVoteMenu = GameVoteMenu(app, world,
                onChange=self._castGameVote)
        self._gameVoteUpdateCounter = 0
        self.elements = [self.currentMessages, self.upgradeDisplay,
                self.reloadGauge, self.starGroup,
                self.gameVoteMenu, self.udpNotifier,
                self.chatBox]

        self.upgradeMap = dict((upgradeClass.action, upgradeClass) for
                upgradeClass in allUpgrades)

    @property
    def controller(self):
        return self.gameInterface.controller

    def tick(self, deltaT):
        super(DetailsInterface, self).tick(deltaT)
        if self.player is None:
            self.gameVoteMenu.active = False
            return
        else:
            if self._gameVoteUpdateCounter <= 0:
                self.gameVoteMenu.update(self.player)
                self._gameVoteUpdateCounter = 25
            else:
                self._gameVoteUpdateCounter -= 1

        self._updateTurretGauge()
        self._updateRespawnGauge()
        self._updateUpgradeGauge()
        self._updateAchievementBox()
        self._updateGameVoteMenu()

    def _castGameVote(self, msg):
        self.controller.send(msg)

    def _updateGameVoteMenu(self):
        if self.gameController.canVote():
            self.gameVoteMenu.active = True
        else:
            self.gameVoteMenu.active = False

    def localAchievement(self, achievementId):
        if self.achievementBox is None:
            self.achievementBox = AchievementBox(self.app, self.player,
                                                 achievementId)
            self.elements.append(self.achievementBox)
        else:
            self.achievementBox.addAchievement(achievementId)

    def _updateAchievementBox(self):
        if (self.achievementBox is not None and
                len(self.achievementBox.achievements) == 0):
            self.elements.remove(self.achievementBox)
            self.achievementBox = None

    def _updateTurretGauge(self):
        player = self.player
        if self.turretGauge is None:
            if player.turret:
                self.turretGauge = TurretGauge(self.app, Area(
                        FullScreenAttachedPoint(ScaledSize(0,-100),
                        'midbottom'), ScaledSize(100,30), 'midbottom'),
                        player)
                self.elements.append(self.turretGauge)
        elif not player.turret:
            self.elements.remove(self.turretGauge)
            self.turretGauge = None

    def _updateRespawnGauge(self):
        player = self.player
        if self.respawnGauge is None:
            if player.ghost:
                self.respawnGauge = RespawnGauge(self.app, Area(
                        FullScreenAttachedPoint(ScaledSize(0,-20),
                        'midbottom'), ScaledSize(100,30), 'midbottom'),
                        player, self.gameController)
                self.elements.append(self.respawnGauge)
        elif not player.ghost:
            self.elements.remove(self.respawnGauge)
            self.respawnGauge = None

    def _updateUpgradeGauge(self):
        player = self.player
        if self.upgradeGauge is None:
            if player.upgrade is not None:
                self.upgradeGauge = UpgradeGauge(self.app, Area(
                        FullScreenAttachedPoint(ScaledSize(0,-20),
                        'midbottom'), ScaledSize(100,30), 'midbottom'),
                        player)
                self.elements.append(self.upgradeGauge)
        elif player.upgrade is None:
            self.elements.remove(self.upgradeGauge)
            self.upgradeGauge = None

    def gameOver(self, winningTeam):
        self.gameInterface.gameOver(winningTeam)

    def setPlayer(self, player):
        self.player = player
        self.reloadGauge.player = player
        if self.menuManager not in self.elements:
            self.elements.append(self.menuManager)

    def showSettings(self):
        if self.settingsMenu not in self.elements:
            self.elements.append(self.settingsMenu)

    def hideSettings(self):
        if self.settingsMenu in self.elements:
            self.elements.remove(self.settingsMenu)
            self.gameInterface.updateKeyMapping()

    def _setCurrentUpgrade(self, upgradeType):
        self.currentUpgrade = upgradeType
        self.upgradeDisplay.setUpgrade(self.currentUpgrade, self.player)
        self.menuManager.manager.reset()

    def _requestUpgrade(self):
        if self.currentUpgrade is not None:
            self.controller.send(BuyUpgradeMsg(self.player.id,
                    self.currentUpgrade.upgradeType, random.randrange(1<<32)))

    def _changeNickname(self):
        if not self.world.canRename():
            self.newMessage('Cannot change nickname after game has started',
                    self.app.theme.colours.errorMessageColour)
            return

        prompt = NicknameBox(self.app)
        @prompt.onClose.addListener
        def _customEntered():
            if prompt.result == DialogResult.OK:
                nickname = prompt.value
                self.controller.send(ChangeNicknameMsg(self.player.id,
                        nickname.encode()))

        prompt.show()

    def markZone(self):
        zone = self.getZoneAtCursor()
        if zone is None:
            return
        self.controller.send(MarkZoneMsg(self.player.id, zone.id, not
                zone.markedBy.get(self.player.team, False)))

    def getZoneAtCursor(self):
        return self.gameInterface.gameViewer.getZoneAtPoint(
                pygame.mouse.get_pos())

    def doAction(self, action):
        '''
        Activated by hotkey or menu.
        action corresponds to the action name in the keyMapping.
        '''
        if action == 'leaderboard':
            self.showPlayerDetails()
            self.menuManager.manager.reset()
        elif action == 'toggle interface':
            self.toggleInterface()
            self.menuManager.manager.reset()
        elif action == 'more actions':
            if self.menuManager is not None:
                self.menuManager.showMoreMenu()
        elif action == 'settings':
            self.showSettings()
        elif action == 'maybeLeave':
            if self.menuManager is not None:
                self.menuManager.showQuitMenu()
        elif action == 'leave':
            # Disconnect from the server.
            self.gameInterface.disconnect()
        elif action == 'menu':
            # Return to main menu and show or hide the menu.
            if self.menuManager is not None:
                self.menuManager.escape()
        elif action == 'follow':
            if self.gameInterface.gameViewer.replay:
                # Replay-specific: follow the action.
                self.gameInterface.gameViewer.setTarget(None)
        elif action == 'toggle terminal':
            self.gameInterface.toggleTerminal()
        else:
            # All actions after this line should require a player.
            if self.player is None:
                return
            if action == 'respawn':
                self.controller.send(RespawnRequestMsg(self.player.id,
                        random.randrange(1<<32)))
            elif action in self.upgradeMap:
                self._setCurrentUpgrade(self.upgradeMap[action])
            elif action == 'no upgrade':
                self._setCurrentUpgrade(None)
                self.menuManager.manager.reset()
            elif action == 'abandon':
                self.abandon(self.player)
                self.menuManager.manager.reset()
            elif action == 'chat':
                self.chat()
                self.menuManager.manager.reset()
            elif action == 'select upgrade':
                if self.menuManager is not None:
                    self.menuManager.showBuyMenu()
            elif action == 'activate upgrade':
                self._requestUpgrade()
            elif action == 'change nickname':
                self._changeNickname()
            elif action == 'mark zone':
                self.markZone()
            elif action not in ('jump', 'right', 'left', 'down'):
                log.warning('Unknown action: %r', action)

    def newMessage(self, text, colour=None):
        if colour is None:
            colour = self.app.theme.colours.grey
        self.currentMessages.newMessage(text, colour)

    def newChat(self, text, sender, private):
        nick = sender.nick
        if not private:
            # Message for everyone
            text = ": " + text

        elif isinstance(private, Player) and self.player is private:
            # Destined for the one player
            text = " (private): " + text

        elif (isinstance(private, Team) and self.player is not None and
                self.player.team == private):
            # Destined for the one team.
            text = " (team): " + text

        else:
            # May not have been destined for our player after all.
            return

        colour = self.app.theme.colours.chatColour(sender.team)

        self.chatBox.newMessage(text,
                nick, colour)

    def newServerChat(self, text):
        self.chatBox.newServerMessage(text)

    def endInput(self):
        if self.input:
            self.elements.remove(self.input)
            self.input = None
        if self.inputText:
            self.elements.remove(self.inputText)
            self.inputText = None
        if self.unobtrusiveGetter:
            self.elements.remove(self.unobtrusiveGetter)
            self.unobtrusiveGetter = None
        if (self.menuManager is not None and self.menuManager not in
                self.elements):
            self.elements.append(self.menuManager)
        self.input = self.inputText = None


    def inputStarted(self):
        self.elements.append(self.input)
        self.elements.append(self.inputText)
        self.input.onEsc.addListener(lambda sender: self.endInput())
        self.input.onEnter.addListener(lambda sender: self.endInput())
        if self.menuManager is not None:
            try:
                self.elements.remove(self.menuManager)
            except ValueError:
                pass

    def chat(self):
        if not self.player:
            return

        if self.chatBox.isOpen():
            self.chatBox.close()
        else:
            pygame.key.set_repeat(300, 30)
            self.chatBox.open()
            self.chatBox.setPlayer(self.player)

    def abandon(self, player):
        '''
        Called when a player says they wish to abandon their upgrade.
        '''
        if player.upgrade:
            addOn = 'upgrade'
            if type(player.upgrade) == Grenade:
                self.newMessage('Cannot abandon an active grenade!',
                        self.app.theme.colours.errorMessageColour)
                return
        else:
            return

        message = 'Really abandon your ' + addOn + ' (Y/N)'
        self.endInput()
        self.unobtrusiveGetter = YesNoGetter(self.app, Location(
                FullScreenAttachedPoint((0,0), 'center'), 'center'), message,
                self.app.screenManager.fonts.unobtrusivePromptFont,
                self.app.theme.colours.unobtrusivePromptColour, 3)
        self.elements.append(self.unobtrusiveGetter)

        def gotValue(abandon):
            if self.unobtrusiveGetter:
                self.elements.remove(self.unobtrusiveGetter)
                self.unobtrusiveGetter = None
            if abandon:
                self.controller.send(DeleteUpgradeMsg(player.id,
                        player.upgrade.upgradeType, 'A'))

        self.unobtrusiveGetter.onGotValue.addListener(gotValue)


    def upgradeUsed(self, player):
        upgrade = player.upgrade
        if upgrade is None:
            upgrade = 'an upgrade'
        else:
            upgrade = str(upgrade)

        if type(player.upgrade) == Grenade:
            message = '%s has thrown a %s' % (player.nick, player.upgrade)
        elif type(player.upgrade) in [Ninja, Turret]:
            message = '%s has become a %s' % (player.nick, player.upgrade)
        elif type(player.upgrade) == Directatorship:
            message = '%s has become a Directator' % player.nick
        elif type(player.upgrade) in [Ricochet, Shoxwave]:
            message = '%s is using %s' % (player.nick, player.upgrade)
        else:
            message = '%s is using a %s' % (player.nick, player.upgrade)

        self.newMessage(message)

    def upgradeDestroyed(self, player, upgrade):
        if upgrade is None:
            upgrade = 'upgrade'
        else:
            upgrade = str(upgrade)
        message = "%s's %s is gone" % (player.nick, upgrade)
        self.newMessage(message)

    def showPlayerDetails(self):
        self.gameInterface.gameViewer.toggleLeaderBoard()

    def toggleInterface(self):
        self.gameInterface.gameViewer.toggleInterface()

class UpgradeDisplay(framework.CompoundElement):

    def __init__(self, app):
        super(UpgradeDisplay, self).__init__(app)

    def setUpgrade(self, upgradeType, player):
        if player is None or upgradeType is None:
            self.elements = []
        else:
            pos = Location(Canvas(620, 0), "midtop")
            image = self.app.theme.sprites.upgradeImage(upgradeType)
            area = Area(
                    Canvas(620, 68),
                    #FullScreenAttachedPoint(ScaledSize(620, 20), 'topleft'),
                    ScaledSize(50, 10), 'midbottom')
            self.elements = [
                PictureElement(self.app, image, pos),
                StarGauge(self.app, area, player, upgradeType)
            ]
