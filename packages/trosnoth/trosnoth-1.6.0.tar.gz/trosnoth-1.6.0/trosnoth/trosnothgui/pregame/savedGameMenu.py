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
import time

from trosnoth.gui import browser

import trosnoth.gui.framework.framework as framework
from trosnoth.gui.framework.listbox import ListBox
from trosnoth.gui.framework.tab import Tab
from trosnoth.gui.framework.tabContainer import TabContainer, TabSize
from trosnoth.gui.framework.elements import (TextElement, TextButton,
        SizedPicture)
from trosnoth.gui.common import (Location, ScaledLocation, ScaledArea,
        AttachedPoint)
from trosnoth.gamerecording.gamerecorder import (RecordedGame,
        RecordedGameException, gameDir, gameExt, recordedGameVersion)
from trosnoth.utils.event import Event

from trosnoth.data import getPath, user, makeDirs

log = logging.getLogger('savedGameMenu')

class SavedGameMenu(framework.CompoundElement):
    def __init__(self, app, onCancel=None, onReplay=None):
        super(SavedGameMenu, self).__init__(app)

        area = ScaledArea(50, 140, 924, 570)
        bg = pygame.Surface((924, 500))
        bg.fill(app.theme.colours.replayMenu)
        if app.displaySettings.useAlpha:
            bg.set_alpha(192)

        font = self.app.screenManager.fonts.ampleMenuFont

        self.tabContainer = TabContainer(self.app, area, font,
                app.theme.colours.replayTabBorder)
        bp = SizedPicture(app, bg, Location(AttachedPoint((0,0),
                self.tabContainer._getTabRect)), TabSize(self.tabContainer))

        self.replayTab = SavedGameTab(app, self.tabContainer, onCancel=onCancel,
                onReplay=onReplay)
        self.tabContainer.addTab(self.replayTab)

        self.elements = [bp, self.tabContainer]

class SavedGameTab(Tab):

    def __init__(self, app, tabContainer, onCancel=None, onReplay=None):
        super(SavedGameTab, self).__init__(app, 'Saved Games')
        self.app = app
        self.tabContainer = tabContainer
        self.onCancel = Event(onCancel)
        self.onReplay = Event(onReplay)

        font = self.app.screenManager.fonts.ampleMenuFont
        smallFont = self.app.screenManager.fonts.menuFont
        colours = app.theme.colours

        # Static text
        self.staticText = [
            TextElement(self.app, 'server details:', font,
                    ScaledLocation(960, 200, 'topright'),
                    colours.headingColour),
            TextElement(self.app, 'date and time:', font,
                    ScaledLocation(960, 370, 'topright'),
                    colours.headingColour),
            TextElement(self.app, 'replay:', font,
                    ScaledLocation(620, 550, 'topleft'), colours.headingColour),
            TextElement(self.app, 'stats:', font,
                    ScaledLocation(620, 605, 'topleft'), colours.headingColour)]

        # Dynamic text
        self.listHeaderText = TextElement(self.app, 'available game files:',
                font, ScaledLocation(65, 200), colours.headingColour)
        self.noFiles1Text = TextElement(self.app, '', font,
                ScaledLocation(65, 260), colours.noGamesColour)
        self.noFiles2Text = TextElement(self.app, '', font,
                ScaledLocation(65, 310), colours.noGamesColour)
        self.serverNameText = TextElement(self.app, '', smallFont,
                ScaledLocation(960, 255, 'topright'), colours.startButton)
        self.serverDetailsText = TextElement(self.app, '', smallFont,
                ScaledLocation(960, 295, 'topright'), colours.startButton)
        self.dateText = TextElement(self.app, '', smallFont,
                ScaledLocation(960, 425, 'topright'), colours.startButton)
        self.lengthText = TextElement(self.app, '', smallFont,
                ScaledLocation(960, 465, 'topright'), colours.startButton)
        self.noReplayText = TextElement(self.app, '', smallFont,
                ScaledLocation(960, 550, 'topright'), colours.noGamesColour)
        self.noStatsText = TextElement(self.app, '', smallFont,
                ScaledLocation(960, 605, 'topright'), colours.noGamesColour)

        self.dynamicText = [self.listHeaderText, self.noFiles1Text,
                self.noFiles2Text, self.serverNameText, self.serverDetailsText,
                self.dateText, self.lengthText, self.noReplayText,
                self.noStatsText]

        # Text buttons
        self.watchButton = TextButton(self.app,
                ScaledLocation(960, 550, 'topright'), '', font,
                colours.secondMenuColour, colours.white)
        self.watchButton.onClick.addListener(self.watchReplay)

        self.statsButton = TextButton(self.app,
                ScaledLocation(960, 605, 'topright'), '', font,
                colours.secondMenuColour, colours.white)
        self.statsButton.onClick.addListener(self.viewStats)

        self.refreshButton = TextButton(self.app,
                ScaledLocation(620, 665, 'topleft'), 'refresh', font,
                colours.secondMenuColour, colours.white)
        self.refreshButton.onClick.addListener(self.populateList)

        self.cancelButton = TextButton(self.app,
                ScaledLocation(960, 665, 'topright'), 'cancel', font,
                colours.secondMenuColour, colours.white)
        self.cancelButton.onClick.addListener(self._cancel)

        self.buttons = [self.watchButton, self.statsButton, self.refreshButton,
                self.cancelButton]

        # Replay list
        self.gameList = ListBox(self.app, ScaledArea(65, 255, 500, 450),
                [], smallFont, colours.listboxButtons)
        self.gameList.onValueChanged.addListener(self.updateSidebar)

        # Combine the elements
        self.elementsFiles = (self.staticText + self.dynamicText + self.buttons
                + [self.gameList])
        self.elementsNoFiles = self.dynamicText + self.buttons

        # Populate the list of replays
        self.populateList()

    def _cancel(self, sender):
        self.onCancel.execute()

    def populateList(self, sender=None):

        # Clear out the sidebar
        for item in self.dynamicText:
            item.setText('')
        self.listHeaderText.setText('available game files:')
        self.gameList.index = -1
        self.elements = self.elementsFiles[:]

        # Get a list of files with the name '*.tros'
        logDir = getPath(user, gameDir)
        makeDirs(logDir)
        fileList = []

        for fname in os.listdir(logDir):
            if os.path.splitext(fname)[1] == gameExt:
                fileList.append(fname)

        # Assume all files are valid for now
        validFiles = fileList[:]

        self.gameInfo = {}
        oldFound = False

        for fname in fileList:
            try:
                game = RecordedGame(os.path.join(logDir, fname))
            except RecordedGameException:
                validFiles.remove(fname)
                continue
            except:
                log.warning('invalid file: %s', fname)
                continue
            else:
                if game.recordedGameVersion != recordedGameVersion:
                    validFiles.remove(fname)
                    oldFound = True

            self.gameInfo[os.path.splitext(fname)[0]] = game

        # Sort the games with most recent first.
        items = [(v.unixTimestamp, n) for n, v in self.gameInfo.iteritems()]
        items.sort(reverse=True)
        items = [n for v,n in items]
        self.gameList.setItems(items)

        if len(self.gameInfo) == 0:
            self.elements = self.elementsNoFiles[:]
            self.listHeaderText.setText('0 available game files:')
            if oldFound:
                self.noFiles1Text.setText('Some games were found from')
                self.noFiles2Text.setText('previous Trosnoth versions')
            else:
                self.noFiles1Text.setText('You have not yet run any')
                self.noFiles2Text.setText('games on this computer')
        else:
            self.gameList.setIndex(0)
            self.updateSidebar(0)
            if len(self.gameInfo) == 1:
                self.listHeaderText.setText('1 available game file:')
            else:
                self.listHeaderText.setText('%d available game files:' %
                        len(self.gameInfo))

    def updateSidebar(self, listID):
        # Update the details on the sidebar
        displayName = self.gameList.getItem(listID)

        # Server title
        self.serverNameText.setText(self.gameInfo[displayName].alias)

        # Map size
        self.serverDetailsText.setText('Map size: %d x %d' %
                (self.gameInfo[displayName].halfMapWidth,
                self.gameInfo[displayName].mapHeight))

        # Date and time of match
        datePython = map(int, self.gameInfo[displayName].dateTime.split(','))
        dateString = time.strftime('%a %d/%m/%y, %H:%M', datePython)
        self.dateText.setText(dateString)

        # Length of match
        dateUnix = time.mktime(datePython)
        if self.gameInfo[displayName].wasFinished():
            lastUnix = self.gameInfo[displayName].gameFinishedTimestamp

            lengthSeconds = int(lastUnix - dateUnix)
            lengthMinutes, lengthSeconds = divmod(lengthSeconds, 60)

            secPlural = ('s', '')[lengthSeconds == 1]
            minPlural = ('s', '')[lengthMinutes == 1]
            if lengthMinutes == 0:
                lengthString = '%d second%s' % (lengthSeconds,secPlural)
            else:
                lengthString = '%d min%s, %d sec%s' % (lengthMinutes, minPlural,
                        lengthSeconds, secPlural)

            self.lengthText.setText(lengthString)
        else:
            self.lengthText.setText('')

        # Enable the replay button
        if (self.gameInfo[displayName].replayFilename is not None and
                os.path.exists(self.gameInfo[displayName].replayFilename)):
            self.watchButton.setText('watch')
            self.noReplayText.setText('')
        else:
            self.watchButton.setText('')
            self.noReplayText.setText('unavailable')

        # Enabled the stats button
        if (self.gameInfo[displayName].statsFilename is not None and
                os.path.exists(self.gameInfo[displayName].statsFilename)):
            self.statsButton.setText('view')
            self.noStatsText.setText('')
        else:
            self.statsButton.setText('')
            self.noStatsText.setText('unavailable')

    def watchReplay(self, sender):
        '''Watch replay button was clicked.'''
        # Try to create a replay server.
        self.onReplay.execute(self.gameInfo[
                self.gameList.getItem()].replayFilename)

    def viewStats(self, sender=None):
        '''View stats button was clicked.'''
        game = self.gameInfo[self.gameList.getItem()]

        self.htmlPath = game.generateHtmlFile()
        browser.openPage(self.app, self.htmlPath)

    def draw(self, surface):
        super(SavedGameTab, self).draw(surface)

        rect = self.tabContainer._getTabRect()
        verLineX = rect.left + (rect.width * 0.6)
        horLineY = rect.top + (rect.height * 0.68)

        colour = self.app.theme.colours.replayTabBorder

        pygame.draw.line(surface, colour, (verLineX, rect.top), (verLineX,
                rect.bottom), self.tabContainer._getBorderWidth())
        pygame.draw.line(surface, colour, (verLineX, horLineY), (rect.right,
                horLineY), self.tabContainer._getBorderWidth())
