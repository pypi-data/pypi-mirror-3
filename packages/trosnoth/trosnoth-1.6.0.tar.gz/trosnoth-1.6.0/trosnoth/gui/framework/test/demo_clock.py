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

from trosnoth.gui.app import Application
from trosnoth.gui.framework import framework, elements, clock, timer
from trosnoth.utils.utils import timeNow
from trosnoth.gui.fonts.font import Font
from trosnoth.gui.common import Location, ScaledSize
import pygame
from random import randint, shuffle

class Interface(framework.CompoundElement):
    def __init__(self, app):
        super(Interface, self).__init__(app)
        backdrop = pygame.Surface(app.screenManager.scaledSize)
        backdrop.fill((128,0,128))
        t1 = timer.CountdownTimer(7)
        t2 = timer.Timer(startAt=1)
        t1.onCountedDown.addListener(t2.start)
        c1 = clock.Clock(self.app, t1, Location((150,50)), Font("KLEPTOCR.TTF", 30))
        c2 = clock.Clock(self.app, t2, Location((150,120)), Font("KLEPTOCR.TTF", 30), (255,255,255), (100,100,100))
        c2.setFixedSize(ScaledSize(100,100))
        c3 = clock.Clock(self.app, timer.Timer(startAt = 3594).start(), Location((190,230), 'bottomright'), Font("KLEPTOCR.TTF", 30))

        c4 = clock.Clock(self.app, timer.Timer(startAt = 0.00000).start(), Location((350,50)), Font("KLEPTOCR.TTF", 30),bgColour=(255,0,0))
        c5 = clock.Clock(self.app, timer.Timer(startAt = -0.16666).start(), Location((350,120)), Font("KLEPTOCR.TTF", 30),bgColour=(255,255,0))
        c6 = clock.Clock(self.app, timer.Timer(startAt = -0.33333).start(), Location((350,190)), Font("KLEPTOCR.TTF", 30),bgColour=(0,255,0))
        c7 = clock.Clock(self.app, timer.Timer(startAt = -0.50000).start(), Location((350,260)), Font("KLEPTOCR.TTF", 30),bgColour=(0,255,255))
        c8 = clock.Clock(self.app, timer.Timer(startAt = -0.66666).start(), Location((350,330)), Font("KLEPTOCR.TTF", 30),bgColour=(0,0,255))
        c9 = clock.Clock(self.app, timer.Timer(startAt = -0.83333).start(), Location((350,400)), Font("KLEPTOCR.TTF", 30),bgColour=(255,0,255))
                        
        self.elements = [elements.PictureElement(app, backdrop), c1, c2, c3, c4, c5, c6, c7, c8, c9]
        t1.start()

size = (600,450)

if __name__ == '__main__':
    a = Application(size, 0, "Testing", Interface)
    a.run()
