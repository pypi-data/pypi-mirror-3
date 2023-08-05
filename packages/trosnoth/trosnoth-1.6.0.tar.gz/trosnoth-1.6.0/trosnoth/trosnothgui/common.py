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

from trosnoth.gui.framework.elements import TextButton
from trosnoth.gui.common import (Location, ScaledSize,
        ScaledScreenAttachedPoint)

def mainButton(app, text, onClick, pos, anchor='topleft', hugeFont=False,
        smallFont=False):
    pos = Location(ScaledScreenAttachedPoint(ScaledSize(pos[0], pos[1]),
            'topleft'), anchor)
    if hugeFont:
        font = app.screenManager.fonts.hugeMenuFont
    elif smallFont:
        font = app.screenManager.fonts.menuFont
    else:
        font = app.screenManager.fonts.mainMenuFont
    result = TextButton(app, pos, text, font, app.theme.colours.mainMenuColour,
            app.theme.colours.mainMenuHighlight)
    result.onClick.addListener(lambda sender: onClick())
    return result

def button(app, text, onClick, pos, anchor='topleft', hugeFont=False,
        smallFont=False, firstColour=None, secondColour=None):
    if firstColour is None:
        firstColour = app.theme.colours.secondMenuColour
    if secondColour is None:
        secondColour = app.theme.colours.mainMenuHighlight
    pos = Location(ScaledScreenAttachedPoint(ScaledSize(pos[0], pos[1]),
            anchor), anchor)
    if hugeFont:
        font = app.screenManager.fonts.hugeMenuFont
    elif smallFont:
        font = app.screenManager.fonts.menuFont
    else:
        font = app.screenManager.fonts.mainMenuFont
    result = TextButton(app, pos, text, font, firstColour, secondColour)
    result.onClick.addListener(lambda sender: onClick())
    return result
