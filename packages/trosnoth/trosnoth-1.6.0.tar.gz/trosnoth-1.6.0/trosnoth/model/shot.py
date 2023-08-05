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
from math import sin, cos, atan2, sqrt

from trosnoth.model.unit import Unit
from trosnoth.utils.checkpoint import checkpoint

log = logging.getLogger('shot')

class GrenadeShot(Unit):
    '''
    This will make the grenade have the same physics as a player without
    control and features of player movement
    '''

    HALF_WIDTH = 5
    HALF_HEIGHT = 5

    def __init__(self, universe, player):
        Unit.__init__(self)
        self.universe = universe
        self.player = player
        self.registeredHit = False

        # Place myself.
        self.pos = player.pos
        angle = player.angleFacing
        self.xVel = self.universe.physics.grenadeInitVel * sin(angle)
        self.yVel = -self.universe.physics.grenadeInitVel * cos(angle)

        try:
            block = player.currentMapBlock
        except IndexError, e:
            log.exception(str(e))
            self.kill()
            return
        self.setMapBlock(block)
        checkpoint('Grenade created')

    def isSolid(self):
        return True

    def setMapBlock(self, block):
        if block == self.currentMapBlock:
            return
        if self.currentMapBlock is not None:
            self.currentMapBlock.removeGrenade(self)
        Unit.setMapBlock(self, block)
        block.addGrenade(self)

    def update(self, deltaT):
        '''Called by this player's universe when this player should update
        its position. deltaT is the time that's passed since its state was
        current, measured in seconds.'''

        try:
            deltaX = self.xVel * deltaT
            deltaY = self.yVel * deltaT

            obstacle = self.universe.physics.moveUnit(self, deltaX, deltaY)
            if obstacle is not None:
                self.requestRebound(obstacle)

            # v = u + at
            vFinal = self.yVel + self.universe.physics.grenadeGravity * deltaT
            if vFinal > self.universe.physics.grenadeMaxFallVel:
                # Hit terminal velocity. Fall has two sections.
                deltaY = (deltaY + (self.universe.physics.grenadeMaxFallVel ** 2
                        - self.yVel ** 2) / (2 *
                        self.universe.physics.grenadeGravity) +
                        self.universe.physics.grenadeMaxFallVel * (deltaT -
                        (self.universe.physics.grenadeMaxFallVel - self.yVel) /
                        self.universe.physics.grenadeGravity))
                self.yVel = self.universe.physics.grenadeMaxFallVel
            else:
                # Simple case: s=ut+0.5at**2
                deltaY = (deltaY + self.yVel * deltaT + 0.5 *
                        self.universe.physics.grenadeGravity * deltaT ** 2)
                self.yVel = vFinal

        except Exception, e:
            log.exception(str(e))

    def requestRebound(self, obstacle):
        '''
        The grenade has hit an obstacle
        '''
        obsAngle = obstacle.getAngle()
        shotAngle = atan2(self.yVel, self.xVel)
        dif = shotAngle - obsAngle
        final = obsAngle - dif
        speed = sqrt(self.xVel ** 2 + self.yVel **2) * 0.9
        xVel = speed * cos(final)
        yVel = speed * sin(final)
        self.universe.sendGrenadeRebound(self.player, self.pos, xVel, yVel)

    def doRebound(self, reboundMessage):
        self.pos = (reboundMessage.xpos, reboundMessage.ypos)
        self.xVel = reboundMessage.xvel
        self.yVel = reboundMessage.yvel


class Shot(Unit):

    NORMAL = 'normal'
    TURRET = 'turret'
    RICOCHET = 'ricochet'

    LIFETIME = 1.     # s

    HALF_WIDTH = 5
    HALF_HEIGHT = 5

    def __init__(self, world, id, team, player, pos, velocity, kind, lifetime,
            mapBlock):
        Unit.__init__(self)

        self.world = world
        self.id = id
        self.team = team
        self.pos = tuple(pos)
        self.originatingPlayer = player
        self.vel = tuple(velocity)
        self.timeLeft = lifetime
        self.kind = kind
        self.bounced = False

        self.setMapBlock(mapBlock)

        checkpoint('Shot created')

    def isSolid(self):
        return self.kind != Shot.TURRET

    def checkCollisions(self, deltaX, deltaY):
        if self.world.clientOptimised:
            return
        block = self.currentMapBlock
        for player in block.players:
            if not player.isFriendsWith(self.originatingPlayer):
                if block.collideTrajectory(player.pos, self.pos,
                        (deltaX, deltaY), 20):
                    block.shotHitPlayer(self, player)

    def reset(self):
        self.registeredHit = False

    def setMapBlock(self, block):
        if block == self.currentMapBlock:
            return
        if self.currentMapBlock is not None:
            self.currentMapBlock.removeShot(self)
        Unit.setMapBlock(self, block)
        block.addShot(self)

    def update(self, deltaT):
        '''Called by the universe when this shot should update its position.
        deltaT is the time that's passed since its state was current, measured
        in seconds.'''
        # Shots have a finite lifetime.
        self.timeLeft = self.timeLeft - deltaT
        if self.timeLeft <= 0:
            self.world.shotExpired(self)
            return

        dX, dY = self.vel[0] * deltaT, self.vel[1] * deltaT
        obstacle = self.world.physics.moveUnit(self, dX, dY)

        if obstacle is not None:
            # Shot hit an obstacle.
            if self.kind == Shot.RICOCHET:
                self.rebound(obstacle)
            else:
                self.world.shotExpired(self)
                return

    def rebound(self, obstacle):
        '''
        Shot is a ricochet shot and it's hit an obstacle.
        '''
        self.bounced = True
        obsAngle = obstacle.getAngle()
        shotAngle = atan2(self.vel[1], self.vel[0])
        dif=shotAngle -obsAngle
        final = obsAngle - dif
        speed = sqrt(self.vel[0]*self.vel[0] + self.vel[1]*self.vel[1])
        self.vel = (speed*cos(final), speed*sin(final))

