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

from trosnoth.model.universe_base import NeutralTeamId
import random

def preferredTeamOtherwiseSmallest(preferredTeamId, universe):
    if preferredTeamId != NeutralTeamId:
        return preferredTeamId
    else:
        playerCounts = universe.getTeamPlayerCounts()

        minCount = len(universe.players) + 1
        minTeams = []
        for team in universe.teams:
            count = playerCounts.get(team.id, 0)
            if count < minCount:
                minCount = count
                minTeams = [team.id]
            elif count == minCount:
                minTeams.append(team.id)
        return random.choice(minTeams)
    

class LobbyState(object):
    def canBuyUpgrades(self):
        return True

    def canRespawn(self):
        return True

    def canShoot(self):
        return True

    def becomeNeutralWhenDie(self):
        return True

    def getTeamToJoin(self, preferredTeamId, universe):
        return NeutralTeamId

    def canLeaveFriendlyTerritory(self):
        return True

    def aisEnabled(self):
        return True

    def canRename(self):
        return True

class PreGameState(object):
    def canBuyUpgrades(self):
        return False

    def canRespawn(self):
        return False

    def canShoot(self):
        return True

    def becomeNeutralWhenDie(self):
        return False

    def getTeamToJoin(self, preferredTeamId, universe):
        return preferredTeamOtherwiseSmallest(preferredTeamId, universe)

    def canLeaveFriendlyTerritory(self):
        return False

    def aisEnabled(self):
        return False

    def canRename(self):
        return True
        

class PracticeState(object):
    def canShoot(self):
        return False

    def canBuyUpgrades(self):
        return False

    def canRespawn(self):
        return True

    def becomeNeutralWhenDie(self):
        return False

    def getTeamToJoin(self, preferredTeamId, universe):
        return preferredTeamOtherwiseSmallest(preferredTeamId, universe)

    def canLeaveFriendlyTerritory(self):
        return True

    def aisEnabled(self):
        return False

    def canRename(self):
        return True

class SoloState(object):
    def canShoot(self):
        return True

    def canBuyUpgrades(self):
        return True

    def canRespawn(self):
        return True

    def becomeNeutralWhenDie(self):
        return False

    def getTeamToJoin(self, preferredTeamId, universe):
        return preferredTeamOtherwiseSmallest(preferredTeamId, universe)

    def canLeaveFriendlyTerritory(self):
        return True

    def aisEnabled(self):
        return True

    def canRename(self):
        return True

class GameInProgressState(object):
    def canShoot(self):
        return True

    def canBuyUpgrades(self):
        return True

    def canRespawn(self):
        return True

    def becomeNeutralWhenDie(self):
        return False

    def getTeamToJoin(self, preferredTeamId, universe):
        return preferredTeamOtherwiseSmallest(preferredTeamId, universe)

    def canLeaveFriendlyTerritory(self):
        return True

    def aisEnabled(self):
        return False

    def canRename(self):
        return False

class RabbitHuntState(object):
    def canBuyUpgrades(self):
        return True

    def canRespawn(self):
        return True

    def canShoot(self):
        return True

    def becomeNeutralWhenDie(self):
        return True

    def getTeamToJoin(self, preferredTeamId, universe):
        return NeutralTeamId

    def canLeaveFriendlyTerritory(self):
        return True

    def aisEnabled(self):
        return False

    def canRename(self):
        return False
