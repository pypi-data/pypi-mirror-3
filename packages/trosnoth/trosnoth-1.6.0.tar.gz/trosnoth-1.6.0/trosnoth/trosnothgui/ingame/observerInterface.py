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
from trosnoth.gui.framework import framework


class ObserverInterface(framework.CompoundElement):
    def __init__(self, app, gameInterface):
        super(ObserverInterface, self).__init__(app)
        self.gameInterface = gameInterface
        self.keyMapping = gameInterface.keyMapping

    def processEvent(self, event):
        if (event.type == pygame.KEYDOWN and self.keyMapping.get(event.key,
                None) == 'menu'):
           self.gameInterface.showMenu()
