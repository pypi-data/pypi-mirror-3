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

# At this point, the class is not expected to work. Just a dumping
# ground for existing code

class HuntingGameModeUniverse(Universe):
    def setHuntTeamWithZones(self, huntTeamWithZones):
        log.debug('Trying to hunt with %s' % (huntTeamWithZones,))
        # Firstly, if somehow all players are on the one zone, swap one to the
        # other team
        if len(self.players) < 4:
            return
        allTeams = set([])
        for player in self.players:
            allTeams.add(player.team)
        if len(allTeams) == 0:
            # No players in the game
            pass
        elif len(allTeams) == 1:
            player = random.choice(self.players)
            team = list(allTeams)[0].opposingTeam
            self.eventPlug.send(SetPlayerTeamMsg(player.id, team.id))
            WeakCallLater(3, self, 'setHuntedMode', team)
        else:
            # Now, check by who is alive and dead on each team
            playersWithoutZones = 0
            playersWithZones = 0
            playersToSpawn = []
            playersToSwapTeam = []
            for player in self.players:
                if player.ghost:
                    playersToSpawn.append(player)
                    if player.team == huntTeamWithZones:
                        playersToSwapTeam.append(player)
                else:
                    if player.team != huntTeamWithZones:
                        playersWithoutZones += 1
                    else:
                        playersWithZones += 1
            if playersWithoutZones < 2: # Having only one player won't work
                WeakCallLater(3, self, 'setHuntedMode',
                        huntTeamWithZones.opposingTeam)
            else:
                log.debug('Hunting!')
                self.huntTeamWithZones = huntTeamWithZones
                self.gameRules = GameRules.Hunting
                if playersWithZones == 0:
                    # We're about to swap everyone onto the one team. Stop this!
                    playersToSwapTeam.remove(random.choice(playersToSwapTeam))

                for p in playersToSwapTeam:
                    self.eventPlug.send(SetPlayerTeamMsg(p.id,
                            huntTeamWithZones.opposingTeam.id))
                for p in playersToSpawn:
                    self.eventPlug.send(RespawnMsg(p.id, player.currentZone.id))
                for zone in self.zones:
                    self.eventPlug.send(ZoneStateMsg(zone.id,
                            self.huntTeamWithZones.id, True, ''))

    @handler(PlayerKilledMsg, orderPlug)
    def playerKilled(self, msg):
        try:
            target = self.getPlayer(msg.targetId)
            shot = self.shotWithId(msg.killerId, msg.shotId)
            try:
                killer = self.playerWithId[msg.killerId]
            except KeyError:
                killer = None
            else:
                if not killer.ghost:
                    killer.incrementStars()

            target.die()

            if self.playerWithElephant == target:
                if not killer.ghost:
                    self.playerWithElephant = killer
                    self.eventPlug.send(PlayerHasElephantMsg(killer.id))
                else:
                    self.returnElephantToOwner()

            if self.gameRules == GameRules.Hunting:
                # Hunt mode
                if target.team != self.huntTeamWithZones:
                    i = 0
                    # Check number of remaining players on that team
                    for player in self.players:
                        if (player.team != self.huntTeamWithZones and player is
                                not target):
                            i += 1
                    if i > 1:
                        self.eventPlug.send(SetPlayerTeamMsg(target.id,
                                self.huntTeamWithZones.id))
                    else:
                        # The second last player on that team just died; change
                        # all zones now
                        self.setHuntTeamWithZones(
                                self.huntTeamWithZones.opposingTeam)

    def setHuntedMode(self, winningTeam):
        if winningTeam == None:
            huntTeamWithZones = random.choice(self.teams)
        else:
            huntTeamWithZones = winningTeam
        self.setHuntTeamWithZones(huntTeamWithZones)