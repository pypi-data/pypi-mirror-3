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

from trosnoth.gui.framework import framework
from trosnoth.gui.framework.elements import TextElement, Backdrop
from trosnoth.version import titleVersion

from trosnoth.gui.common import (Location, ScaledSize,
        FullScreenAttachedPoint)

class TrosnothBackdrop(framework.CompoundElement):
    def __init__(self, app):
        super(TrosnothBackdrop, self).__init__(app)

        backdropPath = app.theme.getPath('startupMenu', 'blackdrop.png')
        backdrop = Backdrop(app, backdropPath,
                app.theme.colours.backgroundFiller)

        # Things that will be part of the backdrop of the entire startup menu
        # system.
        verFont = self.app.screenManager.fonts.versionFont
        self.elements = [
            backdrop,
            TextElement(self.app, titleVersion, verFont,
                Location(FullScreenAttachedPoint(ScaledSize(-10,-10),
                'bottomright'), 'bottomright'),
                app.theme.colours.versionColour),
        ]

