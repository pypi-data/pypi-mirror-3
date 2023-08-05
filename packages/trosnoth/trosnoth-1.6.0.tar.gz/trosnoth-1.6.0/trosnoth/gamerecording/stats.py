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

from trosnoth.utils.components import Component, Plug, handler
from trosnoth.messages import (TaggingZoneMsg, PlayerStarsSpentMsg,
        GameStartMsg, GameOverMsg, ShotFiredMsg, RespawnMsg, PlayerKilledMsg,
        PlayerHitMsg, AddPlayerMsg, RemovePlayerMsg, PlayerHasUpgradeMsg,
        ShotAbsorbedMsg, AchievementProgressMsg)

from trosnoth.utils.utils import timeNow
from collections import defaultdict
from trosnoth.model.upgrades import upgradeOfType

# Known Issues:
#  * If a player shoots a turret, a shield, or a phase shift,
#    their shot will not register as hit.
#
# Things to check:
# * Does it count the very last tag, or has the game terminated before that?

class PlayerStatKeeper(object):
    '''Maintains the statistics for a particular player object'''
    def __init__(self, player, plug):
        self.player = player
        self.plug = plug

        # A: Recorded [A]ll game (including post-round)
        # G: Recorded during the main [G]ame only
        # P: Recorded [P]ost-Game only
        self.kills = 0           # G Number of kills they've made
        self.deaths = 0          # G Number of times they've died
        self.zoneTags = 0        # G Number of zones they've tagged
        self.zoneAssists = 0     # G Number of zones they've been in when their
                                 #   team tags it
        self.shotsFired = 0      # A Number of shots they've fired
        self.shotsHit = 0        # A Number of shots that have hit a target
        self.starsEarned = 0     # G Aggregate total of stars earned
        self.starsUsed = 0       # G Aggregate total of stars used
        self.starsWasted = 0     # G Aggregate total of stars died with
        self.roundsWon = 0       # . Number of rounds won
        self.roundsLost = 0      # . Number of rounds lost

        self.playerKills = defaultdict(int)    # A Number of kills against
                                               #   individual people
        self.playerDeaths = defaultdict(int)   # A Number of deaths from
                                               #   individual people
        self.upgradesUsed = defaultdict(int)   # G Number of each upgrade used

        self.timeAlive = 0.0     # G Total time alive
        self.timeDead = 0.0      # G Total time dead

        self.killStreak = 0      # G Number of kills made without dying
        self.currentKillStreak = 0
        self.tagStreak = 0       # G Number of zones tagged without dying
        self.currentTagStreak = 0
        self.aliveStreak = 0.0   # G Greatest time alive in one life
        self.lastTimeRespawned = None
        self.lastTimeDied = None
        self.lastTimeSaved = None

    def shotFired(self):
        self.shotsFired += 1

        if self.shotsFired >= 100:
            if self.accuracy() >= 0.10:
                self.sendAchievementProgress('accuracySmall')
            if self.accuracy() >= 0.15:
                self.sendAchievementProgress('accuracyMedium')
            if self.accuracy() >= 0.20:
                self.sendAchievementProgress('accuracyLarge')

        if self.totalPoints() >= 1337:
            self.sendAchievementProgress('statScore')

    def sendAchievementProgress(self, achievementId):
        if self.player.id == -1:
            # Player is no longer in game.
            return
        self.plug.send(AchievementProgressMsg(self.player.id, achievementId))

    def _updateStreaks(self, updateAlive):
        '''
        updateAlive will be set to True in three situations:
          1. if the player has just died
          2. if the player was alive when the game ended
          3. if the player was alive when they disconnected
        '''
        self.killStreak = max(self.killStreak, self.currentKillStreak)
        self.tagStreak = max(self.tagStreak, self.currentTagStreak)

        time = timeNow()

        if updateAlive:
            lastLife = time - self.lastTimeRespawned
            self.aliveStreak = max(self.aliveStreak, lastLife)
            self.timeAlive += lastLife
            if lastLife >= 180:
                self.sendAchievementProgress('aliveStreak')

        elif self.lastTimeDied is not None:
            self.timeDead += time - self.lastTimeDied

        self.currentKillStreak = 0
        self.currentTagStreak = 0

    def died(self, killer, stars):
        self.deaths += 1
        self.playerDeaths[killer] += 1
        self.starsWasted += stars

        time = timeNow()

        self._updateStreaks(True)

        self.lastTimeDied = time

        if self.timeAlive >= 1000:
            self.sendAchievementProgress('totalAliveTime')

        if self.timeAlive >= 300 and self.timeAlive >= (self.timeAlive +
                self.timeDead) * 0.75:
            self.sendAchievementProgress('stayingAlive')

    def respawned(self):
        time = timeNow()

        if self.lastTimeDied is not None:
            self.timeDead += (time - self.lastTimeDied)

        self.lastTimeRespawned = time

    def goneFromGame(self):
        self._updateStreaks(not self.player.ghost)

    def gameOver(self, winningTeamId):
        self._updateStreaks(not self.player.ghost)
        winningTeam = self.player.universe.getTeam(winningTeamId)
        if winningTeam is None:
            # Draw. Do nothing
            pass
        elif self.player.isEnemyTeam(winningTeam):
            self.roundsLost += 1
        else:
            self.roundsWon += 1

    def killed(self, victim):
        self.kills += 1
        self.playerKills[victim] += 1
        self.currentKillStreak += 1
        self.starsEarned += 1

        self.killStreak = max(self.killStreak, self.currentKillStreak)

    def zoneTagged(self):
        self.zoneTags += 1
        self.currentTagStreak += 1
        self.starsEarned += 1

        self.tagStreak = max(self.tagStreak, self.currentTagStreak)

    def tagAssist(self):
        self.zoneAssists += 1

    def shotHit(self):
        self.shotsHit += 1

    def usedStars(self, stars):
        self.starsUsed += stars

        if self.starsUsed >= 20 and self.starsUsed >= self.starsEarned * 0.5:
            self.sendAchievementProgress('useStarsEfficiently')

    def upgradeUsed(self, upgradeType):
        self.upgradesUsed[upgradeType] += 1


    def totalPoints(self):
        points = 0
        points += self.kills        * 10
        points += self.deaths       * 1
        points += self.zoneTags     * 20
        points += self.zoneAssists  * 5
        points += self._accuracyPoints()

        return points

    def _accuracyPoints(self):
        if self.shotsFired == 0:
            return 0
        return ((self.shotsHit ** 2.) / self.shotsFired) * 30

    def accuracy(self):
        if self.shotsFired == 0:
            return 0
        return self.shotsHit * 1. / self.shotsFired

    # Probably fallible, as players could rejoin with the same name.
    def statDict(self):
        #self.saveAllStreaks()
        stats = {}
        for val in ('aliveStreak', 'deaths', 'killStreak', 'kills',
                'roundsLost', 'roundsWon', 'shotsFired', 'shotsHit',
                'starsEarned', 'starsUsed', 'starsWasted', 'tagStreak',
                'timeAlive', 'timeDead', 'upgradesUsed', 'zoneAssists',
                'zoneTags'):
            stats[val] = getattr(self, val)
        stats['bot'] = self.player.bot
        stats['team'] = self.player.teamId
        stats['username'] = (self.player.user.username if self.player.user
                else None)

        # We've stored these dicts as player objects (meaning rejoins may be
        # credited in two places)
        # Here, we combine them by aggregating on player nick (which should be
        # the same)
        for attribute in 'playerKills', 'playerDeaths':
            dictionary = getattr(self, attribute)
            newDict = {}
            for item in dictionary.iteritems():
                newDict[item[0].nick] = item[1]
            stats[attribute] = newDict

        return stats

    def rejoined(self, player):
        self.player = player

class StatKeeper(Component):
    inPlug = Plug()

    def __init__(self, world, filename):
        Component.__init__(self)
        self.world = world
        self.filename = filename
        # In case the server dies prematurely, it's nice
        # To at least have the file there so that
        # future games don't accidentally point to this one.
        file = open(self.filename, 'w')
        file.write('{}')
        file.close()
        # A mapping of player ids to statLists
        # (Contains only players currently in the game)
        self.playerStatList = {}
        # A list of all statLists
        # (regardless of in-game status)
        self.allPlayerStatLists = []
        self.winningTeamId = None

    def save(self, force=False):
        if not force and self.world.gameIsInProgress():
            return
        stats = {}
        stats['players'] = {}
        for playerStat in self.allPlayerStatLists:
            stats['players'][playerStat.player.nick] = playerStat.statDict()
        if self.winningTeamId != None:
            stats['winningTeamId'] = self.winningTeamId
        file = open(self.filename, 'w')
        statString = json.dumps(stats, indent = 3)
        file.write(statString)
        file.flush()
        file.close()

    @inPlug.defaultHandler
    def ignore(self, msg):
        pass

    @handler(GameStartMsg, inPlug)
    def gameStarted(self, msg):
        pass

    @handler(RespawnMsg, inPlug)
    def playerRespawned(self, msg):
        self.playerStatList[msg.playerId].respawned()

    @handler(TaggingZoneMsg, inPlug)
    def zoneTagged(self, msg):
        self.playerStatList[msg.playerId].zoneTagged()
        zone = self.world.getZone(msg.zoneId)
        player = self.world.getPlayer(msg.playerId)
        for assistant in zone.players:
            if assistant.team == player.team and assistant != player:
                self.playerStatList[assistant.id].tagAssist()
        self.save()

    @handler(PlayerKilledMsg, inPlug)
    def playerKilled(self, msg):
        if msg.killerId == '\x00':
            return
        self.playerStatList[msg.targetId].died(self.world.getPlayer(
                msg.killerId), msg.stars)
        self.playerStatList[msg.killerId].killed(self.world.getPlayer(
                msg.targetId))
        if msg.shotId != 0 and msg.deathType == 'S':
            self.playerStatList[msg.killerId].shotHit()
        self.save()


    @handler(PlayerStarsSpentMsg, inPlug)
    def usedStars(self, msg):
        self.playerStatList[msg.playerId].usedStars(msg.count)

    @handler(AddPlayerMsg, inPlug)
    def addPlayer(self, msg):
        player = self.world.getPlayer(msg.playerId)
        statkeeper = None
        for sl in self.allPlayerStatLists:
            if sl.player.nick == player.nick:
                statkeeper = sl
                statkeeper.rejoined(player)
        if statkeeper is None:
            statkeeper = PlayerStatKeeper(player, self.world.eventPlug)
            self.allPlayerStatLists.append(statkeeper)
        self.playerStatList[msg.playerId] = statkeeper
        self.save()

    @handler(RemovePlayerMsg, inPlug)
    def removePlayer(self, msg):
        self.playerStatList[msg.playerId].goneFromGame()
        # Just remove this from the list of current players
        # (retain in list of all stats)
        del self.playerStatList[msg.playerId]

    @handler(GameOverMsg, inPlug)
    def gameOver(self, msg):
        self.winningTeamId = msg.teamId
        # Only credit current players for game over
        for playerStat in self.playerStatList.values():
            playerStat.gameOver(msg.teamId)
        self.save(force=True)

    @handler(ShotFiredMsg, inPlug)
    def shotFired(self, msg):
        self.playerStatList[msg.playerId].shotFired()


    @handler(ShotAbsorbedMsg, inPlug)
    @handler(PlayerHitMsg, inPlug)
    def playerHit(self, msg):
        self.playerStatList[msg.shooterId].shotHit()

    @handler(PlayerHasUpgradeMsg, inPlug)
    def upgradeUsed(self, msg):
        upgradeType = upgradeOfType[msg.upgradeType]
        upgradeString = upgradeType.name
        self.playerStatList[msg.playerId].upgradeUsed(upgradeString)

    def stop(self):
        self.save()
