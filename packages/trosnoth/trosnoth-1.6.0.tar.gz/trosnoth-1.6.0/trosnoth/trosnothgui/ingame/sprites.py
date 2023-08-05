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
import datetime
import pygame

from trosnoth.gui.framework.basics import (AngledImageCollection, Animation,
        SingleImage)
from trosnoth.model.player import Player
from trosnoth.trosnothgui.ingame.nametag import NameTag, StarTally
from trosnoth.utils.utils import timeNow

class ShotSprite(pygame.sprite.Sprite):
    def __init__(self, app, shot):
        super(ShotSprite, self).__init__()
        self.app = app
        self.shot = shot
        self.shotAnimation = app.theme.sprites.shotAnimation(shot.team)
        # Need a starting one:
        self.image = self.shotAnimation.getImage()
        self.rect = self.image.get_rect()

    def update(self):
        self.image = self.shotAnimation.getImage()

    @property
    def pos(self):
        return self.shot.pos

class ExplosionSprite(pygame.sprite.Sprite):
    def __init__(self, app, pos):
        super(ExplosionSprite, self).__init__()
        self.app = app
        self.pos = pos
        self.animation = app.theme.sprites.explosion()
        self.image = self.animation.getImage()
        self.rect = self.image.get_rect()

    def update(self):
        self.image = self.animation.getImage()

    def isDead(self):
        return self.animation.isComplete()

class ShoxwaveExplosionSprite(pygame.sprite.Sprite):
    def __init__(self, app, pos):
        super(ShoxwaveExplosionSprite, self).__init__()
        self.app = app
        self.pos = pos
        self.animation = app.theme.sprites.shoxwaveExplosion()
        self.image = self.animation.getImage()
        self.rect = self.image.get_rect()

    def update(self):
        self.image = self.animation.getImage()

    def isDead(self):
        return self.animation.isComplete()

class GrenadeSprite(pygame.sprite.Sprite):
    def __init__(self, app, grenade):
        super(GrenadeSprite, self).__init__()
        self.grenade = grenade
        self.image = app.theme.sprites.teamGrenade(grenade.player.team)
        self.rect = self.image.get_rect()

    @property
    def pos(self):
        return self.grenade.pos

class CollectableStarSprite(pygame.sprite.Sprite):
    def __init__(self, app, star):
        super(CollectableStarSprite, self).__init__()
        self.star = star
        self.image = app.theme.sprites.collectableStar(star.team)
        self.rect = self.image.get_rect()

    @property
    def pos(self):
        return self.star.pos

class PlayerSprite(pygame.sprite.Sprite):
    # These parameters are used to create a canvas for the player sprite object.
    canvasSize = (33, 39)
    colourKey = (255, 255, 255)
    liveOffset = 3
    ghostOffset = 0
    def __init__(self, app, worldGUI, player):
        super(PlayerSprite, self).__init__()
        self.app = app
        self.worldGUI = worldGUI
        self.spriteTeam = player.team
        self.player = player
        self.nametag = NameTag(app, player.nick)
        self._oldName = player.nick
        self.starTally = StarTally(app, 0)

        sprites = app.theme.sprites
        self.gunImages = AngledImageCollection(self.getAngleFacing,
                *sprites.gunImages(self.player.team))
        self.machineGunImages = AngledImageCollection(self.getAngleFacing,
                *sprites.machineGunImages(self.player.team))
        self.ricoGunImages = AngledImageCollection(self.getAngleFacing,
                *sprites.ricoGunImages(self.player.team))
        self.shoxGunImages = SingleImage(sprites.shoxGun3)

        head = sprites.playerHead(self.player.team, self.player.bot)
        self.runningAnimation = [
            Animation(0.1, self.player.universe.getElapsedTime,
                *sprites.runningLegs),
            sprites.playerBody,
            head,
        ]
        self.ghostAnimation = sprites.ghostAnimation(self.player.team)

        self.reversingAnimation = [
            sprites.playerBody,
            Animation(0.1, self.player.universe.getElapsedTime,
                    *sprites.backwardsLegs),
            head,
        ]

        self.turretAnimation = [
            sprites.turretBase,
            sprites.playerBody,
            head,
        ]

        self.standingAnimation = [
            sprites.playerStanding,
            sprites.playerBody,
            head,
        ]

        self.jumpingAnimation = [
            sprites.playerJumping,
            sprites.playerBody,
            head,
        ]
        self.holdingAnimation = [
            sprites.playerBody,
            sprites.playerHolding(self.player.team),
            head,
        ]
        self.fallingAnimation = self.jumpingAnimation
        self.shieldAnimation = Animation(0.15,
                self.player.universe.getElapsedTime, *sprites.shieldImages)
        self.phaseShiftAnimation = Animation(0.15, timeNow,
                *sprites.phaseShiftImages)
        self.jammingHat = app.theme.sprites.jammingHat()

        self.image = pygame.Surface(self.canvasSize)
        self.image.set_colorkey(self.colourKey)
        self.rect = self.image.get_rect()

        # This probably shouldn't be done here.
        _t = datetime.date.today()
        self.is_christmas = _t.day in (24, 25, 26) and _t.month == 12

    @property
    def pos(self):
        return self.player.pos

    def getAngleFacing(self):
        return self.player.angleFacing

    @property
    def angleFacing(self):
        return self.player.angleFacing

    def __getattr__(self, attr):
        '''
        Proxy attributes through to the underlying player class.
        '''
        return getattr(self.player, attr)

    def update(self):
        if self.player.nick != self._oldName:
            self._oldName = self.player.nick
            self.nametag = NameTag(self.app, self.player.nick)

        self.setImage(self._isMoving(), self._isSlow())

    def _isMoving(self):
        return not (self.player._state['left'] or self.player._state['right'])

    def _isSlow(self):
        # Consider horizontal movement of player.
        if self.player._state['left'] and not self.player._state['right']:
            if self.player._faceRight:
                return True
            else:
                return False
        elif self.player._state['right'] and not self.player._state['left']:
            if self.player._faceRight:
                return False
            else:
                return True
        return False

    def setImage(self, moving, slow):
        flip = None
        offset = self.liveOffset
        if self.player.ghost:
            blitImages = self.ghostAnimation
            offset = self.ghostOffset
        elif self.player.turret:
            blitImages = self.turretAnimation
        elif self.player.isAttachedToWall():
            blitImages = self.holdingAnimation
            if self.player.isAttachedToWall() == 'right':
                flip = False
            else:
                flip = True
        elif self.player.isOnGround():
            if not moving == 0:
                blitImages = self.standingAnimation
            elif slow:
                blitImages = self.reversingAnimation
            else:
                blitImages = self.runningAnimation
        else:
            if self.player.yVel > 0:
                blitImages = self.fallingAnimation
            else:
                blitImages = self.jumpingAnimation
        self.image.fill(self.image.get_colorkey())
        # Put the pieces together:
        for element in blitImages:
            self.image.blit(element.getImage(), (offset, 0))
        if not (self.player.ghost or self.player.isAttachedToWall()):
            if self.player.machineGunner:
                weapon = self.machineGunImages
            elif self.player.hasRicochet:
                weapon = self.ricoGunImages
            elif self.player.shoxwave:
                weapon = self.shoxGunImages
            else:
                weapon = self.gunImages
            self.image.blit(weapon.getImage(), (offset, 0))
        if (self.player.phaseshift and self._canSeePhaseShift() and not
                self.app.displaySettings.useAlpha):
            self.image.blit(self.phaseShiftAnimation.getImage(), (offset, 0))
        elif self.player.ninja:
            self.image.blit(self.app.theme.sprites.ninjaHead.getImage(),
                    (offset, 0))
        elif self.player.disruptive:
            self.image.blit(self.jammingHat.getImage(), (offset, 0))
        if self.player.hasElephant() and not self.player.ghost:
            self.image.blit(self.app.theme.sprites.elephant.getImage(),
                    (offset, 0))
        if (not self.player.ghost and not self.player.phaseshift and not
                self.player.ninja and self.is_christmas and not
                self.player.hasElephant()):
            self.image.blit(self.app.theme.sprites.christmasHat.getImage(),
                    (offset, 0))
        if not self.player._faceRight and flip == None or flip:
            self.image = pygame.transform.flip(self.image, True, False)
        if self.player.shielded:
            img = self.shieldAnimation.getImage()
            img.set_alpha(128)
            self.image.blit(img, (offset, 0))
        # Flicker the sprite between different levels of transparency
        if self.app.displaySettings.useAlpha:
            if self.player.phaseshift and self._canSeePhaseShift():
                self.image.set_alpha(random.randint(30, 150))
            elif self.player.ghost:
                self.image.set_alpha(128)
            elif self.player.isInvulnerable():
                self.image.set_alpha(random.randint(30, 150))
            elif self.player.invisible:
                if self.player.isFriendsWith(self.shownPlayer):
                    self.image.set_alpha(80)
                else:
                    self.image.set_alpha(0)
            else:
                self.image.set_alpha(255)
        else:
            self.image.set_alpha(255)

    @property
    def shownPlayer(self):
        return self.worldGUI.gameViewer.viewManager.target

    def _canSeePhaseShift(self):
        target = self.shownPlayer
        if not isinstance(target, Player):
            return False
        return self.player.isFriendsWith(target)
