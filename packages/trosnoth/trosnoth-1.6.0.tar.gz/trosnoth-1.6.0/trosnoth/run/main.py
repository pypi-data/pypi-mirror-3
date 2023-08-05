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
from twisted.internet.error import CannotListenError

from trosnoth.game import makeLocalGame
from trosnoth.settings import (DisplaySettings, SoundSettings, IdentitySettings,
        ConnectionSettings)
from trosnoth.trosnothgui import interface
from trosnoth.themes import Theme
from trosnoth.model.mapLayout import LayoutDatabase
from trosnoth.network.lobby import UDPMulticaster
from trosnoth.network.networkDefines import serverVersion
from trosnoth.network.server import ServerNetHandler

from trosnoth.gui import app

from trosnoth.network.netman import NetworkManager

GAME_TITLE = 'Trosnoth'

class Main(app.MultiWindowApplication):
    '''Instantiating the Main class will set up the game. Calling the run()
    method will run the reactor. This class handles the three steps of joining
    a game: (1) get list of clients; (2) connect to a server; (3) join the
    game.'''

    standardInterfaceFactory = interface.Interface
    keySettingsInterfaceFactory = interface.KeySettingsInterface
    archivesInterfaceFactory = interface.ArchivesInterface
    singleInterfaceFactory = interface.SingleAuthInterface

    def __init__(self, serverDetails=None, screen=None):
        '''Initialise the game.'''
        pygame.init()

        self.serverDetails = serverDetails
        self.server = None
        self.serverInvisible = False
        self.initNetwork()

        self.displaySettings = DisplaySettings(self)
        self.soundSettings = SoundSettings(self)
        self.identitySettings = IdentitySettings(self)
        self.connectionSettings = ConnectionSettings(self)

        if self.displaySettings.fullScreen:
            options = pygame.FULLSCREEN
        else:
            options = 0

        pygame.font.init()
        if self.serverDetails is None and screen is None:
            iface = self.standardInterfaceFactory
        elif screen == 'keysettings':
            iface = self.keySettingsInterfaceFactory
        elif screen == 'archives':
            iface = self.archivesInterfaceFactory
        else:
            iface = self.singleInterfaceFactory

        super(Main, self).__init__( self.displaySettings.getSize(), options,
                GAME_TITLE, iface)

        # Set the master sound volume.
        self.soundSettings.apply()

        # Since we haven't connected to the server, there is no world.
        self.layoutDatabase = LayoutDatabase(self)

        # Start listening for game requests on the lan.
        self.multicaster = UDPMulticaster(self.getGames)

    def __str__(self):
        return 'Trosnoth Main Object'

    def getConsoleLocals(self):
        result = {
            'server': self.server,
        }
        try:
            result['game'] = self.interface.game
        except AttributeError:
            pass
        return result

    def initNetwork(self):
        # Set up the network connection.
        try:
            self.netman = NetworkManager(6789, 6789)
        except CannotListenError:
            # Set up a network manager on an arbitrary port (i.e.
            # you probably cannot run an Internet server because you
            # won't have port forwarding for the correct port.)
            self.netman = NetworkManager(0, None)

    def stopping(self):
        # Shut down the server if one's running.
        if self.server is not None:
            self.server.shutdown()

        self.multicaster.stop()
        super(Main, self).stopping()

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
            options = pygame.FULLSCREEN
        else:
            options = 0

        self.screenManager.setScreenProperties(size, options, GAME_TITLE)

    def startServer(self, serverName, halfMapWidth=3, mapHeight=2,
            maxPlayers=8, gameDuration=0, invisibleGame=False):
        if self.server is not None and self.server.running:
            return
        game = makeLocalGame(serverName, self.layoutDatabase, halfMapWidth,
                mapHeight, gameDuration * 60, maxPlayers)
        self.server = ServerNetHandler(self.netman, game)
        self.serverInvisible = invisibleGame

        self.server.onShutdown.addListener(self._serverShutdown)
        self.netman.addHandler(self.server)

    def getGames(self):
        '''
        Called by multicast listener when a game request comes in.
        '''
        if self.server and not self.serverInvisible:
            gameInfo = {
                'name': self.server.game.name,
                'version': serverVersion,
                'port': self.netman.getTCPPort(),
            }
            return [gameInfo]
        return []

    def _serverShutdown(self):
        self.netman.removeHandler(self.server)
        self.server = None
        self.serverInvisible = False
