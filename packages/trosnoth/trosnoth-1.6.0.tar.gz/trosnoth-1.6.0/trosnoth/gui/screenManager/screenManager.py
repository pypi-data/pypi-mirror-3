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
import platform

import pygame

import screenFonts
from trosnoth.gui.framework import framework
from trosnoth.gui.common import Location

log = logging.getLogger('screenManager')

class SystemHotKeys(framework.Element):
    '''
    Traps a Ctrl+Break / Ctrl+Pause keypress and terminates the game.
    Traps an Alt+Tab keypress and minimises the game.
    '''
    def processEvent(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_SCROLLOCK, pygame.K_BREAK,
                    pygame.K_PAUSE) and (event.mod & pygame.KMOD_CTRL):
                log.warning('Trapped Ctrl+Break keypress: Quitting.')
                self.app.stop()
                return None
            if event.key == pygame.K_BACKSLASH and (event.mod &
                    pygame.KMOD_CTRL) and (event.mod & pygame.KMOD_META):
                log.warning('Trapped Ctrl+Meta+Backslash: Quitting.')
                self.app.stop()
                return None
            if (event.key == pygame.K_TAB and (event.mod & pygame.KMOD_ALT) and
                    self.app.screenManager.isFullScreen()):
                if platform.system() != 'Darwin':
                    # Minimise.
                    pygame.display.iconify()
                return None
        return event

class Pointer(framework.CompoundElement):
    def __init__(self, app, element):
        super(Pointer, self).__init__(app)
        assert hasattr(element, 'setPos')
        self.elements = [element]

    def draw(self, screen):
        try:
            pos = pygame.mouse.get_pos()
            self.elements[0].setPos(Location(pos, 'center'))
        except Exception, e:
            log.exception(str(e))
        super(Pointer, self).draw(screen)

class ScreenManager(framework.CompoundElement):
    '''Manages everything to do with the screen, especially any scaling due
    to the size of the screen.'''

    def __init__(self, app, size, settings, caption):
        super(ScreenManager, self).__init__(app)
        pygame.init()

        self.setScreenProperties(size, settings, caption)
        self.fonts = screenFonts.ScreenFonts()
        self.pointer = None
        self.interface = None
        self.terminator = SystemHotKeys(self.app)
        self.elements = [self.terminator]

    def setPointer(self, pointer):
        # Set up a sprite for the mouse pointer.
        self.elements.remove(self.terminator)
        if self.pointer is not None and self.pointer in self.elements:
            self.elements.remove(self.pointer)
        self.pointer = Pointer(self.app, pointer)
        self.elements.append(self.pointer)
        self.elements.append(self.terminator)


    def createInterface(self, element):
        self.interface = element(self.app)
        self.elements = [self.interface, self.terminator]
        if self.pointer is not None:
            self.elements.append(self.pointer)
        self.elements.append(self.terminator)


    def setScreenProperties(self, size, settings, caption):
        self.size = size

        pygame.display.set_caption(caption)
        self.settings = settings

        try:
            self.screen = pygame.display.set_mode(size, settings)
        except pygame.error:
            # Resolution not valid for this display: get the highest
            # valid resolution and use that instead
            resolutionList = pygame.display.list_modes()
            self.size = size = resolutionList[0]
            self.screen = pygame.display.set_mode(self.size, settings)

        self.scaleFactor = min(size[0] / 1024.,
                               size[1] / 768.)


        # Calculate corner offset for strange screen sizes.
        self.scaledSize = self.scale((1024, 768))
        self.offsets = ((size[0] - self.scaledSize[0]) / 2,
                        (size[1] - self.scaledSize[1]) / 2)

        self.rect = self.screen.get_rect()
        self.scaledRect = pygame.Rect(self.offsets, self.scaledSize)

    def finalise(self):
        pygame.mouse.set_visible(1)

    def isFullScreen(self):
        return (self.settings & pygame.FULLSCREEN) != 0

    def scale(self, point):
        '''Takes a point on a 1024x768 screen and scales it to this screen.'''
        return (int(point[0] * self.scaleFactor),
                int(point[1] * self.scaleFactor))

    def placePoint(self, point):
        '''Places the point from a 1024x768 screen onto the largest rectangle
        of that ratio that fits within this screen.'''
        return (int(point[0] * self.scaleFactor + self.offsets[0]),
                int(point[1] * self.scaleFactor + self.offsets[1]))

