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

import logging

import os
import pygame
from trosnoth.data import getPath, user
from trosnoth.utils import unrepr
import trosnoth.version

log = logging.getLogger('settings')

class SettingsObject(object):
    '''
    Base class for defining settings objects. Defines some functionality for
    loading and saving settings.
    '''
    def __init__(self, app):
        self.app = app
        self.reset()

    def reset(self):
        data = self._loadSettingsFile()

        for attr, key, default in self.attributes:
            setattr(self, attr, data.get(key, default))

    def apply(self):
        pass

    def save(self):
        # Write to file
        fn = getPath(user, self.dataFileName)
        f = open(fn, 'w')
        data = {}
        for attr, key, default in self.attributes:
            data[key] = getattr(self, attr)
        f.write(repr(data))
        f.close()

    def _getSettingsFilename(self):
        return getPath(user, self.dataFileName)

    def _loadSettingsFile(self):
        filename = self._getSettingsFilename()
        try:
            f = open(filename, 'r')
            d = unrepr.unrepr(f.read())
            if not isinstance(d, dict):
                d = {}
        except IOError:
            d = {}
        return d

class DisplaySettings(SettingsObject):
    '''
    Stores the Trosnoth display settings.
    '''
    DEFAULT_THEME = 'default'
    dataFileName = 'display'
    attributes = (
        ('size', 'size', None),
        ('fullScreen', 'fullscreen', True),
        ('useAlpha', 'usealpha', True),
        ('smoothPanning', 'smoothPanning', False),
        ('windowsTranslucent', 'windowsTranslucent', False),
        ('centreOnPlayer', 'centreOnPlayer', True),
        ('fsSize', 'fsSize', None),
        ('theme', 'theme', DEFAULT_THEME),
        ('showObstacles', 'showObstacles', False),
    )

    def reset(self):
        SettingsObject.reset(self)

        if self.size is None:
            nWidth, nHeight = max(pygame.display.list_modes())
            self.size = (min(nWidth, 1024), min(nHeight, 768))
        if self.fsSize is None:
            self.fsSize = max(pygame.display.list_modes())

    def getSize(self):
        if self.fullScreen:
            return self.fsSize
        else:
            return self.size

    def apply(self):
        '''
        Apply the current settings.
        '''
        size = self.getSize()

        # Don't bother changing the screen if the settings that matter haven't
        # changed
        if (size != self.app.screenManager.size) or (self.fullScreen !=
                self.app.screenManager.isFullScreen()):
            # Tell the main program to change its screen size.
            self.app.changeScreenSize(size, self.fullScreen)

class SoundSettings(SettingsObject):
    dataFileName = 'sound'
    attributes = (
        ('soundEnabled', 'playSound', False),
        ('musicEnabled', 'playMusic', True),
        ('musicVolume', 'musicVolume', 100),
        ('soundVolume', 'soundVolume', 100),
    )

    def apply(self):
        '''
        Apply the current settings.
        '''

        if self.musicEnabled != self.app.musicManager.isMusicPlaying():
            if self.musicEnabled:
                self.app.musicManager.playMusic()
            else:
                self.app.musicManager.stopMusic()

        self.app.musicManager.setVolume(self.musicVolume)

        if self.soundEnabled:
            self.app.soundPlayer.setMasterVolume(self.soundVolume / 100.)
        else:
            self.app.soundPlayer.setMasterVolume(0)

class IdentitySettings(SettingsObject):
    dataFileName = 'identity'
    attributes = (
        ('nick', 'nick', None),
        ('usernames', 'usernames', None),
        ('firstTime', 'firstTime', True),
    )

    def __init__(self, app):
        self.app = app
        self.reset()

    def reset(self):
        SettingsObject.reset(self)
        if self.usernames is None:
            self.usernames = {}

    def setNick(self, nick):
        self.nick = nick
        self.save()

    def notFirstTime(self):
        self.firstTime = False
        self.save()

class ConnectionSettings(SettingsObject):
    dataFileName = 'connection'
    attributes = (
        ('servers', 'servers', None),
        ('otherGames', 'otherGames', True),
        ('lanGames', 'lanGames', 'afterInet'),
        ('createGames', 'createGames', True),
    )
    def __init__(self, app):
        SettingsObject.__init__(self, app)
        if self.servers is None:
            self.servers = [('localhost', 6787, 'http://localhost:8080/')]
            if trosnoth.version.release:
                self.servers.append(('play.trosnoth.org', 6787,
                        'http://play.trosnoth.org/'))
        else:
            # For developers who have saved settings.
            for i, s in enumerate(self.servers):
                if s == ('localhost', 6787):
                    self.servers[i] = ('localhost', 6787,
                            'http://localhost:8080/')
                elif len(s) == 2:
                    self.servers[i] = (s[0], s[1], 'http://%s/' % (s[0],))

class AlertSettings(SettingsObject):
    '''
    Stores the Trosnoth authentication server's settings related to when alert
    emails should be sent.

    Settings of the form "alertOnXXX" should have a value of True, False, or an
    email address. If an email address is given, it is the recipient email
    address of that kind of alert. If True, the default recipient address is
    used. If False, no alerts are sent for that alert kind.
    '''
    attributes = (
        ('senderAddress', 'senderAddress', 'trosnoth-server@localhost'),
        ('recipientAddress', 'recipientAddress', None),
        ('smtpServer', 'smtpServer', None),
        ('subject', 'subject', 'Alert from Trosnoth server'),
        ('alertOnGameNearlyFull', 'alertOnGameNearlyFull', True),
    )

    def __init__(self, dataPath):
        self.dataFileName = os.path.join(dataPath, 'alerts')
        self.reset()

    def _getSettingsFilename(self):
        return self.dataFileName

class AuthServerSettings(SettingsObject):
    '''
    Stores general settings for the authentication server.
    '''
    attributes = (
        ('keyLength', 'keyLength', 512),
        ('lobbySize', 'lobbySize', (2, 1)),
        ('maxPlayers', 'playersPerTeam', 5),
        ('allowNewUsers', 'allowNewUsers', True),
        ('privateMsg', 'privateMsg', None),
        ('elephantOwners', 'elephantOwners', ()),
        ('serverName', 'serverName', 'Trosnoth server'),
        ('homeUrl', 'homeUrl', None),
        ('hostName', 'hostName', None),
        ('xmppUsername', 'xmppUsername', None),
        ('xmppPassword', 'xmppPassword', None),
        ('showIdentityScreen', 'showIdentityScreen', False),
    )

    def __init__(self, dataPath):
        self.dataFileName = os.path.join(dataPath, 'settings')
        self.reset()

    def _getSettingsFilename(self):
        return self.dataFileName

    def reset(self):
        SettingsObject.reset(self)
        self.elephantOwners = set(p.lower() for p in self.elephantOwners)
        if self.privateMsg is None or len(self.privateMsg) == 0:
            self.privateMsg = 'This is a private server.'

    def createNotificationClient(self):
        '''
        Either returns an xmpp.NotificationClient or None.
        '''
        username = self.xmppUsername
        password = self.xmppPassword
        if (not username) or (not password):
            return None

        try:
            from trosnoth.network.xmpp import NotificationClient
        except ImportError, E:
            log.warning('Could not import xmpp notification client: %s', E)
            return None

        return NotificationClient(username, password)

class TournamentSettings(SettingsObject):
    '''
    Stores general settings for tournaments on the authentication server.
    '''
    attributes = (
        ('teamNames', 'teamNames', ()),
        ('minTeamSize', 'minTeamSize', 7),
        ('maxTeamSize', 'maxTeamSize', 8),
        ('mapSize', 'mapSize', (3, 2)),
        ('gameDuration', 'gameDuration', 2700),
    )

    def __init__(self, dataPath):
        self.dataFileName = os.path.join(dataPath, 'tournaments')
        self.reset()

    def _getSettingsFilename(self):
        return self.dataFileName
