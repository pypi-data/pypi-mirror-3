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

import json

from trosnoth.gamerecording import replays, stats, statgeneration, achievements
from trosnoth.utils.components import Component, Plug, handler
from trosnoth.messages import (SetTeamNameMsg, WorldResetMsg,
        SetWorldParametersMsg)
from trosnoth.model.isolator import Isolator, WorldSettingsResponder
from trosnoth.network.networkDefines import validServerVersions, serverVersion
from trosnoth.data import getPath, user, makeDirs
import os
import time

gameDir = 'recordedGames'
gameExt = '.tros'
replayDir = os.path.join(gameDir, 'replays')
replayExt = '.trosrepl'
statDir = os.path.join(gameDir, 'stats')
statExt = '.trosstat'
htmlDir = os.path.join(gameDir, 'htmlStats')
achvDir = os.path.join(gameDir, 'achievements')
achvExt = '.trosachv'

def makeGameRecorder(world, gameController, layoutDatabase, idManager):
    gameRecorder = GameRecorder(world)
    w = WorldSettingsResponder(world, gameController, layoutDatabase)

    gameRecorder.inPlug.connectPlug(w.agentEvents)
    gameRecorder.outPlug.connectPlug(w.agentRequests)
    w.gameRequests.connectPlug(idManager.inPlug)
    w.gameEvents.connectPlug(idManager.outPlug)

    return gameRecorder

def getFilename(alias, directory, ext, multipleFiles = True):
    # Figure out the filename to use for the main file
    gamePath = getPath(user, directory)
    makeDirs(gamePath)
    copyCount = 0
    succeeded = False
    if multipleFiles:
        while not succeeded:
            filename = '%s (%s)%s' % (alias, str(copyCount), ext)
            filePath = os.path.join(gamePath, filename)
            succeeded = not os.path.exists(filePath)
            copyCount += 1
    else:
        filename = '%s%s' % (alias, ext)
        filePath = os.path.join(gamePath, filename)
    return filePath

# Separate from the server version, which is to do with the
# types and content of network messages.
recordedGameVersion = 2


class RecordedGameException(Exception):
    pass

class GameRecorder(Component):
    inPlug = Plug()
    outPlug = Plug()

    proxyInPlug = Plug()
    proxyOutPlug = Plug()

    def __init__(self, world):
        super(GameRecorder, self).__init__()
        self.alias = None
        self.world = None
        self.serverVersion = serverVersion
        self.fakeIsolator = Isolator(None, useRealWorld=False)
        self._initWorld(world)

    def _initWorld(self, world):
        self.world = world
        self.alias = self.world.gameName or 'unnamed game'

    @inPlug.defaultHandler
    def handleMessage(self, msg):
        self.proxyInPlug.send(msg)

    @handler(SetWorldParametersMsg, inPlug)
    def gotWorldParams(self, msg):
        self.proxyInPlug.send(msg)

    @handler(WorldResetMsg, inPlug)
    def resetWorld(self, msg):
        self.saveEverything()
        self.gameFile.gameFinished()
        self.reset()
        self.proxyInPlug.send(msg)

    def saveEverything(self):
        self.achievementManager.save()
        self.statRecorder.save()
        self.replayRecorder.stop()

    def reset(self):
        self.proxyInPlug.disconnectAll()
        self.proxyOutPlug.disconnectAll()
        self.fakeIsolator.gameEvents.connectPlug(self.proxyInPlug)
        self.fakeIsolator.gameRequests.connectPlug(self.proxyOutPlug)

        self.filename = getFilename(self.alias, gameDir, gameExt)
        self.replayFilename = getFilename(self.alias, replayDir, replayExt)
        self.statsFilename = getFilename(self.alias, statDir, statExt)
        self.achievementsFilename = getFilename('replace-this', achvDir,
                achvExt, False)
        self.gameFile = RecordedGameFile(self.filename, sVersion=serverVersion,
                alias=self.alias, replayFilename=self.replayFilename,
                statsFilename=self.statsFilename,
                halfMapWidth=self.world.map.layout.halfMapWidth,
                mapHeight=self.world.map.layout.mapHeight)
        self.gameFile.save()
        self.statRecorder = stats.StatKeeper(self.world, self.statsFilename)
        self.replayRecorder = replays.ReplayRecorder(self.world,
                self.replayFilename)
        self.achievementManager = achievements.AchievementManager(self.world,
                self.achievementsFilename)
        self.statRecorder.inPlug.connectPlug(self.proxyInPlug)
        self.replayRecorder.inPlug.connectPlug(self.proxyInPlug)
        self.achievementManager.inPlug.connectPlug(self.proxyInPlug)
        self.achievementManager.outPlug.connectPlug(self.proxyOutPlug)

    @proxyOutPlug.defaultHandler
    def outgoingMessage(self, msg):
        self.outPlug.send(msg)

    @handler(SetTeamNameMsg, inPlug)
    def teamNameChanged(self, msg):
        self.gameFile.teamNameChanged(msg.teamId, msg.name)
        self.proxyInPlug.send(msg)

    def begin(self):
        self.reset()
        self.fakeIsolator.begin()

    def stop(self):
        self.replayRecorder.stop()
        self.statRecorder.stop()
        self.achievementManager.stop()
        self.gameFile.gameFinished()


class RecordedGame(object):
    def __init__(self, filename):
        self.filename = filename
        self.gameFile = RecordedGameFile(self.filename)
        self.gameFile.load()
        if not self.gameFile.isValid():
            raise RecordedGameException, 'Invalid Game File'

    def serverInformation(self):
        return self.gameFile.serverInformation

    def wasFinished(self):
        return self.gameFile.wasFinished()

    def generateHtmlFile(self):
        '''
        Generate an html stats file, and return the url
        '''
        if self.gameFile.hasHtml():
            return self.gameFile.htmlFile
        self.htmlFile = getFilename(self.gameFile.alias, htmlDir, '.html')
        statgeneration.generateHtml(self.htmlFile, self.gameFile.statsFilename)
        self.gameFile.htmlGenerated(self.htmlFile)
        return self.htmlFile

    def __getattr__(self, attr):
        return getattr(self.gameFile, attr)

class RecordedGameFile(object):
    def __init__(self, filename, sVersion=None, alias=None, replayFilename=None,
            statsFilename=None, halfMapWidth=None, mapHeight=None):
        self.filename = filename
        self.serverInformation = {}
        self.serverInformation['recordedGameVersion'] = recordedGameVersion
        self.serverInformation['serverVersion'] = sVersion
        self.serverInformation['alias'] = alias
        self.serverInformation['replayFilename'] = replayFilename
        self.serverInformation['statsFilename'] = statsFilename
        self.serverInformation['dateTime'] = ','.join(map(str,time.localtime()))
        self.serverInformation['unixTimestamp'] = time.time()
        self.serverInformation['halfMapWidth'] = halfMapWidth
        self.serverInformation['mapHeight'] = mapHeight
        self.serverInformation['teamAname'] = 'Blue'
        self.serverInformation['teamBname'] = 'Red'

    def gameFinished(self):
        self.serverInformation['gameFinishedTimestamp'] = time.time()
        self.save()

    def teamNameChanged(self, teamId, teamName):
        self.serverInformation['team%sname' % (teamId,)] = teamName
        self.save()

    def htmlGenerated(self, filename):
        self.serverInformation['htmlFile'] = filename
        self.save()

    ##
    # Overwrites any existing file
    def save(self):
        # No value may be null
        for value in self.serverInformation.itervalues():
            assert value is not None
        file = open(self.filename, 'w')
        serverInfoString = json.dumps(self.serverInformation, indent = 4)
        file.write(serverInfoString)
        file.flush()
        file.close()

    def load(self):
        file = open(self.filename, 'r')
        lines = file.readlines()

        fullText = '\n'.join(lines)
        self.serverInformation = json.loads(fullText)

    def isValid(self):
        return self.serverInformation['serverVersion'] in validServerVersions

    def wasFinished(self):
        return self.serverInformation.has_key('gameFinishedTimestamp')

    def hasHtml(self):
        return self.serverInformation.has_key('htmlFile')

    def __getattr__(self, key):
        return self.serverInformation[key]
