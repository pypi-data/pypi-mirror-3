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

'''mapLayout.py - takes care of initialising map blocks with obstacles and
 images.'''

import logging
import os, random
from StringIO import StringIO

import pygame

from trosnoth.utils.utils import hasher
from trosnoth.utils import unrepr
from trosnoth.model.map import MapLayout

from trosnoth.data import getPath, user, makeDirs
import trosnoth.data.blocks

log = logging.getLogger('mapLayout')

BLOCK_FILES = {
    'ForwardInterfaceMapBlock': 'fwd',
    'BackwardInterfaceMapBlock': 'bck',
    'TopBodyMapBlock': 'top',
    'BottomBodyMapBlock': 'btm',
}

class ChecksumError(Exception):
    pass

class LayoutDatabase(object):
    '''
    Represents a database which stores information on block layouts.
    Contains several LayoutDatastores which will be queried in their order of
    priority when a block is needed.
    '''
    def __init__(self, app, blocks=()):
        self.app = app
        self.datastores = []
        self._addDatastoreWithBlocks(blocks)
        self._addDatastoreByPaths(getPath(trosnoth.data.blocks), getPath(user,
                'blocks'))
        self.downloadPath = getPath(user, 'downloadedBlocks')
        self.downloads = self._addDatastoreByPaths(self.downloadPath)

    def _addDatastoreWithBlocks(self, blocks):
        if len(blocks) == 0:
            return

        store = LayoutDatastore(self.app)
        self.datastores.append(store)
        for block in blocks:
            store.addLayoutAtFilename(block)

    def _addDatastoreByPaths(self, *paths):
        for path in paths:
            makeDirs(path)

        store = LayoutDatastore(self.app)
        self.datastores.append(store)

        # Read map blocks from files.
        for path in paths:
            filenames = os.listdir(path)

            # Go through all files in the blocks directory.
            for fn in filenames:
                # Check for files with a .block extension.
                if os.path.splitext(fn)[1] == '.block':
                    store.addLayoutAtFilename(os.path.join(path, fn))
        return store

    def addDownloadedBlock(self, key, contents, graphics):
        '''
        Adds the given block (which has been downloaded from a remote server) to
        the database.
        '''
        # First save the contents.
        while True:
            base = '%.32x' % (random.randrange(1<<128))
            filename = os.path.join(self.downloadPath, base)
            if not os.path.exists(filename):
                break
        open(filename + '.block', 'wb').write(contents)
        open(filename + '.png', 'wb').write(graphics)

        # Add new block to datastore.
        self.downloads.addLayoutAtFilename(filename + '.block')

    def getFundamentalKey(self, key):
        '''
        If a block with the given key exists in the database, returns None,
        otherwise returns a fundamental form of the key which should be used
        when asking a remote server for a copy of the block. This is done so
        that only one request is sent for map blocks which are mirror images of
        one another.
        '''
        kind, checksum, reversed = key
        for ds in self.datastores:
            if (kind, checksum) in ds.layoutsByKey:
                return None
        return (kind, checksum, False)

    def getLayoutByKey(self, key):
        '''
        Returns a BlockLayout from its key, or None if no such layout is known.
        '''
        for ds in self.datastores:
            result = ds.getLayoutByKey(key)
            if result is not None:
                return result
        return None

    def getRandomLayout(self, kind, blocked):
        for ds in self.datastores:
            if len(ds.layouts[kind, blocked]) > 0:
                return random.choice(ds.layouts[kind, blocked])
        raise ValueError('No layouts found of kind %r with blocked %r' % (kind,
                blocked))

    def getRandomSymmetricalLayout(self, kind, blocked):
        for ds in self.datastores:
            if len(ds.symmetricalLayouts[kind, blocked]) > 0:
                return random.choice(ds.symmetricalLayouts[kind, blocked])
        raise ValueError('No symmetrical layouts found of kind %r with '
                'blocked %r' % (kind, blocked))

    def randomiseBlock(self, block, oppBlock):
        '''Takes a map block and gives it and the
        corresponding opposite block a layout depending on its block type
        and whether it has a barrier.
        '''
        if oppBlock is not block:
            # The block is not symmetrical.
            layout = self.getRandomLayout(block.kind, block.blocked)
            layout.applyTo(block)
            layout.mirrorLayout.applyTo(oppBlock)
        else:
            # The block is symmetrical.
            layout = self.getRandomSymmetricalLayout(block.kind, block.blocked)
            layout.applyTo(block)

    def generateRandomMapLayout(self, halfMapWidth, mapHeight, blockRatio=0.5):
        '''
        Generates and returns a random MapLayout object of the given dimensions
        using blocks from this layout database.
        '''
        #seed = "Clamburger"
        #random.seed(seed)

        layout = MapLayout(halfMapWidth, mapHeight)
        mapBlockList = {}
        tempBlocked = {}
        for blockList in layout.blocks:
            for block in blockList:
                tempBlocked[block] = False
                zones = block.getZones()
                for zone in zones:
                    mapBlockList.setdefault(zone, []).append(block)

        x = -1
        for blockList in layout.blocks:
            x += 1
            for i in range(len(blockList) / 2 + 1):
                block = blockList[i]
                oppBlock = blockList[-i-1]

                if block.blocked:
                    # The block is on the edge, leave it as is
                    continue
                elif len(block.getZones()) == 0:
                    # The block is outside where the player can go
                    continue
                else:
                    # If it's a topBodyMapBlock, make it the same as the
                    # bottomBodyMapBlock just above it
                    if block.kind == 'top':
                        blockAbove = layout.blocks[x-1][i]
                        tempBlocked[block] = tempBlocked[blockAbove]
                    elif random.random() < blockRatio:
                        tempBlocked[block] = True
                        tempBlocked[oppBlock] = True

        # At this point, many of the blocks will probably be connected to all
        # others. However, we shall now ensure that all are connected, using
        # the following method:
        #
        #
        # 1. Find the central zone of the entire map. Use this as a starting
        # point.
        #
        # 2. Create a list of connected zones. At first, the list should only
        # contain the central zone.
        #
        # 3. Create an empty list of unconnected but adjacent zones.
        #
        # 4. For each zone next to the central zone, if it is blocked, add it to
        # the list of unconnected but adjacent zones. Otherwise, add it to the
        # list of connected zones. However, ignore zones on the right-hand side
        # of the map.
        #
        # 5. Repeat step 4 for each of the zones that was just added to the
        # list of connecteds. If ever a zone is added to the list of connecteds,
        # be sure to remove it from the list of unconnected-but-adjacent-zones
        # (if it exists in that list).
        #
        # 6. Choose a random zone from the list of unconnected and adjacent
        # zones. Connect it to a random zone in the list of connecteds
        # (obviously one to which it is adjacent). Remove it from the list
        # of unconnecteds, and add it to the list of connecteds.
        #
        # 7. While the list of unconnecteds is not empty, repeat steps 4-6,
        # using this newly connected zone in place of the central zone.


        centralRow = layout.blocks[len(layout.blocks)/2]
        centralBlock = centralRow[len(centralRow) / 2]
        centralZone = centralBlock.zone

        def adjacentZones(zone):
            '''
            yields (adjZone, connected) for each adjacent zone, where connected
            is True or False depending on whether the zones are connected or
            not.
            '''
            for zone2, blocks in zone.adjacentZones.iteritems():
                for block in blocks:
                    if tempBlocked[block]:
                        yield zone2, False
                        break
                else:
                    yield zone2, True

        def connectZones(zone1, zone2):
            for block in zone1.adjacentZones[zone2]:
                tempBlocked[block] = False

        mapWidth = (layout.halfMapWidth * 2 + 1) * (layout.zoneBodyWidth +
                layout.zoneInterfaceWidth) + layout.zoneInterfaceWidth
        def oppositeZone(zone):
            x, y = zone.pos
            x = mapWidth - x
            i, j = layout.getMapBlockIndices(x, y)
            return layout.blocks[i][j].getZoneAtPoint(x, y)

        visitedZones = set()
        newZones = set([centralZone])
        unreachedZones = {}     # zone -> connected zones
        while len(newZones) > 0 or len(unreachedZones) > 0:
            while len(newZones) > 0:
                curZone = newZones.pop()
                visitedZones.add(curZone)
                for newZone, connected in adjacentZones(curZone):
                    if newZone in visitedZones:
                        continue
                    if connected:
                        if newZone in unreachedZones:
                            del unreachedZones[newZone]
                        newZones.add(newZone)
                    elif newZone not in visitedZones:
                        unreachedZones.setdefault(newZone, []).append(curZone)

            if len(unreachedZones) > 0:
                zone1 = random.choice(unreachedZones.keys())
                zone2 = random.choice(unreachedZones.pop(zone1))
                connectZones(zone1, zone2)
                newZones.add(zone1)
                zone1b = oppositeZone(zone1)
                zone2b = oppositeZone(zone2)
                if zone1b != zone1 or zone2b != zone2:
                    connectZones(zone1b, zone2b)
                    if zone1b in unreachedZones:
                        del unreachedZones[zone1b]
                    newZones.add(zone1b)

        # Populate the map blocks with appropriate obstacles.

        for blockList in layout.blocks:
            for i in range(len(blockList) / 2 + 1):
                block = blockList[i]
                oppBlock = blockList[-i-1]
                if block is oppBlock:
                    assert block.kind in ('top', 'btm')
                if not block.blocked:
                    block.blocked = tempBlocked[block]
                    if not oppBlock == None:
                        oppBlock.blocked = tempBlocked[oppBlock]
                if not block.getZones() == []:
                    # If the block contains zones, get a layout for this block.
                    self.randomiseBlock(block, oppBlock)

        return layout

class LayoutDatastore(object):
    '''Represents a database which stores information on block layouts.'''

    def __init__(self, app):
        '''(paths) - initialises the database and loads the blocks from the
        specified paths.'''
        self.app = app

        # Set up database.
        self.layouts = {}
        self.layoutsByFilename = {}
        self.layoutsByKey = {}          # Keyed by (kind, checksum)
        self.symmetricalLayouts = {}
        for b in True, False:
            for a in 'fwd', 'bck', 'top', 'btm':
                self.layouts[a, b] = []
            for a in 'top', 'btm':
                self.symmetricalLayouts[a, b] = []

    def addLayoutAtFilename(self, filepath):
        # Remember the filename.
        self.filename = os.path.split(filepath)[1]

        # Read the file and create the block
        f = open(filepath, 'rU')
        try:
            contents = f.read()
        finally:
            f.close()

        self.checksum = hasher(contents).hexdigest()

        try:
            contentDict = unrepr.unrepr(contents)
            self.addLayout(filepath, **contentDict)
        except Exception, e:
            log.warning(str(e))
            return False
        return True

    def addLayout(self, filepath, blockType='TopBodyMapBlock', blocked=False,
              obstacles=[], platforms=[], symmetrical=False, graphics=None):
        '''
        Registers a layout with the given parameters.
        '''
        base, ext = os.path.splitext(filepath)
        if graphics is None:
            graphicsIO = None
            try:
                graphicPath = self.app.theme.getPath('blocks', '%s.png' %
                        (os.path.split(base)[1],))
            except IOError:
                graphicPath = base + '.png'
            else:
                if not os.path.exists(graphicPath):
                    graphicPath = base + '.png'
        else:
            graphicPath = None
            graphicsIO = StringIO()
            graphicsIO.write(graphics.decode('base64'))

        blockType = BLOCK_FILES[blockType]

        newLayout = BlockLayout()
        newLayout.setProperties(graphicPath, obstacles, platforms,
                symmetrical, self.checksum, blockType, filepath,
                graphicPath, graphicsIO)

        # Add the layout to the database.
        self.layouts[blockType, blocked].append(newLayout)
        self.layoutsByFilename[self.filename] = newLayout
        self.layoutsByKey[(blockType, self.checksum)] = newLayout

        if symmetrical:
            self.symmetricalLayouts[blockType, blocked].append(newLayout)
        else:
            if blockType == 'fwd':
                blockType = 'bck'
            elif blockType == 'bck':
                blockType = 'fwd'

            self.layouts[blockType, blocked].append(newLayout.mirrorLayout)

    def getLayoutByKey(self, key):
        '''
        Returns a BlockLayout from its key, or None if no such layout is known.
        '''
        kind, checksum, reversed = key
        try:
            layout = self.layoutsByKey[(kind, checksum)]
        except KeyError:
            return None
        if reversed:
            return layout.mirrorLayout
        return layout

class BlockLayout(object):
    '''Represents the layout of a block. Saves the positions of all obstacles
    within the block as well as a graphic of the block.'''

    def __init__(self):
        '''() - initialises a blank block layout.'''
        self.filename = None
        self.graphics = None
        self.obstacles = []
        self.platforms = []
        self.mirrorLayout = self
        self.reversed = False
        self.kind = None
        self.graphicsFilename = None
        self.graphicsIO = None

    @property
    def forwardLayout(self):
        if self.reversed:
            return self.mirrorLayout
        else:
            return self

    @property
    def key(self):
        '''
        Returns a key by which this block layout may be uniquely identified. The
        block may be obtained from the LayoutDatabase using its
        .getLayoutByKey() method.
        '''
        return (self.kind, self.checksum, self.reversed)

    def setProperties(self, graphicPath, obstacles, platforms, symmetrical,
            checksum, blockType, filename, graphicsFilename, graphicsIO):
        '''(graphicPath, obstacles, symmetrical) - sets the properties of
        this block layout.

        graphicPath     A string representing the path to the graphic file
                        which describes the background of this block, or
                        None if no graphic file should be used.
        obstacles       Should be a sequence of obstacle definitions, each of
                        which should be of the form ((x1, y1), (dx, dy)).
                        Obstacles can be passed through in one direction only.
                        A solid block should be composed of obstacles defined
                        in a clockwise direction.
        platforms       Obstacles which can be fallen through.
        symmetrical     Boolean - is this block symmetrical? If set to True,
                        this block will also create a block which is the exact
                        mirror of this block.
        '''
        self.checksum = checksum
        self.kind = blockType
        self.filename = filename
        self.graphicsFilename = graphicsFilename
        self.graphicsIO = graphicsIO

        # Set up the graphic.
        if graphicsIO is None:
            if graphicPath:
                # Check that the graphic exists.
                if not os.path.exists(graphicPath):
                    raise IOError('Graphic file does not exist: %s' %
                            graphicPath)
            self.graphics = FileBlockGraphics(graphicPath)
        else:
            self.graphics = StreamBlockGraphics(graphicsIO)

        # Record obstacles.
        self.obstacles = []
        for obstacle in obstacles:
            self.obstacles.append(obstacle)

        self.platforms = []
        for platform in platforms:
            self.platforms.append(tuple(platform))

        # If it's not symmetrical, create a mirror block.
        if symmetrical:
            self.mirrorLayout = self
        else:
            self.mirrorLayout = BlockLayout()
            self.mirrorLayout.reversed = True
            self.mirrorLayout.mirrorLayout = self
            self.mirrorLayout.checksum = checksum
            if graphicsIO is None:
                self.mirrorLayout.graphics = FileBlockGraphics(graphicPath,
                        True)
            else:
                self.mirrorLayout.graphics = StreamBlockGraphics(graphicsIO,
                        True)
            self.mirrorLayout.kind = self.kind
            self.mirrorLayout.filename = self.filename
            self.mirrorLayout.graphicsFilename = self.graphicsFilename
            self.mirrorLayout.graphicsIO = self.graphicsIO

            # Flip the obstacles.
            for obstacle in self.obstacles:
                mObstacle = []
                for (x, y) in obstacle:
                    mObstacle.insert(0, (-x, y))
                self.mirrorLayout.obstacles.append(tuple(mObstacle))
            for platform in self.platforms:
                x1, y1 = platform[0]
                dx = platform[1]
                x2 = x1 + dx
                self.mirrorLayout.platforms.append(((-x2, y1), dx))

    def applyTo(self, block):
        '''Applies this layout to the specified map block.'''
        block.layout = self
        block.graphics = self.graphics

        # Go through the obstacles and append them to the block's obstacles.
        for obstacle in self.obstacles:
            block.addObstacle(obstacle, self.reversed)

        for relPos, dx in self.platforms:
            block.addPlatform(relPos, dx, self.reversed)

        block.coalesceLayout()

    def getGraphicsData(self):
        if self.graphicsIO is not None:
            self.graphicsIO.seek(0)
            return self.graphicsIO.read()
        return open(self.graphicsFilename, 'rb').read()

class BaseBlockGraphics(object):
    '''Defers loading of graphic until needed.'''

    def __init__(self, reversed):
        self._miniGraphics = {}
        self._rawGraphic = None
        self._graphic = None
        self._reversed = reversed

    def getMini(self, scale):
        try:
            result = self._miniGraphics[scale]
        except KeyError:
            width = int(self.graphic.get_rect().width / scale + 0.5)
            height = int(self.graphic.get_rect().height / scale + 0.5)

            result = pygame.transform.smoothscale(self._rawGraphic, (width,
                    height))
            self._miniGraphics[scale] = result

        return result

    def _getGraphic(self):
        if self._graphic is not None:
            return self._graphic

        # Load the graphic.
        self._rawGraphic = pygame.image.load(self._getFile(), 'png')

        if self._reversed:
            # Flip the graphic.
            self._rawGraphic = pygame.transform.flip(self._rawGraphic, True,
                    False)

        self._graphic = self._rawGraphic.convert()
        self._graphic.set_colorkey((255, 255, 255))

        return self._graphic

    graphic = property(_getGraphic)

class StreamBlockGraphics(BaseBlockGraphics):
    def __init__(self, stream, reversed=False):
        BaseBlockGraphics.__init__(self, reversed)
        self._stream = stream

    def _getFile(self):
        result = StringIO(self._stream.getvalue())
        return result

class FileBlockGraphics(BaseBlockGraphics):
    '''Defers loading of graphic until needed.'''

    def __init__(self, filename, reversed=False):
        BaseBlockGraphics.__init__(self, reversed)
        self._filename = filename

    def _getFile(self):
        return self._filename

