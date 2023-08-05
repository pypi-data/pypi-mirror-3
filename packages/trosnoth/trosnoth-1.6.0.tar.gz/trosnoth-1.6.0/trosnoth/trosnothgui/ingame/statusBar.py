# Trosnoth (UberTweak Platform Game)
# Copyright (C) 2006-2009  Joshua Bartlett
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

'''statusBar.py - defines the StatusBar class which deals with drawing the
zone tallies onto the screen.'''

import random

import pygame

from trosnoth.gui.framework.elements import TextElement
from trosnoth.gui.common import Location
import trosnoth.gui.framework.framework as framework
from trosnoth.gui.framework.basics import Animation
from trosnoth.utils.utils import timeNow


class ZoneProgressBar(framework.CompoundElement):
    def __init__(self, app, world, gameViewer):
        super(ZoneProgressBar, self).__init__(app)
        self.world = world
        self.gameViewer = gameViewer
        self.app = app
        self.disrupt = False
        self.disruptTick = 0

        colours = app.theme.colours
        self.black = colours.black
        self.blue = colours.team1Mn_zone
        self.red = colours.team2Mn_zone
        self.grey = colours.zoneBarNeutral

        self.barFont = app.screenManager.fonts.zoneBarFont

        # Define a few constants to make things easier
        self.triangleLength = 25
        self.sideDistance = 4
        self.barHeight = self.gameViewer.zoneBarHeight
        self.textSpace = 130
        self.neutralTextSpace = 15

        self._oldRect = None
        self._oldScale = None
        self.width = None
        self.mapLeft = None
        self.mapRight = None
        self.mapBottom = None
        self.xFarLeft = None
        self.xFarRight = None
        self.xLeft = None
        self.xRight = None
        self.yTop = None
        self.yBottom = None
        self.disruptAnimation = None
        self.calculateSize()

    def calculateSize(self):
        minimapRect = self.gameViewer.miniMap.getRect()
        scaleFactor = self.app.screenManager.scaleFactor
        if minimapRect == self._oldRect and scaleFactor == self._oldScale:
            return
        self._oldRect = minimapRect
        self._oldScale = scaleFactor

        # Width will always be between 1 and 2 inclusive
        self.width = min(max(int(3 * scaleFactor), 1), 2)

        self.mapLeft = minimapRect.left
        self.mapRight = minimapRect.right
        self.mapBottom = minimapRect.bottom
        self.xFarLeft = self.mapLeft + self.sideDistance
        self.xFarRight = self.mapRight - self.sideDistance

        self.xLeft = self.xFarLeft + self.triangleLength
        self.xRight = self.xFarRight - self.triangleLength

        self.yTop = self.mapBottom - 1
        self.yBottom = self.yTop + self.barHeight

        # Create the disrupted animation
        self.disruptAnimation = self.createDisrupted()

    def draw(self, surface):
        self.calculateSize()
        super(ZoneProgressBar, self).draw(surface)

        if self.disrupt and random.random() < 0.2:
            disrupt = True
        else:
            disrupt = False

        # Automatically generated constants
        yTop = self.yTop
        yBottom = self.yBottom
        yText = yTop

        xFarLeft = self.xFarLeft
        xFarRight = self.xFarRight

        xLeft = self.xLeft
        xRight = self.xRight

        # Define the coordinates for the static shapes
        border = [
            (xFarLeft, yTop),
            (xFarRight, yTop),
            (xRight, yBottom),
            (xLeft, yBottom),
        ]

        blueTriangle = [
            (xFarLeft, yTop),
            (xLeft, yTop),
            (xLeft, yBottom),
        ]

        redTriangle = [
            (xFarRight, yTop),
            (xRight, yTop),
            (xRight, yBottom),
        ]

        # Get the information we need
        blueZones = self.world.teams[0].numOrbsOwned
        redZones = self.world.teams[1].numOrbsOwned
        totalZones = len(self.world.zones)
        neutralZones = totalZones - blueZones - redZones

        if blueZones == 0 or redZones == 0:
            gameOver = True
        else:
            gameOver = False

        # Define the coordinates for the dynamic shapes
        mutableBarLength = xRight - xLeft
        if redZones > 0:
            blueBarLength = round(mutableBarLength * ((blueZones * 1.0) /
                    totalZones))
        else:
            blueBarLength = mutableBarLength
        if blueZones > 0:
            redBarLength = round(mutableBarLength * ((redZones * 1.0) /
                    totalZones))
        else:
            redBarLength = mutableBarLength

        xNeutral = ((xLeft + blueBarLength) + (xRight - redBarLength)) / 2

        xFirstBar = xLeft + blueBarLength
        xSecondBar = xRight - redBarLength

        blueBar = [
            (xLeft, yTop),
            (xLeft + blueBarLength, yTop),
            (xLeft + blueBarLength, yBottom),
            (xLeft, yBottom),
        ]
        redBar = [
            (xRight - redBarLength, yTop),
            (xRight, yTop),
            (xRight, yBottom),
            (xRight - redBarLength, yBottom),
        ]
        greyBar = [
            (xLeft + blueBarLength + 1, yTop),
            (xRight - redBarLength - 1, yTop),
            (xRight - redBarLength - 1, yBottom),
            (xLeft + blueBarLength + 1, yBottom),
        ]

        # Draw the two triangles on the sides
        if blueZones > 0:
            pygame.draw.polygon(surface, self.blue, blueTriangle, 0)
        else:
            pygame.draw.polygon(surface, self.red, blueTriangle, 0)
        if redZones > 0:
            pygame.draw.polygon(surface, self.red, redTriangle, 0)
        else:
            pygame.draw.polygon(surface, self.blue, redTriangle, 0)

        # Draw the team colours
        if blueZones > 0:
            pygame.draw.polygon(surface, self.blue, blueBar, 0)
        if redZones > 0:
            pygame.draw.polygon(surface, self.red, redBar, 0)
        if neutralZones > 0 and not gameOver:
            pygame.draw.polygon(surface, self.grey, greyBar, 0)

        # Draw the black seperator line(s)
        if not gameOver:
            pygame.draw.line(surface, self.black, (xFirstBar, yTop),
                    (xFirstBar, yBottom), self.width)
            if neutralZones != 0:
                pygame.draw.line(surface, self.black, (xSecondBar, yTop),
                        (xSecondBar, yBottom), self.width)

        # Draw the disruption
        if disrupt:
            surface.blit(self.disruptAnimation.getImage(), (self.xFarLeft,
                    self.yTop))

        # Draw the border last so that it goes on top
        colours = self.app.theme.colours
        pygame.draw.polygon(surface, self.black, border, self.width)
        pygame.draw.line(surface, colours.minimapBorder, (self.mapLeft,
                self.mapBottom - 1), (self.mapRight, self.mapBottom - 1), 2)

        # Define the necessary text
        self.blueText = TextElement(self.app, '', self.barFont,
                Location((xFirstBar - 5, yText), 'topright'),
                colour=colours.black)
        self.neutralText = TextElement(self.app, '', self.barFont,
                Location((xNeutral, yText), 'midtop'), colour=colours.black)
        self.redText = TextElement(self.app, '', self.barFont,
                Location((xSecondBar + 7, yText), 'topleft'),
                colour=colours.black)

        if not disrupt:
            blueString = str(blueZones)
            redString = str(redZones)

            if xSecondBar - xFirstBar < self.neutralTextSpace:
                neutralString = ""
            else:
                neutralString = str(neutralZones)

            self.blueText.setText(blueString)
            self.redText.setText(redString)
            self.neutralText.setText(neutralString)
        else:
            self.blueText.setText('')
            self.redText.setText('')
            self.neutralText.setText('')

        # Draw the text
        if blueZones > 0:
            self.blueText.draw(surface)
        if redZones > 0:
            self.redText.draw(surface)
        if neutralZones > 0 and not gameOver:
            self.neutralText.draw(surface)

    def createDisrupted(self):
        screens = []
        for a in range(0,4):
            screen = (pygame.surface.Surface((self.xFarRight - self.xFarLeft,
                                              self.gameViewer.zoneBarHeight)))
            x = y = 0
            xL = 1
            xR = self.xFarRight - self.xFarLeft - 1
            rect = pygame.rect.Rect(0,0,2,2)
            disruptColours = [self.red, self.blue]
            while y < self.gameViewer.zoneBarHeight:
                while x < xR:
                    rect.left = x
                    rect.top = y
                    pygame.draw.rect(screen, random.choice(disruptColours),
                            rect, 0)
                    x += 2
                xL += 2
                xR -= 2
                x = xL
                y += 2
            screen.set_colorkey((0,0,0))
            screens.append(screen)
        return Animation(0.1, timeNow, *screens)
