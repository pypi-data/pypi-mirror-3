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

from trosnoth.utils.checkpoint import checkpoint
from trosnoth.model.map import MapLayout
from trosnoth.messages import RemoveCollectableStarMsg, ShotAbsorbedMsg
from trosnoth.model.unit import Unit

log = logging.getLogger('star')

class CollectableStar(Unit):
    # The following values control star movement.
    maxFallVel = 540            # pix/s
    gravity = 1000 #3672              # pix/s/s
    initVel = 480

    HALF_WIDTH = 5
    HALF_HEIGHT = 5

    def __init__(self, universe, id, pos, team):
        Unit.__init__(self)
        self.universe = universe
        self.id = id
        self.team = team
        self.creationTime = self.universe.getElapsedTime()
        self.registeredHit = False

        # Place myself.
        self.pos = pos
        self.xVel = 0
        self.yVel = 0

        i, j = MapLayout.getMapBlockIndices(*pos)

        self.setMapBlock(self.universe.zoneBlocks[i][j])
        checkpoint('Collectable star created')

    def delete(self):
        self.universe.removeCollectableStar(self)

    def isSolid(self):
        return True

    def setMapBlock(self, block):
        if block == self.currentMapBlock:
            return
        if self.currentMapBlock is not None:
            self.currentMapBlock.removeCollectableStar(self)
        Unit.setMapBlock(self, block)
        block.addCollectableStar(self)

    def checkCollisions(self, deltaX, deltaY):
        if self.universe.clientOptimised:
            return
        block = self.currentMapBlock
        for player in block.players:
            if not player.ghost:
                if block.collideTrajectory(player.pos, self.pos,
                        (deltaX, deltaY), 30):
                    self.collectedBy(player)
                    return
        for shot in list(block.shots):
            if self.team is None or shot.team != self.team:
                if block.collideTrajectory(shot.pos, self.pos, (deltaX,
                        deltaY), 15):
                    self.collectedBy(shot.originatingPlayer, shot)

    def collectedBy(self, player, shot=None):
        if not self.registeredHit:
            self.universe.eventPlug.send(RemoveCollectableStarMsg(self.id,
                    player.id))
            self.registeredHit = True
            if shot is not None:
                self.universe.eventPlug.send(ShotAbsorbedMsg('\x00',
                        player.id, shot.id))

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
            vFinal = self.yVel + self.gravity * deltaT
            if vFinal > self.maxFallVel:
                # Hit terminal velocity. Fall has two sections.
                deltaY = (deltaY + (self.maxFallVel ** 2 - self.yVel ** 2) /
                        (2 * self.gravity) + self.maxFallVel * (deltaT -
                        (self.maxFallVel - self.yVel) / self.gravity))
                self.yVel = self.maxFallVel
            else:
                # Simple case: s=ut+0.5at**2
                deltaY = (deltaY + self.yVel * deltaT + 0.5 * self.gravity *
                        deltaT ** 2)
                self.yVel = vFinal

        except Exception, e:
            log.exception(str(e))

    def requestRebound(self, obstacle):
        obsAngle = obstacle.getAngle()
        shotAngle = atan2(self.yVel, self.xVel)
        dif = shotAngle - obsAngle
        final = obsAngle - dif
        speed = sqrt(self.xVel ** 2 + self.yVel **2) * 0.9
        xVel = speed * cos(final)
        yVel = speed * sin(final)
        self.universe.sendStarRebound(self, xVel, yVel)

    def gotRebound(self, msg):
        self.pos = msg.xpos, msg.ypos
        self.xVel = msg.xvel
        self.yVel = msg.yvel