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

from trosnoth.utils.event import Event
from trosnoth.gui.common import (Region, Canvas, Location)
from trosnoth.gui.framework import framework
from trosnoth.gui.framework.elements import (SolidRect, TextButton)
from trosnoth.model import mapLayout
from trosnoth.model.gameStates import SoloState
from trosnoth.game import makeLocalGame

SIZE = (3, 1)
AICOUNT = 5

class PractiseScreen(framework.CompoundElement):
    def __init__(self, app, onClose=None, onStart=None):
        super(PractiseScreen, self).__init__(app)

        self.onClose = Event()
        if onClose is not None:
            self.onClose.addListener(onClose)
        self.onStart = Event()
        if onStart is not None:
            self.onStart.addListener(onStart)

        if app.displaySettings.useAlpha:
            alpha = 192
        else:
            alpha = None
        bg = SolidRect(app, app.theme.colours.playMenu, alpha,
                Region(centre=Canvas(512, 384), size=Canvas(924, 500)))

        #colour = app.theme.colours.mainMenuColour
        #font = app.screenManager.fonts.consoleFont

        font = app.screenManager.fonts.bigMenuFont
        cancel = TextButton(app, Location(Canvas(512, 624), 'midbottom'),
                'Cancel', font, app.theme.colours.secondMenuColour,
                app.theme.colours.white, onClick=self.cancel)
        self.elements = [bg, cancel]

    def cancel(self, element):
        self.onClose.execute()

    def startGame(self):
        db = mapLayout.LayoutDatabase(self)
        game = makeLocalGame('Practice game', db, SIZE[0], SIZE[1], onceOnly=True)
        game.startGame()
        game.world.setGameState(SoloState())

        game.__ais = []      # To avoid garbage collection
        for i in xrange(AICOUNT):
            game.__ais.append(game.addAI('alpha'))

        self.onStart.execute(game)
