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

'''
themes.py
This module defines the interface to the various different themes.
'''

import logging
import os
import pygame
from random import randrange

from trosnoth import data
from trosnoth.gui.fonts.font import Font, ScaledFont
from trosnoth.gui.framework.basics import SingleImage, Animation
from trosnoth.utils.unrepr import unrepr
from trosnoth.model.upgrades import Upgrade
from trosnoth.utils.utils import timeNow

BLOCK_BACKGROUND_COLOURKEY = (255, 255, 255)
BODY_BLOCK_SIZE = (1024, 384)
INTERFACE_BLOCK_SIZE = (512, 384)
BLOCK_OFFSETS = {
    'top': (-512, 0),
    'btm': (-512, -384),
    'fwd': ((-1536, -384), (0, 0)),
    'bck': ((-1536, 0), (0, -384)),
}

log = logging.getLogger('themes')

def teamColour(colourId):
    def colourFunction(self, team):
        return self.getTeamColour(team, colourId)
    return colourFunction

class ThemeColours(object):
    def getTeamColour(self, team, colourId):
        if team is None:
            teamNum = 0
        else:
            teamNum = ord(team.id) - 64
        return getattr(self, 'team%d%s' % (teamNum, colourId),
                getattr(self, 'team0%s' % (colourId,)))

    sysMessageColour = teamColour('msg')
    chatColour = teamColour('chat')
    miniMapZoneOwnColour = teamColour('Mn_zone')
    miniMapOrbOwnColour = teamColour('Mn_mk')
    miniMapPlayerColour = teamColour('Mn_pl')
    miniMapGhostColour = teamColour('Mn_gh')
    miniMapStarColour = teamColour('Mn_star')
    miniMapZoneHighlight = teamColour('Mn_highlight')
    leaderboard = teamColour('Leaderboard')

def cachedProperty(fn):
    def spriteFunction(self):
        try:
            return self._store[fn]
        except KeyError:
            self._store[fn] = result = fn(self)
            return result
    return property(spriteFunction)

def cached(fn):
    def spriteFunction(self, *args):
        try:
            return self._store[fn, args]
        except KeyError:
            self._store[fn, args] = result = fn(self, *args)
            return result
    return spriteFunction

def image(path, colourkey=(255, 255, 255), alpha=False):
    def imageFunction(self):
        return self.theme.loadSprite(path, colourkey, alpha)
    return cachedProperty(imageFunction)

def images(paths, colourkey=(255, 255, 255), alpha=False):
    def imageFunction(self):
        return self.theme.loadSprites(paths, colourkey, alpha)
    return cachedProperty(imageFunction)

def wrappedImage(path):
    def imageFunction(self):
        return SingleImage(self.theme.loadSprite(path))
    return cachedProperty(imageFunction)

def getTeamId(team):
    if team is None:
        return '\x00'
    return team.id

class ThemeSprites(object):
    def __init__(self, theme):
        self.theme = theme
        self._store = {}

    pointer = image('pointer.bmp')
    smallStar = image('smallstar.png')
    star = image('star.png')
    grenade = image('grenade.png')
    neutralOrb = image('greyOrb.png')
    scenery = image('scenery.png', colourkey=None)
    shoxGun3 = image('shoxgun-3.png')

    gunIcon = wrappedImage('gun.png')
    playerBody = wrappedImage('backbone.png')
    elephant = wrappedImage('elephant.png')
    christmasHat = wrappedImage('christmas.png')
    turretBase = wrappedImage('legs-turret.png')
    playerStanding = wrappedImage('legs-s.png')
    playerJumping = wrappedImage('legs-r3.png')
    ninjaHead = wrappedImage('ninjahead.png')
    jammingHatImage = image('jamminghat.png')
    jammingHatSparks = images(['jamminghat-spark1.png', 'jamminghat-spark2.png',
            'jamminghat-spark3.png'])

    runningLegs = images(['legs-r1.png', 'legs-r2.png',
            'legs-r3.png', 'legs-r4.png'])
    backwardsLegs = images(['legs-w0.png', 'legs-w1.png',
            'legs-w2.png', 'legs-w3.png'])

    shieldImages = images(['shieldImage1.png', 'shieldImage2.png',
            'shieldImage3.png', 'shieldImage2.png'])
    phaseShiftImages = images(['phaseShift1.png', 'phaseShift2.png',
            'phaseShift3.png', 'phaseShift4.png'])

    @cached
    def zoneHighlight(self, team, scale):
        colour = self.theme.colours.miniMapZoneHighlight(team)
        size = int(300. / scale + 0.5)
        result = pygame.Surface((2*size, 2*size))
        result.fill((0,0,0))
        result.set_colorkey((0,0,0))
        pygame.draw.circle(result, colour, (size, size), size)
        result.set_alpha(64)
        return result

    @cached
    def ghostAnimation(self, team):
        if team is not None:
            frames = self.theme.loadTeamSprites(['ghost1', 'ghost2', 'ghost3',
                    'ghost4', 'ghost3', 'ghost2'], team.id)
        else:
            lts = self.theme.loadTeamSprite
            frames = [
                lts('ghost1', 'A'), lts('ghost2', 'B'), lts('ghost3', 'A'),
                lts('ghost4', 'B'), lts('ghost3', 'A'), lts('ghost2', 'B')]
        return [Animation(0.25, timeNow, *frames)]

    @cached
    def ghostIcon(self, team):
        return SingleImage(self.theme.loadTeamSprite('ghost1',
                getTeamId(team)))

    def explosion(self):
        return Animation(0.07, timeNow, *(self.explosionFrame(i) for i in
                xrange(4)))

    def shoxwaveExplosion(self):
        return Animation(0.05, timeNow, *(self.shoxwaveFrame(i) for i in
                    xrange(3)))

    def jammingHat(self):
        images = []
        for spark in self.jammingHatSparks:
            images.append(spark)
            images.extend([self.jammingHatImage] * randrange(5, 15))
        return Animation(0.05, timeNow, *images)

    @cached
    def explosionFrame(self, frame):
        return self.theme.loadSprite('explosion%d.png' % (frame+1,))

    @cached
    def shoxwaveFrame(self, frame):
        return self.theme.loadSprite('shoxwave%d.png' % (frame+1,))

    @cached
    def playerHolding(self, team):
        return SingleImage(self.theme.loadTeamSprite('hold', getTeamId(team)))

    @cached
    def machineGunImages(self, team):
        return self.theme.loadTeamSprites([
            'machinegun-0', 'machinegun-1', 'machinegun-2',
            'machinegun-3', 'machinegun-4', 'machinegun-5',
            'machinegun-6', 'machinegun-7', 'machinegun-8'
        ], getTeamId(team))

    @cached
    def ricoGunImages(self, team):
        return self.theme.loadTeamSprites([
            'ricogun-0', 'ricogun-1', 'ricogun-2',
            'ricogun-3', 'ricogun-4', 'ricogun-5',
            'ricogun-6', 'ricogun-7', 'ricogun-8'
        ], getTeamId(team))

    @cached
    def gunImages(self, team):
        return self.theme.loadTeamSprites([
            'gun-0', 'gun-1', 'gun-2',
            'gun-3', 'gun-4', 'gun-5',
            'gun-6', 'gun-7', 'gun-8'
        ], getTeamId(team))

    @cached
    def playerHead(self, team, bot):
        teamId = getTeamId(team)
        if teamId == 'A':
            path = 'blue'
        elif teamId == 'B':
            path = 'red'
        elif teamId == '\x00':
            path = 'white'
        else:
            path = 'team' + teamId + 'Head'
        if bot:
            path += '-bot'
        return SingleImage(self.theme.loadSprite(path + '.png'))

    @cached
    def collectableStar(self, team):
        teamId = getTeamId(team)
        if teamId == 'A':
            path = 'blueStar.png'
        elif teamId == 'B':
            path = 'redStar.png'
        else:
            return self.star
        return self.theme.loadSprite(path)


    def teamGrenade(self, team):
        teamId = getTeamId(team)
        if teamId == 'A':
            path = 'blueGrenade.png'
        elif teamId == 'B':
            path = 'redGrenade.png'
        else:
            return self.grenade
        return self.theme.loadSprite(path)

    @cached
    def zoneBackground(self, team):
        if team is None:
            path = 'greyzone.png'
        elif team.id == 'A':
            path = 'bluezone.png'
        elif team.id == 'B':
            path = 'redzone.png'
        else:
            return self.zoneBackground(None)
        return self.theme.loadSprite(path)

    @cached
    def upgradeImage(self, upgradeType):
        assert issubclass(upgradeType, Upgrade)
        path = upgradeType.iconPath
        if path is None:
            path = 'upgrade-unknown.png'
        return self.theme.loadSprite(path, colourkey=upgradeType.iconColourKey)

    def blockBackground(self, block):
        return self.getBlockBackground(block, 'zone.png')

    def blockAlphaBackground(self, block):
        return self.getBlockBackground(block, 'alzone.png')

    def getBlockBackground(self, block, filename):
        bd = block.defn
        def ownerId(owner):
            if owner is None:
                return '\x00'
            return owner.id

        if bd.kind in ('top', 'btm'):
            if bd.zone is None:
                return None
            owners = (ownerId(block.zone.zoneOwner),)
        else:
            if bd.zone1 is None:
                owner1 = None
            else:
                owner1 = ownerId(block.zone1.zoneOwner)
            if bd.zone2 is None:
                owner2 = None
            else:
                owner2 = ownerId(block.zone2.zoneOwner)
            owners = (owner1, owner2)
        try:
            return self._store['blockBackground', filename, bd.kind, owners]
        except KeyError:
            pass
        self._buildBlockBackgrounds(filename)
        return self._store['blockBackground', filename, bd.kind, owners]

    def _buildBlockBackgrounds(self, filename):
        '''
        Loads and caches zone backgrounds for all combinations of block owners.
        '''
        zonePics = {
            '\x00': self.theme.loadSprite('grey%s' % (filename,)),
            'A': self.theme.loadSprite('blue%s' % (filename,)),
            'B': self.theme.loadSprite('red%s' % (filename,))
        }

        def storePic(kind, owners, pic):
            self._store['blockBackground', filename, kind, owners] = pic

        for kind in ('top', 'btm'):
            for ownerId, zonePic in zonePics.iteritems():
                pic = pygame.Surface(BODY_BLOCK_SIZE)
                pic.fill(BLOCK_BACKGROUND_COLOURKEY)
                pic.set_colorkey(BLOCK_BACKGROUND_COLOURKEY)
                pic.blit(zonePic, BLOCK_OFFSETS[kind])
                storePic(kind, (ownerId,), pic)
        for kind in ('fwd', 'bck'):
            for oid1 in (None, '\x00', 'A', 'B'):
                for oid2 in (None, '\x00', 'A', 'B'):
                    pic = pygame.Surface(INTERFACE_BLOCK_SIZE)
                    pic.fill(BLOCK_BACKGROUND_COLOURKEY)
                    pic.set_colorkey(BLOCK_BACKGROUND_COLOURKEY)
                    if oid1 is not None:
                        pic.blit(zonePics[oid1],
                                BLOCK_OFFSETS[kind][0])
                    if oid2 is not None:
                        pic.blit(zonePics[oid2],
                                BLOCK_OFFSETS[kind][1])
                    storePic(kind, (oid1, oid2), pic)


    @cached
    def orb(self, team):
        teamId = getTeamId(team)
        if teamId == 'A':
            path = 'blueOrb.png'
        elif teamId == 'B':
            path = 'redOrb.png'
        else:
            return self.neutralOrb
        return self.theme.loadSprite(path)

    @cached
    def shotAnimation(self, team):
        teamId = getTeamId(team)

        if teamId == 'A':
            colour = 'blue'
        elif teamId == 'B':
            colour = 'red'
        elif teamId == '\x00':
            colour = 'default'
        else:
            colour = 'team' + teamId
        return self.theme.makeShot(colour)

class Theme(object):
    def __init__(self, app):
        self.app = app
        self.paths = []
        self.colours = ThemeColours()
        self.sprites = ThemeSprites(self)
        self.setTheme("default")
##        self.setTheme(app.displaySettings.theme)

    def setTheme(self, themeName):
        '''
        Sets the theme to the theme with the given name.
        '''
        self.name = themeName
        self.paths = [data.getPath(data.user), data.getPath(data)]

        def insertPath(p):
            if os.path.exists(p):
                self.paths.insert(0, p)
        insertPath(data.getPath(data.themes, themeName))
        insertPath(data.getPath(data.user, 'themes', themeName))
        self.initFonts()
        self.initSounds()
        self.initColours()

    def initColours(self):
        colourPath = self.getPath('config', 'colours.cfg')
        colourData = self._getColourData(colourPath)
        defaultColours = self._getColourData(data.getPath(data))

        for colourName, colour in defaultColours.iteritems():
            if colourName in colourData:
                colour = colourData[colourName]
            setattr(self.colours, colourName, colour)

    def initSounds(self):
        self.app.soundPlayer.addSound('buyUpgrade.ogg', 'buyUpgrade', 1)
        self.app.soundPlayer.addSound('gameLose.ogg', 'gameLose', 1)
        self.app.soundPlayer.addSound('startGame.ogg', 'startGame', 1)
        self.app.soundPlayer.addSound('shoot.ogg', 'shoot', 3)
        self.app.soundPlayer.addSound('turret.ogg', 'turret', 1)
        self.app.soundPlayer.addSound('explodeGrenade.ogg', 'explodeGrenade', 1)

    def initFonts(self):
        fontData = self._getFontData()

        for fontName, defaultDetails in DEFAULT_FONTS.iteritems():
            if fontName in fontData:
                fontFile, size, bold = fontData[fontName]
            else:
                fontFile, size, bold = defaultDetails.unpack()

            if fontName in UNSCALED_FONTS:
                font = Font(fontFile, size, bold)
            else:
                font = ScaledFont(fontFile, size, bold)
            self.app.fonts.addFont(fontName, font)

    def _getFontData(self):
        try:
            fontLines = open(self.getPath('config', 'fonts.cfg')).readlines()
        except IOError:
            return {}

        result = {}
        for line in fontLines:
            bits = line.split("=")
            bits[2] = bits[2].strip()
            # Perform basic checks
            if len(bits) != 3 or not bits[2].isdigit():
                log.warning('Invalid font config line: %r', line)
            else:
                result[bits[0]] = (bits[1], int(bits[2]))
        return result

    def _getColourData(self, filepath):
        try:
            lines = open(self.getPath('config', 'colours.cfg')).readlines()
        except IOError:
            return {}

        result = {}
        for line in lines:
            line = line.strip()
            if line == '' or line.startswith('#'):
                continue
            bits = line.split("=", 1)
            # Perform basic checks
            invalid = False
            if len(bits) != 2:
                invalid = True
            else:
                try:
                    colour = unrepr(bits[1])
                    if type(colour) is str:
                        colour = colour.strip("'")
                except:
                    invalid = True
                else:
                    if colour in result.keys():
                        colour = result[colour]
                    else:
                        if (not isinstance(colour, tuple) or len(colour) < 3 or
                                len(colour) > 4):
                            invalid = True
            if invalid:
                log.warning('Invalid colour config line: %r', line)
            else:
                result[bits[0].strip()] = colour
        return result

    def getPath(self, *pathBits):
        '''
        Returns a path to the given themed file, looking in the following
        locations:
         1. User theme files for the current theme.
         2. Built-in theme files for the current theme.
         3. Default files.
        '''
        for path in self.paths:
            path = os.path.join(path, *pathBits)
            if os.path.isfile(path):
                return path
        raise IOError('file not found: %s' % (os.path.join(*pathBits),))

    def loadSprite(self, filename, colourkey=(255, 255, 255), alpha=False):
        '''
        Loads the sprite with the given name. A colour key of None may be given
        to disable colourkey transparency.
        '''
        filepath = self.getPath('sprites', filename)
        image = pygame.image.load(filepath)

        if alpha:
            image = image.convert_alpha()
        else:
            image = image.convert()

        if colourkey is not None:
            image.set_colorkey(colourkey)

        return image

    def loadSprites(self, filenames, colourkey=(255, 255, 255), alpha=False):
        images = []
        for filename in filenames:
            images.append(self.loadSprite(filename, colourkey, alpha))
        return images

    def makeShot(self, colour):
        '''
        Creates the shot sprite / animation. This is here because the Pirate
        theme needs the shot to spin, which it does not normally do.
        '''
        shotImg = self.loadSprite('%sShot.png' % (colour,))

        if self.name != 'pirate':
            return SingleImage(shotImg)

        numShotImages = 5
        degree = (360 / numShotImages)

        shots = [pygame.transform.rotate(shotImg, degree * i) for i in range(0,
                numShotImages)]
        return Animation(0.07, timeNow, *shots)

    def loadTeamSprite(self, filename, teamId):
        '''
        teamId must be 'A' or 'B'.
        If teamId is 'A', grabs <filename>.png
        If teamId is 'B', grabs <filename>b.png if it exists, or <filename>.png
            otherwise.
        '''
        if teamId == 'B':
            fullFilename = '%sb.png' % (filename,)
            try:
                filepath = self.getPath('sprites', fullFilename)
                if not os.path.isfile(filepath):
                    fullFilename = '%s.png' % (filename,)
            except IOError:
                fullFilename = '%s.png' % (filename,)
        else:
            fullFilename = '%s.png' % (filename,)

        return self.loadSprite(fullFilename)

    def loadTeamSprites(self, filenames, teamId):
        images = []
        for filename in filenames:
            images.append(self.loadTeamSprite(filename, teamId))
        return images

class F(object):

    def __init__(self, fontFile, size, bold = False):
        self.fontFile = fontFile
        self.size = size
        self.bold = bold

    def unpack(self):
        return (self.fontFile, self.size, self.bold)

DEFAULT_FONTS = {
    'default': F('Junction.ttf', 24),
    'defaultTextBoxFont': F('Junction.ttf', 20),
    'unobtrusivePromptFont': F('Junction.ttf', 28),
    'chatFont': F('Junction.ttf', 25),
    'newChatFont': F('Vera.ttf', 14, True),

    'winMessageFont': F('Junction.ttf', 72),

    'nameFont': F('Junction.ttf', 20),

    'hugeMenuFont': F('Junction.ttf', 54),
    'bigMenuFont': F('Junction.ttf', 36),
    'mainMenuFont': F('Junction.ttf', 36),
    'serverListFont': F('Junction.ttf', 24),
    'timerFont': F('Junction.ttf', 32),
    'consoleFont': F('orbitron-light.ttf', 20),
    'ampleMenuFont': F('Junction.ttf', 40),
    'mediumMenuFont': F('Junction.ttf', 36),
    'menuFont': F('Junction.ttf', 30),
    'smallMenuFont': F('Junction.ttf', 20),
    'ingameMenuFont': F('FreeSans.ttf', 12),
    'versionFont': F('Junction.ttf', 16),
    'scrollingButtonsFont': F('Junction.ttf', 24),
    'zoneBarFont': F('Junction.ttf', 24),
    'dialogButtonFont': F('KLEPTOCR.TTF', 50),
    'serverSelectionCheckboxesFont': F('Junction.ttf', 28),

    'customSizeButtonFont': F('KLEPTOCR.TTF', 100),

    'messageFont': F('Junction.ttf', 20),
    'leaderboardFont': F('KLEPTOCR.TTF', 21),

    'smallNoteFont': F('Junction.ttf', 22),
    'labelFont': F('Junction.ttf', 32),
    'captionFont': F('Junction.ttf', 35),
    'keymapFont': F('Junction.ttf', 20),
    'keymapInputFont': F('Junction.ttf', 20),

    'achievementTitleFont': F('orbitron-light.ttf', 21),
    'achievementNameFont': F('Junction.ttf', 18),

    'connectionFailedFont': F('Junction.ttf', 32),

    'creditsFont': F('Junction.ttf', 24),
    'creditsH2': F('KLEPTOCR.TTF', 48),
    'creditsH1': F('KLEPTOCR.TTF', 60),
}

UNSCALED_FONTS = set([
    'nameFont',
    'ingameMenuFont',
    'newChatFont'
])
