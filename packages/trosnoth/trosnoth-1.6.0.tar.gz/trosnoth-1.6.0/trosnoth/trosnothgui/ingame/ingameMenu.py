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
from trosnoth.gui.common import ScaledLocation

class InGameMenu(framework.CompoundElement):
    def __init__(self, app):
        super(InGameMenu, self).__init__(app)
        self.font = self.app.fonts.menuFont

    '''
    onClick can be expected to be a function with no parameters
    '''
    def button(self, height, text, hotkey, onClick=None):
        item = elements.TextButton(self.app, ScaledLocation(512, height,
                'center'), text, self.font,
                self.app.theme.colours.inGameButtonColour,
                self.app.theme.colours.white,
                hotkey)
        if onClick:
            item.onClick.addListener(lambda sender: onClick())
        return item
