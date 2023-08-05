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

from math import pi, atan2
import random

from trosnoth.model.universe import Abort
from trosnoth.utils.math import distance
from trosnoth.ai import AI
from trosnoth.utils.twist import WeakCallLater

class AlphaAI(AI):
    nick = 'AlphaAI'
    playable = True

    def start(self):
        self.xdir = 'left'
        self.dead = True

        self.clRespawn = None
        self.clChangeXDir = None
        self.clJump = None
        self.clDrop = None
        self.clShoot = None

        self._launchDeadCallLaters(0)

    def disable(self):
        for cl in (self.clRespawn, self.clChangeXDir, self.clJump, self.clDrop,
                self.clShoot):
            if cl:
                cl.cancel()

    def _launchAliveCallLaters(self):
        self._cancelAliveCallLaters()
        self.clChangeXDir = WeakCallLater(0, self, 'changeXDir')
        self.clJump = WeakCallLater(0, self, 'jumpAgain')
        self.clDrop = WeakCallLater(0, self, 'drop')
        self.clShoot = WeakCallLater(0, self, 'shoot')

    def _cancelAliveCallLaters(self):
        if self.clChangeXDir is not None and self.clChangeXDir.active():
            self.clChangeXDir.cancel()
            self.clChangeXDir = None
        if self.clJump is not None and self.clJump.active():
            self.clJump.cancel()
            self.clJump = None
        if self.clDrop is not None and self.clDrop.active():
            self.clDrop.cancel()
            self.clDrop = None
        if self.clShoot is not None and self.clShoot.active():
            self.clShoot.cancel()
            self.clShoot = None

    def _launchDeadCallLaters(self, respawnTime=None):
        if respawnTime == None:
            respawnTime = self.player.respawnGauge
        self._cancelDeadCallLaters()
        self.clRespawn = WeakCallLater(respawnTime, self, 'tryRespawn')

    def _cancelDeadCallLaters(self):
        if self.clRespawn is not None:
            self.clRespawn.cancel()
            self.clRespawn = None

    def died(self, killerId):
        self.dead = True
        self._cancelAliveCallLaters()
        self._launchDeadCallLaters()
        self.aimAtActionZone()

    def respawned(self):
        self.dead = False
        self._cancelDeadCallLaters()
        self._launchAliveCallLaters()

    def aimAtNearestFriendlyZone(self, time = None):
        if time == None:
            time = self.player.respawnGauge
        nearest = None
        for zone in self.world.zones:
            if zone.orbOwner == self.player.team:
                if nearest == None or (distance(zone.defn.pos, self.player.pos)
                        < distance(self.player.pos, nearest.defn.pos)):
                    nearest = zone
        if nearest == None:
            # Stop moving
            self.aimAtPoint(self.player.pos, time)
        else:
            self.aimAtPoint(nearest.defn.pos, time)

    def aimAtActionZone(self, time = None):
        if time == None:
            time = self.player.respawnGauge
        zone = self.getBestRespawnZone()

        self.aimAtPoint(zone.defn.pos, time)

    def getBestRespawnZone(self):
        best, score = None, -1000
        for zone in self.world.zones:
            thisScore = self.getRespawnScore(zone)

            if thisScore > score:
                best, score = zone, thisScore
        return best

    def getRespawnScore(self, zone):
        thisScore = 0
        threat = False
        try:
            team = self.player.team
        except Abort:
            return 0
        if zone.orbOwner == team:
            for adjDef, open in zone.defn.zones_AdjInfo():
                adj = self.world.zoneWithDef[adjDef]
                # Find boundary zone.
                if adj.isNeutral():
                    if open:
                        thisScore += 3
                elif adj.orbOwner != team:
                    threat = True
                    if open:
                        thisScore += 5
                if open:
                    # Add 2 points for each unmarked enemy in an open, adjacent
                    # zone
                    thisScore += self.numUnmarkedEnemies(adj) * 2
            if threat == False:
                # No threat, since no enemy adjacent zones
                return thisScore
            else:
                thisScore += 5

            # And 20 points for each unmarked enemy in this zone
            thisScore += self.numUnmarkedEnemies(zone) * 20
        return thisScore

    def numUnmarkedEnemies(self, zone):
        score = 0
        for player in zone.players:
            if player.team == self.player.team:
                score -= 1
            else:
                score += 1
        return max(score, 0)

    def aimAtNearestEnemy(self):
        nearest = None
        thisPlayer = self.player
        for player in self.world.players:
            if (not player.isFriendsWith(thisPlayer) and not player.ghost and
                    not player.turret and not player.invisible):
                if nearest == None or (distance(player.pos, thisPlayer.pos) <
                        distance(thisPlayer.pos, nearest.pos)):
                    nearest = player
        if nearest is not None:
            # Add uncertainty
            pos = (nearest.pos[0] + (random.random() * 80 - 40),
                   nearest.pos[1] + (random.random() * 80 - 40))
            self.aimAtPoint(pos)

    def aimAtPoint(self, pos, timeLeft = None):
        dx = pos[0] - self.player.pos[0]
        dy = pos[1] - self.player.pos[1]
        theta = atan2(dx, -dy)
        thrust = 1.0
        if timeLeft is not None:
            dist = (dx ** 2 + dy ** 2) ** 0.5
            maxSpeed = self.world.physics.playerMaxGhostVel
            if timeLeft <= 0:
                speedReq = maxSpeed
            else:
                speedReq = dist / timeLeft

            if speedReq < maxSpeed:
                thrust = speedReq / maxSpeed
        self.doAimAt(theta, thrust)

    def tryRespawn(self):
        if self.dead:
            self.aimAtActionZone()
            self.clRespawn = WeakCallLater(0.5, self, 'tryRespawn')
            self.doRespawn()

    def changeXDir(self):
        t = random.random() * 5 + 3
        self.clChangeXDir = WeakCallLater(t, self, 'changeXDir')
        if self.xdir == 'left':
            self.xdir = 'right'
            self.doAimAt(pi/2.)
            self.doMoveRight()
        else:
            self.xdir = 'left'
            self.doAimAt(-pi/2.)
            self.doMoveLeft()

    def drop(self):
        self.clDrop = WeakCallLater(random.random() * 3 + 1.5, self, 'drop')
        self.doDrop()

    def jumpAgain(self):
        self.clJump = WeakCallLater(random.random() * 0.5 + 0.5, self,
                'stopJump')
        self.doJump()

    def stopJump(self):
        self.clJump = WeakCallLater(random.random() * 1.5, self, 'jumpAgain')
        self.doStopJump()

    def shoot(self):
        self.clShoot = WeakCallLater(random.random() * .5 + .4, self, 'shoot')
        self.aimAtNearestEnemy()
        self.doShoot()

    def zoneTagged(self, zoneId, playerId):
        # In case our zone was tagged
        self.aimAtActionZone()

AIClass = AlphaAI
