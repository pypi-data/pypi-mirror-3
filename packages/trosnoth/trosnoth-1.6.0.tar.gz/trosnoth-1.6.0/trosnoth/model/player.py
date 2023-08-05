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
from math import sin, cos
import struct

from trosnoth.utils.checkpoint import checkpoint

from trosnoth.model.unit import Unit
from trosnoth.model.universe_base import NeutralTeamId, NoPlayer
from trosnoth.model.map import MapLayout
from trosnoth.utils.math import distance

from trosnoth.messages import (DeleteUpgradeMsg, PlayerUpdateMsg,
        SetPlayerTeamMsg, PlayerKilledMsg, PlayerHitMsg, ShotAbsorbedMsg,
        AchievementProgressMsg)
from trosnoth.utils.network import compress_boolean

RESPAWN_CAMP_TIME = 1.0
MAX_STARS = 10

log = logging.getLogger('player')

class Player(Unit):
    '''Maintains the state of a player. This could be the user's player, a
    player on the network, or conceivably even a bot.
    '''

    HALF_WIDTH = 10
    HALF_HEIGHT = 19

    def __init__(self, universe, nick, team, id, zone, dead=False,
            bot=False):
        Unit.__init__(self)

        self.universe = universe
        self.nick = nick
        self.user = None      # If authenticated, this will have a value.
        self.team = team
        self.id = id
        self.bot = bot
        self._state = {'left':  False,
                       'right': False,
                       'jump':  False,
                       'down': False,
                       'respawn' : False}
        self._alreadyJumped = False

        self.stars = universe.PLAYER_RESET_STARS

        # Place myself.
        self.pos = zone.defn.pos
        self._jumpTime = 0.0
        self.yVel = 0
        self.attachedObstacle = None
        self.motionState = 'fall'   # fall / ground / leftwall / rightwall
        self._unstickyWall = None
        self._ignore = None         # Used when dropping through a platform.
        self.angleFacing = 1.57
        self.ghostThrust = 1.0      # Determined by mouse position
        self._faceRight = True
        self.reloadTime = 0.0
        self.reloadFrom = 0.0
        self.turretHeat = 0.0
        self.respawnGauge = 0.0
        self.upgradeGauge = 0.0
        self.upgradeTotal = 0.0
        self.health = self.universe.physics.playerRespawnHealth
        self.ghost = dead
        # Upgrade-related
        self.upgrade = None
        self.turretOverHeated = False
        self.invulnerableUntil = None
        self.mgBulletsRemaining = 0
        self.mgFiring = False

        # Shots this player has fired
        self.shots = {}

        # Preferences during the voting phase.
        self.preferredTeam = ''
        self.prefersTournamentTeam = False
        self.readyToStart = False
        self.readyForTournament = False
        self.preferredSize = (0, 0)
        self.preferredDuration = 0

        self.currentZone = zone
        zone.addPlayer(self)

    @property
    def dead(self):
        return self.ghost

    @staticmethod
    def getObstacles(mapBlockDef):
        '''
        Return which obstacles in the given map block apply to this kind of
        unit.
        '''
        return mapBlockDef.obstacles + mapBlockDef.ledges

    @property
    def identifyingName(self):
        if self.user is None:
            return self.nick
        return self.user.username

    @property
    def shielded(self):
        return self.upgrade is not None and self.upgrade.upgradeType in 'sd'

    @property
    def phaseshift(self):
        return self.upgrade is not None and self.upgrade.upgradeType == 'h'

    @property
    def turret(self):
        return self.upgrade is not None and self.upgrade.upgradeType == 't'

    @property
    def shoxwave(self):
        return self.upgrade is not None and self.upgrade.upgradeType == 'w'

    @property
    def machineGunner(self):
        return self.upgrade is not None and self.upgrade.upgradeType in 'xd'

    @property
    def hasRicochet(self):
        return self.upgrade is not None and self.upgrade.upgradeType in 'rd'

    @property
    def ninja(self):
        return self.upgrade is not None and self.upgrade.upgradeType in 'nd'

    @property
    def disruptive(self):
        return self.upgrade is not None and self.upgrade.upgradeType == 'm'

    @property
    def invisible (self):
        return self.ninja and self.reloadTime == 0.0 and (
                self.distanceFromCenter() > 200 or
                self.isFriendsWithTeam(self.currentZone.orbOwner))

    def distanceFromCenter(self):
        zone = self.currentZone
        distanceFromOrb = distance(zone.defn.pos, self.pos)
        return distanceFromOrb

    def isAttachedToWall(self):
        '''
        Returns False if this player is not attached to a wall, otherwise
        returns 'left' or 'right' to indicate whether the wall is on the
        player's left or right.
        '''
        if self.motionState == 'leftwall':
            return 'left'
        elif self.motionState == 'rightwall':
            return 'right'
        return False

    def detachFromEverything(self):
        self.setAttachedObstacle(None)

    def isOnGround(self):
        '''
        Returns True iff this player is on the ground (whether that ground is a
        ledge or solid ground).
        '''
        return self.motionState == 'ground'

    def isOnPlatform(self):
        return self.isOnGround() and self.attachedObstacle.drop

    def isFriendsWith(self, other):
        '''
        Returns True iff self and other are on the same team.
        '''
        if other is self:
            return True
        return self.isFriendsWithTeam(other.team)

    def isFriendsWithTeam(self, team):
        if team is None:
            return False
        return self.team == team

    def inRespawnableZone(self):
        return (self.team is None or self.currentZone.orbOwner == self.team)

    @property
    def teamId(self):
        if self.team is None:
            return '\x00'
        return self.team.id

    @property
    def teamName(self):
        if self.team is None:
            return self.universe.rogueTeamName
        return self.team.teamName

    def isEnemyTeam(self, team):
        '''
        Returns True iff the given team is an enemy team of this player. It is
        not enough for the team to be neutral (None), it must actually be an
        enemy for this method to return True.
        '''
        if team is None:
            return False
        return self.team != team

    def isInvulnerable(self):
        iu = self.invulnerableUntil
        if iu is None:
            return False
        elif self.universe.getElapsedTime() > iu:
            self.invulnerableUntil = None
            return False
        return True

    def getTeamStars(self):
        if self.team is None:
            return self.stars
        return self.universe.getTeamStars(self.team)

    @property
    def isMinimapDisrupted(self):
        for team in self.universe.teams:
            if team != self.team and team.usingMinimapDisruption:
                return True
        return False

    @staticmethod
    def _leftValidator(obs):
        return obs.deltaPt[0] == 0 and obs.deltaPt[1] > 0

    @staticmethod
    def _rightValidator(obs):
        return obs.deltaPt[0] == 0 and obs.deltaPt[1] < 0

    @staticmethod
    def _groundValidator(obs):
        return obs.deltaPt[0] > 0

    def setPos(self, pos, attached):
        self.pos = pos

        # Ensure we're in the right mapBlock
        i, j = MapLayout.getMapBlockIndices(*pos)
        self.setMapBlock(self.universe.zoneBlocks[i][j])

        return
        if attached not in ('l', 'r', 'g'):
            self.setAttachedObstacle(None)
        else:
            if attached == 'l':
                deltaX, deltaY = -0.5, 0
                valid = self._leftValidator
            elif attached == 'r':
                deltaX, deltaY = 0.5, 0
                valid = self._rightValidator
            else:
                deltaX, deltaY = 0, 0.5
                valid = self._groundValidator

            lastObstacle = None
            # Check for collisions with obstacles - find the closest obstacle.
            physics = self.universe.physics
            for obstacle in physics.getNearbyObstacles(self, deltaX, deltaY):
                if self.ignoreObstacle(obstacle) or not obstacle.isObstacle:
                    continue
                if not valid(obstacle):
                    continue
                dX, dY = obstacle.collide(self, deltaX, deltaY)
                if (dX, dY) != (deltaX, deltaY):
                    # Remember the last obstacle we hit.
                    lastObstacle = obstacle
                    deltaX = dX
                    deltaY = dY
            self.setAttachedObstacle(lastObstacle)

    def __str__(self):
        return self.nick

    def getDetails(self):
        if self.id == -1:
            return {}

        pID = struct.unpack('B', self.id)[0]
        nick = self.nick
        team = self.teamId
        dead = self.ghost
        stars = self.stars
        if self.upgrade:
            upgrade = str(self.upgrade)
        else:
            upgrade = None

        return {'pID': pID,
                'nick': nick,
                'team': team,
                'dead': dead,
                'stars': stars,
                'upgrade': upgrade,
                'bot': self.bot
        }

    def removeFromGame(self):
        '''Called by network client when server says this player has left the
        game.'''
        
        if self.upgrade:
            self.upgrade.delete()

        # Remove myself from all groups I'm in.
        self.currentMapBlock.removePlayer(self)
        self.currentZone.removePlayer(self)

        # Remove all shots (otherwise we get issues looking up originating
        # player id.)
        for shot in self.shots.values():
            self.universe.removeShot(shot)

    def isSolid(self):
        return not self.ghost

    def ignoreObstacle(self, obstacle):
        return self._ignore == obstacle

    def continueOffMap(self):
        if not self.ghost:
            # Player is off the map: mercy killing.
            self.deathDetected(NoPlayer, 0, 'O')
        return False

    def canEnterZone(self, newZone):
        if newZone == self.currentZone:
            return True
        universe = self.universe
        if (not universe.state.canLeaveFriendlyTerritory()
                and newZone is None and self.ghost):
            # Pre-game ghost cannot enter purple zones.
            return False

        if (newZone is not None and
                not universe.state.canLeaveFriendlyTerritory()
                and newZone.orbOwner != self.team):
            # Disallowed zone change.
            return False

        if newZone is not None:
            self.changeZone(newZone)
        return True

    def setMapBlock(self, block):
        if block == self.currentMapBlock:
            return
        if self.currentMapBlock is not None:
            self.currentMapBlock.removePlayer(self)
        Unit.setMapBlock(self, block)
        block.addPlayer(self)

        # If we're changing blocks, we can't hold on to the same obstacle,
        # as obstacles belong to a particular mapblock.
        self.detachFromEverything()

    def checkCollisions(self, deltaX, deltaY):
        if self.universe.clientOptimised:
            return
        if not self.ghost:
            block = self.currentMapBlock
            for shot in list(block.shots):
                if not self.isFriendsWith(shot.originatingPlayer):
                    if block.collideTrajectory(shot.pos, self.pos, (deltaX,
                            deltaY), 20):
                        block.shotHitPlayer(shot, self)

    def updateState(self, key, value):
        '''Update the state of this player. State information is information
        which is needed to calculate the motion of the player. For a
        human-controlled player, this is essentially only which keys are
        pressed. Keys which define a player's state are: left, right, jump and
        down.
        Shooting is processed separately.'''

        if key == 'left' or key == 'right':
            self._unstickyWall = None

        # Ignore messages if we already know the answer.
        if self._state[key] == value:
            return
        if key == 'jump':
            self._alreadyJumped = False

        # Set the state.
        self._state[key] = value

    def processJumpState(self):
        '''
        Checks the player's jump key state to decide whether to initiate a jump
        or stop a jump.
        '''
        jumpKeyDown = self._state['jump']
        if jumpKeyDown:
            if self.motionState == 'fall':
                return
            if self._alreadyJumped:
                return

            # Otherwise, initiate the jump.
            self._jumpTime = self.universe.physics.playerMaxJumpTime
            if self.isAttachedToWall():
                self._unstickyWall = self.attachedObstacle
            self.detachFromEverything()
            self._alreadyJumped = True
        elif self._jumpTime > 0:
            # If we're jumping, cancel the jump.
            # The following line ensures that small jumps are possible
            #  while large jumps still curve.
            self.yVel = (-(1 - self._jumpTime /
                    self.universe.physics.playerMaxJumpTime) *
                    self.universe.physics.playerJumpThrust)
            self._jumpTime = 0

    def lookAt(self, angle, thrust=None):
        '''Changes the direction that the player is looking.  angle is in
        radians and is measured clockwise from the right.'''
        if thrust is not None:
            self.ghostThrust = thrust

        if self.angleFacing == angle:
            return

        self.angleFacing = angle
        self._faceRight = angle > 0

    def checkUpgrades(self, deltaT):
        # Update upgrade gauge based on Time:
        if self.upgrade and self.upgradeGauge > 0:
            self.upgradeGauge -= deltaT
            if self.upgradeGauge <= 0:
                self.upgrade.timeIsUp()
                self.universe.eventPlug.send(DeleteUpgradeMsg(self.id,
                        self.upgrade.upgradeType, 'T'))

    def updateGhost(self, deltaT):
        deltaX = (self.universe.physics.playerMaxGhostVel * deltaT *
                sin(self.angleFacing) * self.ghostThrust)
        deltaY = (-self.universe.physics.playerMaxGhostVel * deltaT *
                cos(self.angleFacing) * self.ghostThrust)

        self.universe.physics.moveUnit(self, deltaX, deltaY)

        # Update respawn gauge based on Time:
        if self.respawnGauge >= 0:
            self.respawnGauge -= deltaT
            if self.respawnGauge < 0:
                self.respawnGauge = 0

    def updateTurret(self, deltaT):
        self.reloadTime = max(0.0, self.reloadTime - deltaT)
        self.turretHeat = max(0.0, self.turretHeat - deltaT)
        if self.turretOverHeated and self.turretHeat == 0.0:
            self.turretOverHeated = False

    def getAbsVelocity(self):
        '''
        Return the absolute value of the velocity the player should have
        (assuming the player is living), given the direction that the player is
        facing and the keys (left/right) being pressed.
        '''
        # Consider horizontal movement of player.
        if self._state['left'] and not self._state['right']:
            if self._faceRight:
                return -self.universe.physics.playerSlowXVel
            return -self.universe.physics.playerXVel

        if self._state['right'] and not self._state['left']:
            if self._faceRight:
                return self.universe.physics.playerXVel
            return self.universe.physics.playerSlowXVel

        return 0

    def dropThroughFloor(self):
        checkpoint('Player: drop through ledge')
        self._ignore = self.attachedObstacle
        self.detachFromEverything()

    def dropOffWall(self):
        self._unstickyWall = self.attachedObstacle
        self.detachFromEverything()
        checkpoint('Player: drop off wall')

    def moveAlongGround(self, absVel, deltaT):
        if absVel == 0:
            return

        attachedObstacle = self.attachedObstacle
        for i in xrange(100):
            if deltaT <= 0:
                obstacle = None
                break

            oldPos = self.pos
            deltaX, deltaY = attachedObstacle.walkTrajectory(absVel, deltaT)
            nextSection, corner = attachedObstacle.checkBounds(self, deltaX,
                    deltaY)

            # Check for collisions in this path.
            obstacle = self.universe.physics.moveUnit(self, corner[0] -
                    self.pos[0], corner[1] - self.pos[1],
                    ignoreObstacles=attachedObstacle.subshape)
            if obstacle is not None:
                break
            if nextSection is None:
                obstacle = None
                self.setAttachedObstacle(None)
                break
            if nextSection == attachedObstacle:
                obstacle = None
                break

            self.attachedObstacle = attachedObstacle = nextSection
            nextSection.hitByPlayer(self)
            deltaT -= ((oldPos[0]-self.pos[0])**2 +
                    (oldPos[1]-self.pos[1])**2)**0.5 / abs(absVel)
        else:
            log.error('Very very bad thing: motion loop did not terminate '
                    'after 100 iterations')

        if obstacle:
            if obstacle.jumpable:
                if self.isOnGround() and obstacle.grabbable:
                    # Running into a vertical wall while on the ground.
                    pass
                else:
                    self.universe.playerIsDirty(self.id)
                    self.setAttachedObstacle(obstacle)
            else:
                self.setAttachedObstacle(None)
            obstacle.hitByPlayer(self)
            self.universe.playerIsDirty(self.id)

        self._ignore = None

    def setAttachedObstacle(self, obstacle):
        self.attachedObstacle = obstacle
        if obstacle is None:
            self.motionState = 'fall'
        elif obstacle.grabbable:
            if obstacle.deltaPt[1] < 0:
                self.motionState = 'rightwall'
            else:
                self.motionState = 'leftwall'
        else:
            self.motionState = 'ground'

    def calculateJumpMotion(self, absVel, deltaT):
        '''
        Returns (dx, dy, dt) where (dx, dy) is the trajectory due to the upward
        thrust of jumping, and dt is the time for which the upward thrust does
        not apply.
        '''
        deltaY = 0
        deltaX = absVel * deltaT

        # If the player is jumping, calculate how much they jump by.
        if self._jumpTime > 0:
            thrustTime = min(deltaT, self._jumpTime)
            self.yVel = -self.universe.physics.playerJumpThrust
            deltaY = thrustTime * self.yVel
            self._jumpTime = self._jumpTime - deltaT

            # Automatically switch off the jumping state if the player
            # has reached maximum time.
            if self._jumpTime <= 0:
                self._jumpTime = 0
            return deltaX, deltaY, deltaT - thrustTime
        return deltaX, deltaY, deltaT

    def getFallTrajectory(self, deltaX, deltaY, fallTime):
        # If player is falling, calculate how far they fall.

        # v = u + at
        vFinal = self.yVel + self.universe.physics.playerGravity * fallTime
        if vFinal > self.universe.physics.playerMaxFallVel:
            # Hit terminal velocity. Fall has two sections.
            deltaY = (deltaY + (self.universe.physics.playerMaxFallVel ** 2 -
                    self.yVel ** 2) / (2 * self.universe.physics.playerGravity)
                    + self.universe.physics.playerMaxFallVel * (fallTime -
                    (self.universe.physics.playerMaxFallVel- self.yVel) /
                    self.universe.physics.playerGravity))

            self.yVel = self.universe.physics.playerMaxFallVel
        else:
            # Simple case: s=ut+0.5at**2
            deltaY = (deltaY + self.yVel * fallTime + 0.5 *
                    self.universe.physics.playerGravity * fallTime ** 2)
            self.yVel = vFinal

        return deltaX, deltaY

    def fallThroughAir(self, absVel, deltaT):
        deltaX, deltaY, fallTime = self.calculateJumpMotion(absVel, deltaT)
        deltaX, deltaY = self.getFallTrajectory(deltaX, deltaY, fallTime)

        obstacle = self.universe.physics.moveUnit(self, deltaX, deltaY)
        if obstacle:
            if obstacle == self._unstickyWall:
                targetPt = obstacle.unstickyWallFinalPosition(self.pos, deltaX,
                        deltaY)
            else:
                targetPt = obstacle.finalPosition(self, deltaX, deltaY)
            if targetPt is not None:
                deltaX = targetPt[0] - self.pos[0]
                deltaY = targetPt[1] - self.pos[1]
                obstacle = self.universe.physics.moveUnit(self, deltaX, deltaY)

        if obstacle and obstacle.jumpable:
            self.setAttachedObstacle(obstacle)
            self.universe.playerIsDirty(self.id)
        else:
            self.setAttachedObstacle(None)
        if obstacle:
            obstacle.hitByPlayer(self)
            self.universe.playerIsDirty(self.id)

        self._ignore = None

    def updateLivingPlayer(self, deltaT):
        self.processJumpState()

        absVel = self.getAbsVelocity()
        wall = self.isAttachedToWall()

        # Allow falling through fall-through-able obstacles
        if self.isOnPlatform() and self._state['down']:
            self.dropThroughFloor()
        if self.isOnGround():
            self.moveAlongGround(absVel, deltaT)
        elif wall:
            if (self._state['down'] or (self._state['right'] and wall == 'left')
                    or (self._state['left'] and wall == 'right')):
                self.dropOffWall()
        else:
            self.fallThroughAir(absVel, deltaT)

    def update(self, deltaT):
        '''Called by this player's universe when this player should update
        its position. deltaT is the time that's passed since its state was
        current, measured in seconds.'''

        self.checkUpgrades(deltaT)
        self.reloadTime = max(0.0, self.reloadTime - deltaT)

        if self.ghost:
            self.updateGhost(deltaT)
        elif self.turret:
            self.updateTurret(deltaT)
        else:
            self.updateLivingPlayer(deltaT)

    def changeZone(self, newZone):
        try:
            self.currentZone.removePlayer(self)
        except Exception, e:
            log.exception(str(e))
        newZone.addPlayer(self)
        self.currentZone = newZone

    def die(self):
        self.currentZone.removePlayer(self)
        self.ghost = True
        self.currentZone.addPlayer(self)
        self.health = 0
        self.respawnGauge = self.universe.physics.playerRespawnTotal
        self._jumpTime = 0
        self._setStarsForDeath()
        checkpoint('Player: died')

    def hurtBy(self, shooterId, shot, deathType):
        if shot is not None:
            shotId = shot.id
        else:
            shotId = 0

        if self.phaseshift or self.turret:
            if shotId != 0:
                self.universe.eventPlug.send(ShotAbsorbedMsg(self.id,
                        shooterId, shotId))
        elif self.shielded and self.upgrade.protections <= 1:
            self.universe.eventPlug.send(ShotAbsorbedMsg(self.id, shooterId,
                    shotId))
            self.universe.eventPlug.send(DeleteUpgradeMsg(self.id,
                    self.upgrade.upgradeType, 'S'))
        elif self.health <= 1:
            self.deathDetected(shooterId, shotId, deathType)
            if shotId != 0:
                if shot.bounced:
                    self.universe.eventPlug.send(
                        AchievementProgressMsg(shooterId, 'ricochetKill'))

                if shot.timeLeft < 0.1:
                    self.universe.eventPlug.send(
                        AchievementProgressMsg(shooterId, 'longRangeKill'))
        else:
            self.universe.eventPlug.send(PlayerHitMsg(self.id, shooterId,
                    shotId, deathType))

    def deathDetected(self, shooterId, shotId, deathType):
        if self.upgrade is None:
            upgradeType = "-"
        else:
            upgradeType = self.upgrade.upgradeType;

        self.universe.eventPlug.send(PlayerKilledMsg(self.id,
                    shooterId, shotId, self.stars, upgradeType, deathType))
        if self.upgrade is not None and self.upgrade.goneWhenDie:
            self.universe.eventPlug.send(DeleteUpgradeMsg(self.id,
                    self.upgrade.upgradeType, 'D'))

        if self.universe.state.becomeNeutralWhenDie() and self.team is not None:
            self.universe.eventPlug.send(SetPlayerTeamMsg(self.id,
                    NeutralTeamId))

    def _setStarsForDeath(self):
        self.stars = self.universe.PLAYER_RESET_STARS

    def respawn(self):
        self.setAttachedObstacle(None)
        self.ghost = False
        self.health = self.universe.physics.playerRespawnHealth
        self.invulnerableUntil = (self.universe.getElapsedTime() +
                RESPAWN_CAMP_TIME)
        self.respawnGauge = 0
        self.pos = self.currentZone.defn.pos
        i, j = MapLayout.getMapBlockIndices(self.pos[0], self.pos[1])
        try:
            block = self.universe.zoneBlocks[i][j]
        except IndexError:
            raise IndexError, "You're off the map!"
        self.setMapBlock(block)
        checkpoint('Player: respawned')

    def deleteUpgrade(self):
        '''Deletes the current upgrade object from this player'''
        if self.upgrade:
            self.upgrade.delete()

    def destroyShot(self, sId):
        try:
            del self.shots[sId]
        except KeyError:
            pass

    def addShot(self, shot):
        self.shots[shot.id] = shot

    def incrementStars(self):
        if self.stars < MAX_STARS:
            self.stars += 1

    def getShotType(self):
        '''
        Returns one of the following:
            None - if the player cannot currently shoot
            'N' - if the player can shoot normal shots
            'R' - if the player can shoot ricochet shots
            'T' - if the player can shoot turret shots
        '''
        if self.ghost or self.phaseshift:
            return None

        # While on a vertical wall, one canst not fire
        if self.reloadTime > 0 or self.isAttachedToWall():
            return None

        if self.hasRicochet:
            return 'R'
        if self.turret:
            if self.turretOverHeated:
                return None
            return 'T'
        return 'N'

    def isElephantOwner(self):
        return self.user is not None and self.user.isElephantOwner()

    def hasElephant(self):
        return self.universe.playerWithElephant == self

    def canShoot(self):
        return self.getShotType() is not None

    def makePlayerUpdate(self):
        values = compress_boolean((self._state['left'],
                self._state['right'], self._state['jump'],
                self._state['down'], self.upgrade is not None, self.ghost
                ))

        if self.isOnGround():
            attached = 'g'
        else:
            wall = self.isAttachedToWall()
            if not wall:
                attached = 'f'
            else:
                attached = wall[0]

        return PlayerUpdateMsg(self.id, self.pos[0],
                self.pos[1], self.yVel, self.angleFacing,
                self.ghostThrust, attached, str(values))
