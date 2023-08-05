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

from math import pi
import random

from trosnoth.ai import AI
from trosnoth.utils.twist import WeakCallLater, WeakLoopingCall

class SimpleAI(AI):
    '''
    An example of a simple AI which runs around randomly and shoots at the
    nearest enemy.
    '''
    nick = 'SimpleAI'
    playable = True

    def start(self):
        self._pauseTimer = None
        self._loop = WeakLoopingCall(self, 'tick')
        self._loop.start(0.5)

    def disable(self):
        self._loop.stop()
        if self._pauseTimer is not None:
            self._pauseTimer.cancel()

    def tick(self):
        if self.player.dead:
            if self.player.inRespawnableZone():
                self.doAimAt(0, thrust=0)
                if self.player.respawnGauge == 0:
                    self.doRespawn()
            else:
                self.aimAtFriendlyZone()
        else:
            if self._pauseTimer is None:
                self.startPlayerMoving()
            if self.player.canShoot():
                self.fireAtNearestEnemy()

    def aimAtFriendlyZone(self):
        zones = [z for z in self.world.zones if z.orbOwner == self.player.team]
        if len(zones) == 0:
            return

        def getZoneDistance(zone):
            x1, y1 = self.player.pos
            x2, y2 = zone.defn.pos
            return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

        bestZone = min(zones, key=getZoneDistance)
        self.doAimAtPoint(bestZone.defn.pos)

    def fireAtNearestEnemy(self):
        enemies = [p for p in self.world.players if not
                (p.dead or p.invisible or self.player.isFriendsWith(p))]
        if len(enemies) == 0:
            return

        def getPlayerDistance(p):
            x1, y1 = self.player.pos
            x2, y2 = p.pos
            return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

        nearestEnemy = min(enemies, key=getPlayerDistance)
        if getPlayerDistance(nearestEnemy) < 512:
            self.doAimAtPoint(nearestEnemy.pos)
            self.doShoot()

    def died(self, killerId):
        self._pauseTimer = None
        self.doStop()
        self.aimAtFriendlyZone()

    def respawned(self):
        self.startPlayerMoving()

    def startPlayerMoving(self):
        self.pauseAndReconsider()

    def pauseAndReconsider(self):
        if self.player.dead:
            self._pauseTimer = None
            return

        # Pause again in between 0.5 and 2.5 seconds time.
        t = random.random() * 2 + 0.5
        self._pauseTimer = WeakCallLater(t, self, 'pauseAndReconsider')

        # Decide whether to jump or drop.
        if self.player.isAttachedToWall():
            verticalActions = ['none', 'jump', 'drop']
        elif self.player.isOnPlatform():
            verticalActions = ['none', 'jump', 'drop']
        elif self.player.isOnGround():
            verticalActions = ['none', 'jump']
        else:
            verticalActions = ['none']
        action = random.choice(verticalActions)
        if action == 'jump':
            self.doJump()
        elif action == 'drop':
            self.doDrop()

        # Decide on a direction.
        d = random.choice(['left', 'right', 'stop'])
        if d == 'left':
            self.doAimAt(-pi/2.)
            self.doMoveLeft()
        elif d == 'right':
            self.doAimAt(pi/2.)
            self.doMoveRight()
        else:
            self.doStop()

AIClass = SimpleAI
