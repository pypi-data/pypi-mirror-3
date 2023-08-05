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
from trosnoth.utils.twist import WeakCallLater

class StarGroup(framework.CompoundElement):
    def __init__(self, app):
        super(StarGroup, self).__init__(app)

    def _remove(self, starAn):
        self.elements.remove(starAn)
    def star(self, pos):
        self.elements.append(StarAnimation(self.app, pos, self))

class StarAnimation(elements.PictureElement):
    def __init__(self, app, pos, starGroup):
        pic = app.theme.sprites.star

        super(StarAnimation, self).__init__(app, pic, pos)

        self.pos = pos
        self.count = 0
        self.starGroup = starGroup
        WeakCallLater(0.1, self, 'advance')

    def advance(self):
        self.pos = (self.pos[0], self.pos[1] - 10)
        self.setPos(self.pos)
        self.count += 1
        if self.count < 5:
            WeakCallLater(0.1, self, 'advance')
        else:
            self.starGroup._remove(self)
