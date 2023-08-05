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

class Unit(object):
    def __init__(self):
        self.pos = (0, 0)
        self.currentMapBlock = None

    def setMapBlock(self, block):
        '''Called when the sprite changes from one map block to another.'''
        self.currentMapBlock = block

    def isSolid(self):
        raise NotImplementedError

    def ignoreObstacle(self, obstacle):
        '''
        Returns True if this obstacle should be ignored in obstacle collision.
        Implemented by Player class for dropping through platforms.
        '''
        return False

    def continueOffMap(self):
        '''
        Called when this unit has fallen off the map. Returns True or False
        indicating whether this unit should keep falling or not.
        '''
        return True

    def canEnterZone(self, zone):
        '''
        Called when this unit attempts to enter the given zone. Should return
        True or False to indicate whether this zone entry is allowed.
        '''
        return True

    def reset(self):
        '''
        Called once every tick before any sprite has moved.
        '''

    def checkCollisions(self, deltaX, deltaY):
        '''
        Checks any collisions relevant to this unit type.
        '''

    @staticmethod
    def getObstacles(mapBlockDef):
        '''
        Return which obstacles in the given map block apply to this kind of
        unit.
        '''
        return mapBlockDef.obstacles
