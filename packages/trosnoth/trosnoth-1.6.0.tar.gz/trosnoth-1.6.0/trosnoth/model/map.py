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

from trosnoth.model.zone import ZoneDef, ZoneState
from trosnoth.utils.unrepr import unrepr

class MapLayout(object):
    '''Stores static info about the layout of the map.

    Attributes:
        centreX, centreY: the x and y coordinates of the map centre.
        zones: collection of zoneDefs
        blocks: collection of blockDefs
    '''

    # The dimensions of zones. See diagram below.
    halfZoneHeight = 384        # a / 2
    zoneBodyWidth = 1024        # b
    zoneInterfaceWidth = 512    # c

    # This diagram explains the dimensions defined above.
    #     \___________/ _ _ _ _
    #     /           \       ^
    #    /             \      |
    # __/               \___  a
    #   \               /|    |
    #    \             / |    |
    #     \___________/ _|_ _ v
    #     /|         |\  |
    #      |<-- b -->|<c>|

    def __init__(self, halfMapWidth, mapHeight):
        self.halfMapWidth = halfMapWidth
        self.mapHeight = mapHeight

        from trosnoth.model.mapblocks import MapBlockDef
        totalWidth = halfMapWidth * 2 + 1
        middleHeight = ((halfMapWidth - 1) % 2) + 1 + mapHeight

        self.worldSize = (
            totalWidth * self.zoneBodyWidth + (totalWidth + 1) *
                    self.zoneInterfaceWidth,
            2 * middleHeight * self.halfZoneHeight
        )

        if middleHeight == mapHeight + 2:
            highExists = True
        else:
            highExists = False

        # Calculate position of centre.
        self.centreX = ((halfMapWidth + 0.5) * MapLayout.zoneBodyWidth +
                (halfMapWidth + 1) * MapLayout.zoneInterfaceWidth)
        self.centreY = middleHeight * MapLayout.halfZoneHeight

        # Collection of all zone definitions:
        self.zones = set()

        # Zones shall also be stored as a multidimensional array
        # in the following format of column/vertical position:
        #    0   1   2   3   4   5   6
        # 0 -/a  a  a\-  -  -/d  d  d\-
        # 1 -\a  a  a/c  c  c\d  d  d/-
        # 2 -/b  b  b\c  c  c/e  e  e\-
        # 3 -\b  b  b/-  -  -\e  e  e/-
        # so that the players' currentZone can more easily be calculated (in
        # the getMapBlockIndices procedure below)

        # This will be stored in the format of a list of lists of MapBlocks.
        # The most encompassing list will store the rows.
        # Each "row" will be a list of blocks.
        # Each "block" will be an instance of a subclass of MapBlock.

        self.blocks = []
        blockTypes = ('btm', 'fwd', 'top', 'bck')
        y = 0

        # Decide which type of block to start with.
        if halfMapWidth % 2 == 0:
            nextBlock = 1
        else:
            nextBlock = 3

        # Initialise self.blocks
        for i in range(middleHeight * 2):
            row = []
            x = 0
            bodyBlock = None
            for j in range(totalWidth):
                # Add an interface.
                blockType = blockTypes[nextBlock]
                ifaceBlock = MapBlockDef(blockType, x, y)
                row.append(ifaceBlock)

                x = x + MapLayout.zoneInterfaceWidth
                nextBlock = (nextBlock + 1) % 4

                # Add a body block.
                blockType = blockTypes[nextBlock]
                bodyBlock = MapBlockDef(blockType, x, y)
                row.append(bodyBlock)

                x = x + MapLayout.zoneBodyWidth
                nextBlock = nextBlock + 1

            # Add the last interface.
            blockType = blockTypes[nextBlock]
            ifaceBlock = MapBlockDef(blockType, x, y)
            row.append(ifaceBlock)

            self.blocks.append(row)
            y = y + MapLayout.halfZoneHeight

        # height: low means the column is of height mapHeight
        # mid means it is mapHeight + 1, high means mapHeight + 2 (middleHeight)

        # height starts (and ends) at low in every case.
        height = "low"

        # numSoFar keeps track of the number of zones created so far.
        numSoFar = 0

        ''' To calculate adjacent zones, the zones were conceptualised in the
         following pattern, counting downwards by column, then left to right:
         (assuming mapHeight = 3, halfMapWidth = 2)
              7
            3    12
         0    8     16
            4    13
         1    9     17
            5    14
         2    10    18
            6    15
              11

        '''

        '''In order to create each of the zones, we will iterate firstly through
        each of the columns, then through each of the zones in each column. This
        allows us to calculate adjacent zones based on column height.'''

        # Keep track of where the zones should be put.
        xCoord = MapLayout.zoneInterfaceWidth + int(MapLayout.zoneBodyWidth / 2)

        # Iterate through each column:
        for i in range(0, totalWidth):
            startCol = i * 2

            # Determine number of zones in the current column
            if height == "low":
                colHeight = mapHeight
            elif height == "mid":
                colHeight = mapHeight + 1
            elif height == "high":
                colHeight = mapHeight + 2

            # Calculate y-coordinate of the first zone in the column.
            if height == "low" and highExists:
                yCoord = MapLayout.halfZoneHeight
            elif ((height == "mid" and highExists) or (height == "low" and not
                    highExists)):
                yCoord = 0
            elif height == "high" or (height == "mid" and not highExists):
                yCoord = -MapLayout.halfZoneHeight

            prevZone = None

            # Iterate through each zone in the column
            for j in range(0, colHeight):

                # Determine Team, and create a zone.
                if i < halfMapWidth:
                    team = 0
                elif i > (halfMapWidth):
                    team = 1
                else:
                    team = None

                # Determine co-ordinates of the zone's orb (middle of zone)
                yCoord = yCoord + 2 * MapLayout.halfZoneHeight

                newZone = ZoneDef(numSoFar, team, xCoord, yCoord)


                # Link this zone to the zone above.
                if prevZone is not None:
                    connectingBlocks = (self.blocks[y][startCol+1],
                            self.blocks[y+1][startCol+1])
                    prevZone.adjacentZones[newZone] = connectingBlocks
                    newZone.adjacentZones[prevZone] = connectingBlocks

                # Add zone to list of zones
                self.zones.add(newZone)


                # Add zone to blocks
                if highExists and height == "low":
                    startRow = 2 + j * 2
                elif (highExists and height == "mid") or (not highExists and
                        height == "low"):
                    startRow = 1 + j * 2
                elif height == "high" or (not highExists and height == "mid"):
                    startRow = 0 + j * 2
                else:
                    raise Exception, "There's an error in blocks allocation"

                # Put new zone into blocks, and connect it to zones left.
                for y in range(startRow, startRow+2):
                    cornerBlock = self.blocks[y][startCol+2]
                    cornerBlock.zone1 = newZone
                    bodyBlock = self.blocks[y][startCol+1]
                    bodyBlock.zone = newZone
                    block = self.blocks[y][startCol]
                    block.zone2 = newZone
                    newZone.bodyBlocks.append(bodyBlock)
                    newZone.interfaceBlocks.extend([cornerBlock, block])

                    if block.zone1:
                        # Connect this block to the block to the left.
                        block.zone1.adjacentZones[newZone] = (block,)
                        newZone.adjacentZones[block.zone1] = (block,)

                # If block is at the top of a column, it must have a roof.
                if prevZone is None:
                    self.blocks[startRow][startCol+1].blocked = True

                numSoFar = numSoFar + 1
                prevZone = newZone

            # Make sure that the bottom zone in each column has a floor.
            self.blocks[startRow+1][startCol+1].blocked = True

            # Advance x-coordinate.
            xCoord = (xCoord + MapLayout.zoneBodyWidth +
                    MapLayout.zoneInterfaceWidth)

            # Determine how high the next column will be:
            if height == "low":
                if i == totalWidth - 1:
                    height = None
                else:
                    height = "mid"
            elif height == "mid":
                if i == halfMapWidth - 1:
                    height = "high"
                else:
                    height = "low"
            elif height == "high":
                height = "mid"

        for row in self.blocks:
            for i in xrange(0, len(row), 2):
                block = row[i]
                if block.zone1 is None or block.zone2 is None:
                    # Make sure the edges are blocked.
                    block.blocked = True
        # Zone initialisation and calculations end here.

    def toString(self):
        '''
        Serialises this MapLayout into a string that can be sent over the
        network, then reconstructed with fromString().
        '''
        result = []
        for blockRow in self.blocks:
            row = []
            result.append(row)
            for block in blockRow:
                if block.layout is None:
                    row.append(None)
                else:
                    row.append(block.layout.key)
        return repr([(self.halfMapWidth, self.mapHeight), result])

    @staticmethod
    def unknownBlockKeys(layoutDatabase, text):
        '''
        Goes through a MapLayout's toString() representation and checks for and
        returns a collection of map block keys for all map blocks not known by
        the given layoutDatabase.
        '''
        result = set()
        data = unrepr(text)
        assert isinstance(data, list)
        discard, data = data
        for row in data:
            for key in row:
                if key is not None:
                    fKey = layoutDatabase.getFundamentalKey(key)
                    if fKey is not None:
                        result.add(fKey)

        return result

    @staticmethod
    def fromString(layoutDatabase, text):
        '''
        Reconstructs a MapLayout from its toString() result. Assumes that all
        map block definitions are available in the LayoutDatabase given.
        '''
        data = unrepr(text)
        assert isinstance(data, list)
        (halfMapWidth, mapHeight), data = data
        result = MapLayout(halfMapWidth, mapHeight)
        for i, row in enumerate(data):
            for j, key in enumerate(row):
                if key is not None:
                    layout = layoutDatabase.getLayoutByKey(key)
                    layout.applyTo(result.blocks[i][j])
        return result

    @staticmethod
    def getMapBlockIndices(xCoord, yCoord):
        '''Returns the index in Universe.zoneBlocks of the map block which the
        given x and y-coordinates belong to.
        (0, 0) is the top-left corner.

        To find a zone, use MapBlock.getZoneAtPoint()'''

        blockY = int(yCoord // MapLayout.halfZoneHeight)

        blockX, remainder = divmod(xCoord, MapLayout.zoneBodyWidth +
                MapLayout.zoneInterfaceWidth)
        if remainder >= MapLayout.zoneInterfaceWidth:
            blockX = int(2 * blockX + 1)
        else:
            blockX = int(2 * blockX)

        return blockY, blockX

class MapState(object):
    '''Stores dynamic info about the layout of the map including who owns what
    zone.

    Attributes:
        layout - the static MapLayout
        zones - a set of zones
        blocks - a set of blocks
        zoneWithId - mapping from zone id to zone
    '''
    def __init__(self, universe, layout):
        self.layout = layout

        self.zones = set()
        self.zoneWithDef = {}
        for zone in self.layout.zones:
            newZone = ZoneState(universe, zone)

            self.zones.add(newZone)
            self.zoneWithDef[zone] = newZone

        self.zoneWithId = {}
        for zone in self.zones:
            self.zoneWithId[zone.id] = zone

        self.zoneBlocks = []
        for row in self.layout.blocks:
            newRow = []
            for blockDef in row:
                newRow.append(blockDef.spawnState(universe, self.zoneWithDef))
            self.zoneBlocks.append(newRow)
