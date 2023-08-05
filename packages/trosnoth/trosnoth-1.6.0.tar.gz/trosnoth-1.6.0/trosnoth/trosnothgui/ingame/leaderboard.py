# Trosnoth (UberTweak Platform Game)
# Copyright (C) 2006-2007  Joshua Bartlett
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

'''leaderboard.py - defines the LeaderBoard class which deals with drawing the
leader board to the screen.'''

import pygame
import struct

from trosnoth.data import getPath, sprites
import trosnoth.gui.framework.framework as framework
from trosnoth.gui.common import (Location, ScaledScalar,
        FullScreenAttachedPoint, SizedImage, ScaledSize)
from trosnoth.gui.framework import table
from trosnoth.gui.framework.elements import PictureElement
from trosnoth.model.universe_base import GameState
from trosnoth.utils.twist import WeakCallLater

# How often the leaderboard will update (in seconds)
UPDATE_DELAY = 1.0
SHORT_UPGRADE_NAMES = {
    'Minimap Disruption': 'minimap',
    'Phase Shift': 'phase',
}
# Upgrades that the enemy team have that you are allowed to see
PUBLIC_UPGRADES = ['Minimap Disruption', 'Turret', 'Shield', 'Grenade']

class LeaderBoard(framework.CompoundElement):

    def __init__(self, app, game, gameViewer):
        super(LeaderBoard, self).__init__(app)
        self.world = game.world
        self.gameController = game.gameController
        self.gameViewer = gameViewer
        self.app = app
        self.scale = self.app.screenManager.scaleFactor

        self.xPos = 4
        self.yPos = (self.gameViewer.miniMap.getRect().bottom +
                self.gameViewer.zoneBarHeight + 5)
        position = Location(FullScreenAttachedPoint((self.xPos, self.yPos),
                'topright'), 'topright')

        # Create the table and set all the appropriate style attributes
        self.playerTable = table.Table(app, position, columns = 3)

        self.playerTable.setBorderWidth(0)
        self.playerTable.setBorderColour((0, 0, 0))

        self.playerTable.style.backColour = None
        self.playerTable.style.foreColour = app.theme.colours.leaderboardNormal
        self.playerTable.style.font = app.screenManager.fonts.leaderboardFont
        self.playerTable.style.padding = (4, 1)
        self.playerTable.style.hasShadow = True
        self.playerTable.style.shadowColour = (0, 0, 0)

        self.playerTable.getColumn(0).style.textAlign = 'midright'
        self.playerTable.getColumn(1).style.textAlign = 'center'
        self.playerTable.getColumn(2).style.textAlign = 'midleft'

        self.rowHeight = 25

        self.playerTable.getColumn(0).setWidth(ScaledScalar(150))   # Name
        self.playerTable.getColumn(1).setWidth(ScaledScalar(25))    # Star
        self.playerTable.getColumn(2).setWidth(ScaledScalar(70))    # Upgrade

        self._resetPlayers()

        self.elements = [self.playerTable]
        self.update(True)

    def _resetPlayers(self):
        self.players = dict((k, []) for k in self.world.teamWithId)

    def update(self, loop=False):
        self._resetPlayers()

        if self.world.gameIsInProgress():
            yPos = self.yPos
        else:
            yPos = self.yPos + int(50 * self.scale)
        self.playerTable.pos = Location(FullScreenAttachedPoint(
                (self.xPos, yPos), 'topright'), 'topright')

        try:
            pi = self.gameViewer.interface.runningPlayerInterface
            self.friendlyTeam = pi.player.team
            self.spectator = False
        except (AttributeError, KeyError):
            # This will occur if the player is not yet on a team
            self.friendlyTeam = self.world.teamWithId['A']
            self.spectator = True

        for player in self.world.players:
            # getDetails() returns dict with pID, nick, team, dead, stars,
            # upgrade
            details = player.getDetails()
            self.players[details['team']].append(details)

        self._sort('A')
        self._sort('B')
        self._sort('\x00')
        self._updateTable()

        if loop:
            self.callDef = WeakCallLater(UPDATE_DELAY, self, 'update', True)

    def _sort(self, team):
        starList = []
        sortedList = []
        teamPlayers = self.players[team][:]

        for details in teamPlayers:
            if details['dead']:
                sortedList.append(details)
            else:
                starList.append(details['stars'])
                starList.sort()
                starList.reverse()

                sortedList.insert(starList.index(details['stars']), details)

        # List is now sorted with dead people at the bottom and the alive people
        # in order of stars.

        self.players[team] = sortedList[:]

    def _updateTable(self):
        for x in range(self.playerTable.rowCount()):
            self.playerTable.delRow(0)

        index = -1
        self.contents = []

        teamOrder = [self.friendlyTeam] + [t for t in self.world.teams if t !=
                self.friendlyTeam]
        if self.friendlyTeam is not None:
            teamOrder.append(None)
        for team in teamOrder:
            if team is None:
                teamId = '\x00'
            else:
                teamId = team.id
            # If we're in the lobby, only show real players
            shouldShow = lambda player: teamId != '\x00' or not player['bot']
            visiblePlayers = filter(shouldShow, self.players[teamId])
            if len(visiblePlayers) == 0:
                continue

            index = self._addTeamHeader(team, teamId, visiblePlayers, index)

            # Add a row for each player
            for player in visiblePlayers:
                index = self._addPlayerRow(team, teamId, player, index)

            # Add the 'star total' row
            index = self._addTeamFooter(team, teamId, visiblePlayers, index)

    def _addRow(self, index, height):
        index += 1
        self.playerTable.addRow()
        row = self.playerTable.getRow(index)
        row.setHeight(height)
        return index

    def _embedTeamHeaderStar(self, index):
        starImage = SizedImage(getPath(sprites, 'smallstar.png'),
                ScaledSize(14, 13), (255,255,255))
        xPos = int(1 * self.scale)
        yPos = int(5 * self.scale)
        starImage = PictureElement(self.app, starImage,
                Location(table.CellAttachedPoint((xPos,yPos),
                self.playerTable[1][index], 'topleft')))
        self.playerTable[1][index].elements = [starImage]

    def _writeTeamHeaderPlayerCount(self, players, index):
        if len(players) == 1:
            noun = 'player'
        else:
            noun = 'players'
        self.playerTable[2][index].setText(str(len(players)) + ' ' + noun)

    def _setTeamHeaderStatus(self, index, text, colour):
        cell = self.playerTable[2][index]
        cell.setText(text)
        cell.style.foreColour = colour

    def _addTeamHeader(self, team, teamId, players, index):
        index = self._addRow(index, ScaledScalar(self.rowHeight))
        self.playerTable[0][index].setText( self.world.getTeamName(teamId))

        if self.world.gameIsInProgress():
            self._embedTeamHeaderStar(index)
            self._writeTeamHeaderPlayerCount(players, index)
        else:
            self.playerTable[1][index].elements = []

        teamColour = self.app.theme.colours.leaderboard(team)
        if self.gameController.state() in (GameState.Lobby, GameState.PreGame,
                GameState.Starting):
            if team is None:
                pass
        elif self.gameController.state() == GameState.Ended:
            if team is None:
                pass
            elif self.world.getWinningTeam() == team:
                self._setTeamHeaderStatus(index, 'has won!', teamColour)
            elif self.world.getWinningTeam() is not None:
                self._setTeamHeaderStatus(index, 'has lost.', teamColour)
            else:
                self._setTeamHeaderStatus(index, 'has drawn!', teamColour)

        self.playerTable.getRow(index).style.foreColour = teamColour
        self.contents.append((index, 'header', team))

        return index

    def _addUpgradeText(self, team, player, index):
        if player['upgrade'] is None:
            upgradeText = ''
        elif (team != self.friendlyTeam and player['upgrade'] not in
                PUBLIC_UPGRADES and team is not None):
            upgradeText = ''
        else:
            if player['upgrade'] in SHORT_UPGRADE_NAMES:
                upgradeText = '+ ' + SHORT_UPGRADE_NAMES[player['upgrade']]
            else:
                upgradeText = '+ ' + player['upgrade'].lower()

        cell = self.playerTable[2][index]
        cell.setText(upgradeText)
        cell.style.foreColour = self.app.theme.colours.leaderboardNormal

    def _setPlayerColour(self, team, player, index):
        if player['dead']:
            colour = self.app.theme.colours.leaderboardDead
        else:
            colour = self.app.theme.colours.leaderboard(team)
        self.playerTable[0][index].style.foreColour = colour
        self.playerTable[1][index].style.foreColour = colour

    def _addPlayerRow(self, team, teamId, player, index):
        index = self._addRow(index, ScaledScalar(self.rowHeight))
        self.playerTable[0][index].setText(player['nick'])

        if self.gameController.state() not in (GameState.PreGame, GameState.Starting):
            if team is self.friendlyTeam or self.spectator:
                self.playerTable[1][index].setText(str(player['stars']))

            self._addUpgradeText(team, player, index)

        self._setPlayerColour(team, player, index)

        return index

    def _addTeamFooter(self, team, teamId, players, index):
        if (len(players) > 1 and self.gameController.state() not in
                (GameState.PreGame, GameState.Starting) and
                team is not None):
            index = self._addRow(index, ScaledScalar(self.rowHeight))
            self.playerTable[0][index].setText('Total:')
            teamStars = self.world.getTeamStars(team)
            self.playerTable[1][index].setText(teamStars)
            if teamStars == 1:
                noun = 'star'
            else:
                noun = 'stars'
            self.playerTable[2][index].setText(noun)
            self.contents.append((index, 'total', team))

        return index

    def kill(self):
        self.callDef.cancel()

    def draw(self, surface):
        super(LeaderBoard, self).draw(surface)

        # pointA = left-most point of the line
        # pointB = right-most point of the line
        # pointC = left-most point of the line shadow
        # pointD = right-most point of the line shadow

        for (index, rowKind, team) in self.contents:
            if rowKind == 'header':
                rightMargin = int(8 * self.scale)
                leftMargin = int(40 * self.scale)
                bottomMargin = int(2 * self.scale)

                point = self.playerTable._getRowPt(index + 1)
                pointA = (point[0] + leftMargin, point[1] - bottomMargin)
                pointB = (pointA[0] + self.playerTable._getSize()[0] -
                        leftMargin - rightMargin, pointA[1])
                pointC, pointD = shift(pointA, pointB)
                teamColour = self.app.theme.colours.leaderboard(team)
                pygame.draw.line(surface, teamColour, pointA, pointB, 1)
                pygame.draw.line(surface, (0, 0, 0), pointC, pointD, 1)

                pointA, pointB = shift(pointA, pointB,
                        -self.playerTable.getRow(index)._getHeight() +
                        bottomMargin, 0)
                pointC, pointD = shift(pointA, pointB)
                teamColour = self.app.theme.colours.leaderboard(team)
                pygame.draw.line(surface, teamColour, pointA, pointB, 1)
                pygame.draw.line(surface, (0, 0, 0), pointC, pointD, 1)

            elif rowKind == 'total':
                bottomMargin = int(2 * self.scale)

                rowPoint = self.playerTable._getRowPt(index)
                colPoint = self.playerTable._getColPt(1)
                pointA = (colPoint[0], rowPoint[1] - bottomMargin)
                pointB = (pointA[0] + self.playerTable.getColumn(1)._getWidth(),
                        pointA[1])
                pointC, pointD = shift(pointA, pointB)
                pygame.draw.line(surface,
                        self.app.theme.colours.leaderboardNormal, pointA,
                        pointB, 1)
                pygame.draw.line(surface, (0, 0, 0), pointC, pointD, 1)

def shift(pointA, pointB, down = 1, right = 1):
    '''Returns two points that are shifted by the specified number of pixels.
    Negative values shift up and left, positive values shift down and right.'''
    return ((pointA[0] + right, pointA[1] + down),
            (pointB[0] + right, pointB[1] + down))

