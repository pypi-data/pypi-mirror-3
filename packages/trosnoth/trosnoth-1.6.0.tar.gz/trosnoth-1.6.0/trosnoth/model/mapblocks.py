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

import pygame
import random

from trosnoth.model.obstacles import (GroundObstacle, LedgeObstacle,
        VerticalWall, RoofObstacle, joinObstacles)
from trosnoth.model.map import MapLayout

class MapBlockDef(object):
    '''Represents the static information about a particular map block. A map
    block is a grid square, and may contain a single zone, or the interface
    between two zones.'''

    def __init__(self, kind, x, y):
        self.pos = (x, y)       # Pos is the top-left corner of this block.
        assert kind in ('top', 'btm', 'fwd', 'bck')
        self.kind = kind
        self.layout = None

        self.obstacles = []
        self.ledges = []
        self.indices = MapLayout.getMapBlockIndices(x, y)

        self.rect = pygame.Rect(x, y, 0, 0)
        self.rect.size = (self._getWidth(), MapLayout.halfZoneHeight)

        self.graphics = None
        self.blocked = False    # There's a barrier somewhere depending on type.

        # For body block.
        self.zone = None

        # For interface block.
        self.zone1 = None
        self.zone2 = None

    def __str__(self):
        return 'Block @ %r' % (self.indices,)

    def _getWidth(self):
        if self.kind in ('top', 'btm'):
            return MapLayout.zoneBodyWidth
        else:
            return MapLayout.zoneInterfaceWidth

    def spawnState(self, universe, zoneWithDef):
        if self.kind == 'top':
            return TopBodyMapBlock(universe, self,
                zoneWithDef.get(self.zone, None))
        elif self.kind == 'btm':
            return BottomBodyMapBlock(universe, self,
                zoneWithDef.get(self.zone, None))
        elif self.kind == 'fwd':
            return ForwardInterfaceMapBlock(universe, self,
                zoneWithDef.get(self.zone1, None),
                zoneWithDef.get(self.zone2, None))
        elif self.kind == 'bck':
            return BackwardInterfaceMapBlock(universe, self,
                zoneWithDef.get(self.zone1, None),
                zoneWithDef.get(self.zone2, None))
        else:
            assert False

    def randomPosition(self):
        '''
        Returns a random position within this map block.
        '''
        x = self.rect.left + random.random() * self.rect.width
        y = self.rect.top + random.random() * self.rect.height
        return x, y

    def randomPositionInZone(self, zone):
        '''
        Returns a random position within this map block and within the given
        zone.
        '''
        if zone not in self.getZones():
            raise ValueError('Invalid zone!')
        while True:
            x, y = self.randomPosition()
            if self.getZoneAtPoint(x, y) == zone:
                return x, y

    def getZones(self):
        result = []
        for z in (self.zone, self.zone1, self.zone2):
            if z is not None:
                result.append(z)
        return result

    def getZoneAtPoint(self, x, y):
        '''getZoneAtPoint(x, y)
        Returns the zone def for the zone at the specified point, ASSUMING
        that the point is in fact within this map block.'''
        if self.kind == 'fwd':
            # Equation of interface line:
            #   (y - self.y) = -(halfZoneHeight / interfaceWidth)(x - self.x)
            #                        + halfZoneHeight
            deltaY = y - self.pos[1] - MapLayout.halfZoneHeight
            deltaX = x - self.pos[0]

            if (deltaY * MapLayout.zoneInterfaceWidth >
                   -MapLayout.halfZoneHeight * deltaX):
                return self.zone2
            return self.zone1
        elif self.kind == 'bck':
            # Equation of interface line:
            #   (y - self.y) = (halfZoneHeight / interfaceWidth)(x - self.x)
            deltaY = y - self.pos[1]
            deltaX = x - self.pos[0]

            if (deltaY * MapLayout.zoneInterfaceWidth >
                    MapLayout.halfZoneHeight * deltaX):
                return self.zone1
            return self.zone2
        else:
            return self.zone

    def addPlatform(self, pos, dx, reverse):
        '''Adds a horizontal platform which can be dropped through to this
        block's list of obstacles.

        pos         The position of the obstacle's first point relative to the
                    top-left corner of this block, or relative to the top-right
                    corner if reverse is set to True.
        dx          The horizontal displacement from first point to the second
                    point of the obstacle. This value should always be positive.
        reverse     Determines whether the obstacle is defined in terms of the
                    top-left corner of this map block or the top-right corner.
        '''

        # Add the block's position offset.
        pt = [pos[0] + self.pos[0],
              pos[1] + self.pos[1]]
        if reverse:
            pt[0] += self.rect.width

        # Put the platform in.
        x, y = pt

        self.ledges.append(LedgeObstacle(pt, (dx, 0)))

    def addObstacle(self, points, reverse):
        '''Adds an obstacle to this block's list of obstacles.

        points      A sequence specifying the positions of the obstacle's points
                    relative to the top-left corner of this block, or relative
                    to the top-right corner if reverse is set to True.
        reverse     Determines whether the obstacle is defined in terms of the
                    top-left corner of this map block or the top-right corner.
        '''
        def translate(pt):
            '''
            Translates the give point to absolute reference points given that
            it's relative to this map block.
            '''
            x = pt[0] + self.pos[0]
            y = pt[1] + self.pos[1]
            if reverse:
                x += self.rect.width
            return x, y

        lastGround = [None]
        def checkGround(obstacle):
            if obstacle.deltaPt[0] > 0:
                if lastGround[0]:
                    obstacle.leftGround = lastGround[0]
                    lastGround[0].rightGround = obstacle
                lastGround[0] = obstacle
            else:
                lastGround[0] = None

        def addObstacle(pt1, pt2):
            '''
            Creates, records and returns a new obstacle between the two points
            provided.
            '''
            dx, dy = pt2[0]-pt1[0], pt2[1]-pt1[1]

            if dx == 0:
                kind = VerticalWall
            elif dx > 0:
                kind = GroundObstacle
            else:
                kind = RoofObstacle

            obstacle = kind(pt1, (dx, dy))
            self.obstacles.append(obstacle)
            return obstacle

        firstObstacle = None
        prevObstacle = None
        prevPt = None
        for pt in points:
            pt = translate(pt)
            if prevPt is not None:
                obstacle = addObstacle(prevPt, pt)
                if prevObstacle is None:
                    firstObstacle = obstacle
                else:
                    self.obstacles.extend(joinObstacles(prevObstacle, obstacle))
                prevObstacle = obstacle
            prevPt = pt
        if points[0] == points[-1] and firstObstacle is not None:
            self.obstacles.extend(joinObstacles(obstacle, firstObstacle))

    def coalesceLayout(self):
        '''
        Gives this block definition the chance to perform calculations after all
        obstacles have been added to it.
        '''
        touched = set()
        for obs in self.obstacles:
            if obs in touched or not obs.ground:
                continue
            subshape = set()
            pending = set([obs])
            while len(pending) > 0:
                obs = pending.pop()
                if obs in subshape:
                    continue
                subshape.add(obs)
                touched.add(obs)
                if obs.leftGround is not None:
                    pending.add(obs.leftGround)
                if obs.rightGround is not None:
                    pending.add(obs.rightGround)
            for obs in subshape:
                obs.subshape = subshape

class MapBlock(object):
    '''Represents a grid square of the map which may contain a single zone,
    or the interface between two zones.
    '''

    def __init__(self, universe, defn):
        self.universe = universe
        self.defn = defn

        self.shots = set()
        self.players = set()
        self.grenades = set()
        self.collectableStars = set()

    def removePlayer(self, player):
        if player in self.players:
            self.players.remove(player)

    def addPlayer(self, player):
        self.players.add(player)

    def __contains__(self, point):
        '''Checks whether a given point is within this zone.'''
        return self.defn.rect.collidepoint(*point)

    def _getBlockLeft(self):
        try:
            i, j = self.defn.indices
            if j == 0:
                return None
            return self.universe.zoneBlocks[i][j-1]
        except IndexError:
            return None
    blockLeft = property(_getBlockLeft)

    def _getBlockRight(self):
        try:
            i, j = self.defn.indices
            if j >= len(self.universe.zoneBlocks[i]) - 1:
                return None
            return self.universe.zoneBlocks[i][j+1]
        except IndexError:
            return None
    blockRight = property(_getBlockRight)

    def _getBlockAbove(self):
        try:
            i, j = self.defn.indices
            if i == 0:
                return None
            return self.universe.zoneBlocks[i-1][j]
        except IndexError:
            return None
    blockAbove = property(_getBlockAbove)

    def _getBlockBelow(self):
        try:
            i, j = self.defn.indices
            if i >= len(self.universe.zoneBlocks) - 1:
                return None
            return self.universe.zoneBlocks[i+1][j]
        except IndexError:
            return None
    blockBelow = property(_getBlockBelow)

    def getZoneAtPoint(self, x, y):
        '''getZoneAtPoint(x, y)
        Returns what zone is at the specified point, ASSUMING that the point
        is in fact within this map block.'''
        raise NotImplementedError, 'getZoneAtPoint not implemented.'

    def shotHitPlayer(self, shot, player):
        if shot.registeredHit:
            return
        if shot.originatingPlayer is not None:
            shooterId = shot.originatingPlayer.id
        else:
            shooterId = '\x00'

        if player.ghost or player.turret or player.isInvulnerable():
            return

        shot.registeredHit = True
        player.hurtBy(shooterId, shot, 'S')

    def collideTrajectory(self, pt, origin, trajectory, tolerance):
        '''Returns true if pt lies within a distance of tolerance from the
        line segment described by origin and trajectory.'''

        # Get distance between point and trajectory origin.
        tr0 = origin
        d0 = ((tr0[0] - pt[0]) ** 2 + (tr0[1] - pt[1]) ** 2) ** 0.5
        if d0 < tolerance:
            return True

        delta = trajectory

        while True:
            # Calculate other end of trajectory.
            tr1 = (tr0[0] + delta[0],
                   tr0[1] + delta[1])
            d1 = ((tr1[0] - pt[0]) ** 2 + (tr1[1] - pt[1]) ** 2) ** 0.5

            # Check for collision.
            if d1 < tolerance:
                return True

            # Refine and loop.
            if d1 < d0:
                tr0, delta = tr1, (-0.5 * delta[0],
                                   -0.5 * delta[1])
            else:
                delta = (0.5 * delta[0],
                         0.5 * delta[1])

            # Check end condition.
            if (delta[0] ** 2 + delta[1] ** 2) < 5:
                return False

    def fromEdge(self, player):
        '''Returns the distance from the edge of the zone that a player is'''
        return

    def removeShot(self, shot):
        '''Removes a given shot from this mapBlock'''
        self.shots.remove(shot)

    def addShot(self, shot):
        '''Adds a given shot to this mapBlock'''
        if shot not in self.shots:
            self.shots.add(shot)

    def removeGrenade(self, grenade):
        '''Removes a given grenade from this mapBlock'''
        self.grenades.remove(grenade)

    def addGrenade(self, grenade):
        '''Adds a given grenade to this mapBlock'''
        self.grenades.add(grenade)

    def removeCollectableStar(self, star):
        '''Removes a given grenade from this mapBlock'''
        self.collectableStars.remove(star)

    def addCollectableStar(self, star):
        '''Adds a given grenade to this mapBlock'''
        self.collectableStars.add(star)

class BodyMapBlock(MapBlock):
    '''Represents a map block which contains only a single zone.'''

    def __init__(self, universe, defn, zone):
        super(BodyMapBlock, self).__init__(universe, defn)
        self.zone = zone

    def __str__(self):
        return '< %s >' % self.zone

    def getZoneAtPoint(self, x, y):
        return self.zone

    def getZones(self):
        if self.zone is not None:
            yield self.zone


class TopBodyMapBlock(BodyMapBlock):
    '''Represents a map block containing the top half of a zone.'''

    def orbPos(self, drawRect):
        return drawRect.midbottom

    def fromEdge(self, player):
        '''Returns the distance from the edge of the zone that a player is'''

        return min(abs(player.pos[1] - self.defn.rect.top),
                self.blockLeft.fromEdge(player),
                self.blockRight.fromEdge(player))

class BottomBodyMapBlock(BodyMapBlock):
    '''Represents a map block containing the bottom half of a zone.'''

    def orbPos(self, drawRect):
        return drawRect.midtop

    def fromEdge(self, player):
        '''Returns the distance from the edge of the zone that a player is'''

        return min(abs(self.defn.rect.bottom - player.pos[1]),
                self.blockLeft.fromEdge(player),
                self.blockRight.fromEdge(player))

class InterfaceMapBlock(MapBlock):
    '''Base class for map blocks which contain the interface between two
    zones.'''

    def __init__(self, universe, defn, zone1, zone2):
        super(InterfaceMapBlock, self).__init__(universe, defn)

        self.zone1 = zone1
        self.zone2 = zone2

    def getZones(self):
        if self.zone1 is not None:
            yield self.zone1
        if self.zone2 is not None:
            yield self.zone2

class ForwardInterfaceMapBlock(InterfaceMapBlock):
    '''Represents a map block which contains the interface between two
    zones, split in the direction of a forward slash '/'.
    Note that exactly on the diagonal counts as being in the left-hand zone.
    '''

    def __str__(self):
        return '< %s / %s >' % (self.zone1, self.zone2)

    def getZoneAtPoint(self, x, y):
        # Equation of interface line:
        #   (y - self.y) = -(halfZoneHeight / interfaceWidth)(x - self.x)
        #                        + halfZoneHeight
        deltaY = y - self.defn.pos[1] - MapLayout.halfZoneHeight
        deltaX = x - self.defn.pos[0]

        if (deltaY * MapLayout.zoneInterfaceWidth > -MapLayout.halfZoneHeight *
                deltaX):
            return self.zone2
        return self.zone1

    def fromEdge(self, player):
        '''Returns the distance from the edge of the zone that a player is.
        Assumes that the player is actually in this map block.'''
        relPos = (self.defn.rect.left - player.pos[0], self.defn.rect.top -
                player.pos[1])
        # Note: this following formula relies upon the dimensions:
        # MapLayout.halfZoneHeight = 384
        # MapLayout.zoneInterfaceWidth = 512
        # Should they be changed, should change this to:
        # d = sin(theta) * abs(relPos[1] + relPos[0] *
        # MapLayout.halfZoneHeight / MapLayout.zoneInterfaceWidth + 384)
        # (where theta is the angle formed by the diagonal line seperating the
        # zones, and a vertical line).
        d = 0.8 * abs(relPos[1] + relPos[0] * 0.75 + 384)
        return d

class BackwardInterfaceMapBlock(InterfaceMapBlock):
    '''Represents a map block which contains the interface between two
    zones, split in the direction of a backslash '\'.
    Note that a point exactly on the diagonal counts as being in the left-hand
    zone.
    '''

    def __str__(self):
        return '< %s \ %s >' % (self.zone1, self.zone2)

    def getZoneAtPoint(self, x, y):
        # Equation of interface line:
        #   (y - self.y) = (halfZoneHeight / interfaceWidth)(x - self.x)
        deltaY = y - self.defn.pos[1]
        deltaX = x - self.defn.pos[0]

        if (deltaY * MapLayout.zoneInterfaceWidth >
               MapLayout.halfZoneHeight * deltaX):
            return self.zone1
        return self.zone2

    def fromEdge(self, player):
        '''Returns the distance from the edge of the zone that a player is.
        Assumes that the player is actually in this map block.'''
        relPos = (self.defn.rect.left - player.pos[0], self.defn.rect.top -
                player.pos[1])

        # Note: this following formula relies upon the dimensions:
        # MapLayout.halfZoneHeight = 384
        # MapLayout.zoneInterfaceWidth = 512
        # Should they be changed, should change this to:
        # d = sin(theta) * abs(relPos[1] - relPos[0] *
        # MapLayout.halfZoneHeight / MapLayout.zoneInterfaceWidth)
        # where theta is the angle formed by the diagonal line seperating the
        # zones, and a vertical line.
        d = 0.8 * abs(relPos[1] - relPos[0] * 3 / 4)
        return d
