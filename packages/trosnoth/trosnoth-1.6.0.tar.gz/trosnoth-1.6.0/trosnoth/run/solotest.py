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

import sys
import pygame

from trosnoth.game import makeLocalGame, makeIsolatedGame
from trosnoth.gui import app
from trosnoth.settings import DisplaySettings, SoundSettings, IdentitySettings
from trosnoth.themes import Theme
from trosnoth.trosnothgui.ingame.gameInterface import GameInterface
from trosnoth.gui.framework import framework
from trosnoth.model import mapLayout
from trosnoth.model.gameStates import SoloState

GAME_TITLE = 'Trosnoth Solo Mode'

class Main(app.MultiWindowApplication):
    def __init__(self, isolate=False, size=(1,1), aiCount=0, aiClass='alpha',
            mapBlocks=(), testMode=False, lobby=False, stackTeams=False):
        '''Initialise the game.'''
        pygame.init()
        self.size = size
        self.aiCount = aiCount
        self.isolate = isolate
        self.mapBlocks = mapBlocks
        self.testMode = testMode
        self.lobby = lobby
        self.stackTeams = stackTeams
        self.aiClass = aiClass

        self.displaySettings = DisplaySettings(self)
        self.soundSettings = SoundSettings(self)
        self.identitySettings = IdentitySettings(self)
        self.ais = []

        if self.displaySettings.fullScreen:
            options = pygame.FULLSCREEN
        else:
            options = 0

        pygame.font.init()
        super(Main, self).__init__(
            self.displaySettings.getSize(),
            options,
            GAME_TITLE,
            SoloInterface)

        # Set the master sound volume.
        self.soundSettings.apply()

        self.game = None
        self.startGame()

    def getConsoleLocals(self):
        result = {
            'game': self.game,
            'ais': self.ais,
        }
        return result

    def initialise(self):
        super(Main, self).initialise()

        # Loading the theme loads the fonts.
        self.theme = Theme(self)

    def getFontFilename(self, fontName):
        '''
        Tells the UI framework where to find the given font.
        '''
        return self.theme.getPath('fonts', fontName)

    def changeScreenSize(self, size, fullScreen):
        if fullScreen:
            options = pygame.locals.FULLSCREEN
        else:
            options = 0

        self.screenManager.setScreenProperties(size, options, GAME_TITLE)

    def startGame(self):
        db = mapLayout.LayoutDatabase(self, blocks=self.mapBlocks)
        self.game = game = makeLocalGame('Solo game', db, self.size[0],
                self.size[1], onceOnly=True)
        if not self.lobby:
            game.startGame()
        if self.testMode:
            game.world.setTestMode()
            
        self.game.world.setGameState(SoloState())

        # Create a client and an interface.
        if self.isolate:
            igame, eventPlug, controlPlug = makeIsolatedGame(db)
            self.igame = igame
            self.gi = gi = GameInterface(self, igame)
            game.addAgent(eventPlug, controlPlug)
            igame.addAgent(gi.eventPlug, gi.controller)
            igame.syncWorld()
        else:
            self.gi = gi = GameInterface(self, game)
            game.addAgent(gi.eventPlug, gi.controller)
        gi.onDisconnectRequest.addListener(self.stop)
        gi.onConnectionLost.addListener(self.stop)
        self.interface.elements.append(gi)
        
        self.ais[:] = []
        
        try:
            for i in xrange(self.aiCount):
                if self.stackTeams:
                    ai = game.addAI(self.aiClass, team=0)
                else:
                    ai = game.addAI(self.aiClass)
                self.ais.append(ai)
        except ImportError:
            print >> sys.stderr, 'AI module not found: %s' % (self.aiClass,)
            sys.exit(1)
        except AttributeError:
            print >> sys.stderr, ('AI module does not define AIClass: %s'
                    % (self.aiClass,))
            sys.exit(1)
            

    def stop(self):
        self.game.stop()
        super(Main, self).stop()

class SoloInterface(framework.CompoundElement):
    def __init__(self, app):
        super(SoloInterface, self).__init__(app)
        self.elements = []
