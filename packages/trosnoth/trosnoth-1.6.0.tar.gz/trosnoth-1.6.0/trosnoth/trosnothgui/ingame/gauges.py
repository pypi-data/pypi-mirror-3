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

from trosnoth.gui.framework import framework
from trosnoth.model.universe_base import GameState
from trosnoth.utils.utils import timeNow
import pygame

class GaugeBase(framework.Element):
    def __init__(self, app, area):
        super(GaugeBase, self).__init__(app)
        self.area = area

    def draw(self, surface):
        rect = self.area.getRect(self.app)
        pos = rect.topleft
        ratio = min(1, max(0, self.getRatio()))
        amount = int(ratio * rect.width)

        backColour = self.getBackColour()
        if backColour != None:
            backRect = pygame.rect.Rect(pos[0] + amount, pos[1],
                    rect.width - amount + 1, rect.height)
            surface.fill(backColour, backRect)

        if amount > 0:
            insideRect = pygame.rect.Rect(pos, (amount, rect.height))
            surface.fill(self.getForeColour(), insideRect)

        # Draw the border on top
        pygame.draw.rect(surface, self.app.theme.colours.gaugeBorder, rect, 2)

        icon = self.getIcon()
        if icon is not None:
            r = icon.get_rect()
            r.center = rect.midleft
            r.left -= r.width // 5
            a = icon.get_alpha()
            icon.set_alpha(160)
            surface.blit(icon, r)
            icon.set_alpha(a)

    def getRatio(self):
        '''
        Return a number as a proportion (0..1) of how complete
        this box is. To be implemented in subclasses
        '''
        raise NotImplementedError

    def getForeColour(self):
        '''
        Return the foreground colour that this gauge should be.
        To be implemented in subclasses
        '''
        raise NotImplementedError

    def getBackColour(self):
        '''
        Return the background colour that this gauge should be.
        None = blank
        To be implemented in subclasses
        '''
        return None

    def getIcon(self):
        return None

class RespawnGauge(GaugeBase):
    '''Represents a graphical gauge to show how close to respawning a player
    is.'''
    def __init__(self, app, area, player, gameController):
        super(RespawnGauge, self).__init__(app, area)
        self.player = player
        self.gameController = gameController

    def getRatio(self):
        if self.gameController.state() == GameState.Starting:
            secondsUntilGameStarts = self.gameController._gameStartingAt - timeNow()
            return 1 - (secondsUntilGameStarts /
                        self.gameController._gameStartDelay)
        else:
            return 1 - (self.player.respawnGauge /
                    self.player.universe.physics.playerRespawnTotal)

    def getForeColour(self):
        if self.getRatio() >= 1:
            return self.app.theme.colours.gaugeGood
        else:
            return self.app.theme.colours.gaugeBad

    def getIcon(self):
        return self.app.theme.sprites.ghostIcon(self.player.team).getImage()

class TurretGauge(GaugeBase):
    '''Represents a graphical gauge to show the overheatedness of a turret'''
    def __init__(self, app, area, player):
        super(TurretGauge, self).__init__(app, area)
        self.player = player

    def getRatio(self):
        return (self.player.turretHeat /
                self.player.universe.physics.playerTurretHeatCapacity)

    def getForeColour(self):
        if self.player.turretOverHeated:
            return self.app.theme.colours.gaugeBad
        elif self.getRatio() > 0.5:
            return self.app.theme.colours.gaugeWarn
        else:
            return self.app.theme.colours.gaugeGood

    def getIcon(self):
        return self.app.theme.sprites.turretBase.getImage()

class GunGauge(GaugeBase):
    player = None

    def getRatio(self):
        player = self.player
        if player is None:
            return 0

        if player.machineGunner and player.mgBulletsRemaining > 0:
            return player.mgBulletsRemaining / 15.

        if player.reloadTime > 0:
            return 1 - player.reloadTime / (player.reloadFrom + 0.)

        return 1

    def getForeColour(self):
        player = self.player
        if player.machineGunner and player.mgBulletsRemaining > 0:
            return self.app.theme.colours.gaugeGood
        if player is None or player.reloadTime > 0:
            return self.app.theme.colours.gaugeBad
        return self.app.theme.colours.gaugeGood

    def getIcon(self):
        return self.app.theme.sprites.gunIcon.getImage()

class UpgradeGauge(GaugeBase):
    '''Represents a graphical gauge to show how much time a player has left
    to use their upgrade.'''
    def __init__(self, app, area, player):
        super(UpgradeGauge, self).__init__(app, area)
        self.player = player

    def getRatio(self):
        if self.player.upgradeTotal == 0:
            return 1
        return self.player.upgradeGauge / self.player.upgradeTotal

    def getForeColour(self):
        return self.app.theme.colours.gaugeGood

    def getIcon(self):
        return self.app.theme.sprites.upgradeImage(type(self.player.upgrade))

class StarGauge(GaugeBase):
    '''
    Shows how your teams stars are going compared to the number required for the
    selected upgrade.
    '''

    def __init__(self, app, area, player, upgrade):
        super(StarGauge, self).__init__(app, area)
        self.player = player
        self.upgrade = upgrade

    def getRatio(self):
        if self.upgrade.requiredStars == 0:
            return 1
        return self.player.getTeamStars() / (self.upgrade.requiredStars + 0.)

    def getForeColour(self):
        if self.getRatio() < 1:
            return self.app.theme.colours.gaugeBad
        return self.app.theme.colours.gaugeGood

