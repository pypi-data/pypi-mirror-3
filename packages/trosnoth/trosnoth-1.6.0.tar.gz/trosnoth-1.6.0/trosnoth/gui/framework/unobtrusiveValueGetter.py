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

from trosnoth.gui.framework import framework, elements
from trosnoth.utils.event import Event
import pygame

class UnobtrusiveValueGetter(framework.Element):
    '''
    Gets some result from the use without obstructing normal use of the
    program.
    '''
    def __init__(self, app, pos, message, font, colour=(100, 100, 0),
            timer=None):
        framework.Element.__init__(self, app)
        self.drawIt = False
        self.text = elements.TextElement(app, message, font, pos, colour)
        if message:
            self.drawIt = True
        self.onGotValue = Event()

        if timer != None:
            self.timeRemaining = timer
        else:
            self.timeRemaining = None

    def draw(self, screen):
        if self.drawIt:
            self.text.draw(screen)

    def timerOver(self):
        self.drawIt = False

    def tick(self, deltaT):
        if self.timeRemaining is not None:
            self.timeRemaining -= deltaT
            if self.timeRemaining <=0:
                self.timeRemaining = None
                self.timerOver()

    def processEvent(self, event):
        if event.type == pygame.KEYDOWN:
            value = self.getValue(event.key)
            if value is not None:
                self.onGotValue.execute(value)
                return None
        return event

    def getValue(self, key):
        raise NotImplementedError, "This should be implemented in subclasses"

class NumberGetter(UnobtrusiveValueGetter):
    '''Gets numbers.'''
    def getValue(self, key):
        numKeys = {pygame.K_0: 0,
                   pygame.K_1: 1,
                   pygame.K_2: 2,
                   pygame.K_3: 3,
                   pygame.K_4: 4,
                   pygame.K_5: 5,
                   pygame.K_6: 6,
                   pygame.K_7: 7,
                   pygame.K_8: 8,
                   pygame.K_9: 9,
                   pygame.K_MINUS: 10,
                   pygame.K_KP0: 0,
                   pygame.K_KP1: 1,
                   pygame.K_KP2: 2,
                   pygame.K_KP3: 3,
                   pygame.K_KP4: 4,
                   pygame.K_KP5: 5,
                   pygame.K_KP6: 6,
                   pygame.K_KP7: 7,
                   pygame.K_KP8: 8,
                   pygame.K_KP9: 9,
                   pygame.K_KP_MINUS: 10,
                   pygame.K_RETURN: 0,
                   pygame.K_KP_ENTER: 0}

        return numKeys.get(key, None)

class YesNoGetter(UnobtrusiveValueGetter):
    '''Gets a boolean (y/n)'''
    def getValue(self, key):
        if key == pygame.K_y:
            return True
        elif key == pygame.K_n:
            return False
        else:
            return None

