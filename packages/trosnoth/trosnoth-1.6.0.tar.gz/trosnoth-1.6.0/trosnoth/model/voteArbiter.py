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

import random
import logging

from trosnoth.messages import SetPlayerTeamMsg, RemovePlayerMsg
from trosnoth.model.universe import DEFAULT_TEAM_NAME_1, DEFAULT_TEAM_NAME_2

log = logging.getLogger(__name__)

class VoteArbiter(object):
    def __init__(self, universe, eventPlug, gameStartMethod):
        self.universe = universe
        self.gameStartMethod = gameStartMethod
        self.eventPlug = eventPlug

    def getPlayers(self):
        return [p for p in self.universe.players if not p.bot]

    def getTeams(self):
        return self.universe.teams

    def startNewGameIfReady(self):
        if self.readyForTournament():
            self.startTournamentGame()
        elif self.readyForScratchMatch():
            self.startNewGame()

    def getReadyTournamentPlayersByTeam(self):
        tournamentTeams = {}
        for p in self.getPlayers():
            if p.prefersTournamentTeam and p.readyForTournament:
                tournamentTeams.setdefault(p.preferredTeam, []).append(p)
        return tournamentTeams

    def getReadyTournamentTeams(self):
        if not self.universe.authManager:
            return []

        tournamentTeams = self.getReadyTournamentPlayersByTeam()

        minReady = self.universe.authManager.tournamentSettings.minTeamSize
        return [t for t, players in tournamentTeams.items() if
                len(players) >= minReady]

    def readyForTournament(self):
        readyTeams = self.getReadyTournamentTeams()

        return len(readyTeams) >= 2

    def readyForScratchMatch(self):
        players = self.getPlayers()
        totalPlayers = len(players)

        readyPlayerCount = len([p for p in players if p.readyToStart])

        if totalPlayers < 2:
            return False
        return readyPlayerCount >= 0.8 * totalPlayers

    def startTournamentGame(self):
        players = self.getReadyTournamentPlayersByTeam()
        teams = self.getReadyTournamentTeams()

        while len(teams) > 2:
            teams.pop(random.randrange(len(teams)))

        settings = self.universe.authManager.tournamentSettings
        size = settings.mapSize
        duration = settings.gameDuration
        maxTeamSize = settings.maxTeamSize

        teamName1, teamName2 = teams
        players1 = players[teamName1][:maxTeamSize]
        players2 = players[teamName2][:maxTeamSize]

        log.info('Starting tournament match with %r vs %r', teamName1,
                teamName2)
        log.info('Duration %r, size %r', duration, size)
        self.assignTeamNames(teamName1, teamName2)
        self.assignPlayersToTeams(players1, players2)
        self.bootPlayers(p for p in self.getPlayers() if p not in players1 and p
                not in players2)

        self.gameStartMethod(duration, size)

    def assignTeamNames(self, teamName1, teamName2):
        # Set team names.
        self.getTeams()[0].teamName = teamName1
        self.getTeams()[1].teamName = teamName2

    def assignPlayersToTeams(self, players1, players2):
        for i, players in [(0, players1), (1, players2)]:
            team = self.getTeams()[i]
            for player in players:
                self.eventPlug.send(SetPlayerTeamMsg(player.id, team.id))
                player.team = team

    def bootPlayers(self, players):
        for player in players:
            self.universe.eventPlug.send(RemovePlayerMsg(player.id))

    def startNewGame(self):
        result = self._getNewTeams()
        if result is None:
            return
        teamName1, players1, teamName2, players2 = result

        size = self._getNewSize(min(len(players1), len(players2)))
        duration = self._getNewDuration(size)

        self.assignTeamNames(teamName1, teamName2)
        self.assignPlayersToTeams(players1, players2)

        self.gameStartMethod(duration, size)

    def _getNewDuration(self, mapSize):
        results = {}
        for player in self.getPlayers():
            duration = player.preferredDuration
            results[duration] = results.get(duration, 0) + 1
        items = results.items()
        items.sort(key=lambda (duration, count): count)
        items.reverse()
        duration, count = items[0]
        if results.get(0, 0) != count:
            return duration

        # Decide default based on map size.
        if mapSize == (3, 2):
            return 45 * 60
        elif mapSize == (1, 1):
            return 10 * 60
        elif mapSize == (5, 1):
            return 20 * 60
        else:
            return min(7200, 2 * 60 * (mapSize[0]*2+1) * (mapSize[1]*1.5))

    def _getNewSize(self, teamSize):
        '''
        Returns a new map size based on what players vote for, with the
        defaults (if most people select Auto) being determined by the size of
        the smaller team.
        '''
        results = {}
        for player in self.getPlayers():
            size = player.preferredSize
            results[size] = results.get(size, 0) + 1
        items = results.items()
        items.sort(key=lambda (size, count): count)
        items.reverse()
        size, count = items[0]
        if results.get((0, 0), 0) != count:
            return size

        # Decide size based on player count.
        if teamSize <= 3:
            return (1, 1)
        elif teamSize <= 4:
            return (5, 1)
        else:
            return (3, 2)

    def _getNewTeams(self):
        '''
        Returns (teamName1, players1, teamName2, players2) based on what teams
        people have selected as their preferred teams. Bots will not be put on
        any team.
        '''
        teamName1, players1, teamName2, players2, others = (
                self._getRelevantTeamPreferences())

        totalPlayers = len(self.getPlayers())
        fairLimit = (totalPlayers + 1) // 2
        if len(players1) == totalPlayers:
            # Don't start if everyone's on one team.
            return None

        if len(players1) > fairLimit:
            # Require every player on the disadvantaged team to be ready.
            for player in players2 + others:
                if not player.readyToStart:
                    return None

        random.shuffle(others)
        for player in others:
            count1 = len(players1)
            count2 = len(players2)
            if count1 > count2:
                players2.append(player)
            elif count2 > count1:
                players1.append(player)
            else:
                random.choice([players1, players2]).append(player)

        return teamName1, players1, teamName2, players2

    def _getRelevantTeamPreferences(self):
        '''
        Returns (teamName1, players1, teamName2, players2, otherPlayers) based
        on what teams people have selected as their preferred teams. Players who
        have not selected one of the two most popular teams will be in the
        otherPlayers collection.
        '''
        desiredTeams = self._getDesiredTeams()
        others = []
        if desiredTeams[0][0] == '':
            teamName, players = desiredTeams.pop(0)
            others.extend(players)

        if desiredTeams:
            teamName1, players1 = desiredTeams.pop(0)
        else:
            teamName1, players1 = '', []

        if desiredTeams:
            teamName2, players2 = desiredTeams.pop(0)
        else:
            teamName2, players2 = '', []

        for teamName, players in desiredTeams:
            others.extend(players)

        if teamName1 == '':
            teamName1 = (DEFAULT_TEAM_NAME_1 if teamName2 != DEFAULT_TEAM_NAME_1
                    else DEFAULT_TEAM_NAME_2)
        if teamName2 == '':
            teamName2 = (DEFAULT_TEAM_NAME_1 if teamName1 != DEFAULT_TEAM_NAME_1
                    else DEFAULT_TEAM_NAME_2)

        return teamName1, players1, teamName2, players2, others

    def _getDesiredTeams(self):
        '''
        Returns a sorted sequence of doubles of the form (teamName, players)
        where teamName is a unicode/string and players is a list of players. The
        sequence will be sorted from most popular to least popular.
        '''
        results = {}
        for player in self.getPlayers():
            teamName = player.preferredTeam
            results.setdefault(teamName, []).append(player)
        items = results.items()
        items.sort(key=lambda (teamName, players): (len(players), teamName))
        items.reverse()
        return items

