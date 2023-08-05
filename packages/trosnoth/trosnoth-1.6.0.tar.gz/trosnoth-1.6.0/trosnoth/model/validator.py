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

from math import pi
import random
from trosnoth.utils.components import Component, handler, Plug
from trosnoth.messages import (ChatMsg, BuyUpgradeMsg, PlayerStarsSpentMsg,
        PlayerHasUpgradeMsg, CannotBuyUpgradeMsg, DeleteUpgradeMsg,
        RespawnRequestMsg, CannotRespawnMsg, PreferredTeamSelectedMsg,
        RespawnMsg, FireShotMsg, ShootMsg, JoinRequestMsg, CannotJoinMsg,
        JoinApproved, UpdatePlayerStateMsg, AimPlayerAtMsg, RemovePlayerMsg,
        PlayerIsReadyMsg, SetPreferredTeamMsg, SetPreferredDurationMsg,
        SetPreferredSizeMsg, ChangeNicknameMsg, FireShoxwaveMsg, MarkZoneMsg,
        ChangePlayerLimitsMsg)
from trosnoth.model.universe import Abort
from trosnoth.model.universe_base import NeutralTeamId
from trosnoth.model.upgrades import Turret, MinimapDisruption, allUpgrades

EDGE_TURRET_BOUNDARY = 100
ORB_TURRET_BOUNDARY = 150

MAX_TEAM_NAME_LENGTH = 30
MAX_PLAYER_NAME_LENGTH = 30
MAX_MAP_HEIGHT = 10
MAX_HALF_WIDTH = 10
MAX_GAME_DURATION = 86400

class Validator(Component):
    '''
    Checks the validity of messages from the interface's controller plug
    against a universe.
    '''
    agentRequests = Plug()
    gameRequests = Plug()
    gameEvents = Plug()
    agentEvents = Plug()

    def __init__(self, world, maxPlayers=8, authTagManager=None,
            authRequired=True, maxTotalPlayers=40, alerter=None):
        super(Validator, self).__init__()
        self.world = world
        self.maxPlayers = maxPlayers
        self.maxTotalPlayers = min(2*maxPlayers, maxTotalPlayers)
        self.authTagManager = authTagManager
        self.authRequired = authRequired
        self.alerter = alerter

    @gameEvents.defaultHandler
    def passOn(self, msg):
        self.agentEvents.send(msg)

    @handler(ChangePlayerLimitsMsg, gameEvents)
    def setPlayerLimits(self, msg):
        self.maxPlayers = msg.maxPerTeam
        if msg.maxTotal == 0:
            self.maxTotalPlayers = 2 * msg.maxPerTeam
        else:
            self.maxTotalPlayers = min(2 * msg.maxPerTeam, self.maxTotal)

    @handler(MarkZoneMsg, agentRequests)
    def markZone(self, msg):
        self.gameRequests.send(msg)

    @handler(ShootMsg, agentRequests)
    def reqFireShot(self, msg):
        if not self.world.physics.shooting:
            return
        # This call will ultimately supercede the previous
        if not self.world.canShoot():
            return

        try:
            player = self.world.getPlayer(msg.playerId)
            shotType = player.getShotType()
            if shotType is None:
                return

            xpos, ypos = player.pos
            if player.shoxwave:
                self.gameRequests.send(FireShoxwaveMsg(msg.playerId,
                    xpos, ypos))
            else:
                self.gameRequests.send(FireShotMsg(msg.playerId,
                        player.angleFacing, xpos, ypos, shotType))
        except Abort:
            pass

    @handler(BuyUpgradeMsg, agentRequests)
    def reqUpgrade(self, msg):
        try:
            player = self.world.getPlayer(msg.playerId)
            if player.upgrade is not None:
                self.agentEvents.send(CannotBuyUpgradeMsg(msg.playerId, 'A',
                        msg.tag))
                return
            elif not self.world.canBuyUpgrades():
                self.agentEvents.send(CannotBuyUpgradeMsg(msg.playerId, 'P',
                        msg.tag))
                return
            elif player.ghost:
                self.agentEvents.send(CannotBuyUpgradeMsg(msg.playerId, 'D',
                        msg.tag))
                return

            upgrade = self.world.getUpgradeType(msg.upgradeType)
            if upgrade not in allUpgrades:
                self.agentEvents.send(CannotBuyUpgradeMsg(msg.playerId, 'I',
                        msg.tag))
                return

            if player.getTeamStars() < upgrade.requiredStars:
                self.agentEvents.send(CannotBuyUpgradeMsg(msg.playerId, 'N',
                        msg.tag))
                return

            reason = self._checkUpgradeConditions(player, upgrade)
            if reason is not None:
                self.agentEvents.send(CannotBuyUpgradeMsg(msg.playerId, reason,
                        msg.tag))
                return

            self._processUpgradePurchase(player, upgrade)
        except Abort:
            pass

    def _checkUpgradeConditions(self, player, upgrade):
        '''
        Checks whether the conditions are satisfied for the given player to be
        able to purchase an upgrade of the given kind. Returns None if no
        condition is violated, otherwise returns a one-byte reason code for why
        the upgrade cannot be purchased.
        '''
        if upgrade is Turret:
            zone = player.currentZone
            if not player.isFriendsWithTeam(zone.zoneOwner):
                return 'F'
            if zone.turretedPlayer is not None:
                return 'T'
            if player.currentMapBlock.fromEdge(player) < EDGE_TURRET_BOUNDARY:
                return 'E'

            distanceFromOrb = ((zone.defn.pos[0] - player.pos[0]) ** 2 +
                    (zone.defn.pos[1] - player.pos[1]) ** 2) ** 0.5
            if distanceFromOrb < ORB_TURRET_BOUNDARY:
                return 'O'
        elif upgrade is MinimapDisruption:
            if player.team is None or player.team.usingMinimapDisruption:
                return 'M'

        return None

    def _processUpgradePurchase(self, player, upgrade):
        '''
        Sends the required sequence of messages to gameRequests to indicate
        that the upgrade has been purchased by the player.
        '''
        remaining = upgrade.requiredStars

        # Take from the purchasing player first.
        fromPurchaser = min(player.stars, remaining)
        self.gameRequests.send(PlayerStarsSpentMsg(player.id, fromPurchaser))
        remaining -= fromPurchaser

        # Now take evenly from other team members.
        if remaining > 0:
            players = []
            totalStars = 0
            for p in self.world.players:
                if p.team == player.team and p.id != player.id and p.stars > 0:
                    players.append(p)
                    totalStars += p.stars
            # Order by descending number of stars
            # Shuffle first to avoid biasing any player with the same number of
            # stars as another
            random.shuffle(players)
            players.sort(cmp=lambda p1, p2:cmp(p1.stars, p2.stars))
            players.reverse()

            for p in players:
                fraction = remaining / (totalStars + 0.)
                toGive = int(round(fraction * p.stars))
                remaining -= toGive
                totalStars -= p.stars
                self.gameRequests.send(PlayerStarsSpentMsg(p.id, toGive))
            # Everything should add up
            assert remaining == 0
            assert totalStars == 0

        self.gameRequests.send(PlayerHasUpgradeMsg(player.id,
                upgrade.upgradeType, "B"))

    def isValidNick(self, nick):
        if len(nick) < 2 or len(nick) > MAX_PLAYER_NAME_LENGTH:
            return False
        return True

    @handler(JoinRequestMsg, agentRequests)
    def reqJoinGame(self, msg):
        preferredTeamId = msg.teamId
        nick = msg.nick.decode()
        teamPlayerCounts = self._getTeamPlayerCounts()

        if len(self.world.players) >= self.maxTotalPlayers:
            self.agentEvents.send(CannotJoinMsg('F', msg.teamId, msg.tag))
            return

        teamId = self.world.getTeamToJoin(preferredTeamId)
        if teamId != NeutralTeamId and teamPlayerCounts.get(teamId, 0) >= self.maxPlayers:
            self.agentEvents.send(CannotJoinMsg('F', msg.teamId, msg.tag))
            return

        if not self.isValidNick(nick):
            self.agentEvents.send(CannotJoinMsg('B', msg.teamId, msg.tag))
            return

        if self.authTagManager is not None and not msg.localBotRequest:
            user = self.authTagManager.checkAuthTag(msg.authTag)
            if user is None:
                if self.authRequired:
                    self.agentEvents.send(CannotJoinMsg('A', msg.teamId,
                            msg.tag))
                    return
            else:
                for player in self.world.players:
                    if player.user == user:
                        self.agentEvents.send(CannotJoinMsg('U', msg.teamId,
                                msg.tag))
                        return
                if (nick.lower() != user.username and
                        self.authTagManager.checkUsername(nick)):
                    self.agentEvents.send(CannotJoinMsg('N', msg.teamId,
                            msg.tag))
                    return

        # Only check for duplicate nick after checking for auth-related errors.
        for player in self.world.players:
            if player.nick.lower() == nick.lower():
                self.agentEvents.send(CannotJoinMsg('N', msg.teamId, msg.tag))
                return

        if self.authTagManager is not None and not msg.localBotRequest:
            self.authTagManager.discardAuthTag(msg.authTag)
            username = user.username
            user.setNick(nick)
        else:
            username = ''

        self.gameRequests.send(JoinApproved(teamId, msg.tag,
                self._selectZone(teamId), msg.nick, username, msg.bot))

        maxTotalPlayers = min(self.maxTotalPlayers, 2 * self.maxPlayers)
        if len(self.world.players) > 0.75 * maxTotalPlayers:
            self._sendNearlyFullAlert()

    def _sendNearlyFullAlert(self):
        teamPlayerCounts = self._getTeamPlayerCounts()
        if not self.alerter:
            return
        self.alerter.send('GameNearlyFull', '''
A Trosnoth game running on this server is nearly full.

Details:
    Game name: %r
    Team A: %r
    Team A players: %r
    Team B: %r
    Team B players: %r
    Rogue players: %r
    Maximum team size: %r
    Absolute maximum load: %r
''' % (self.world.gameName, self.world.teams[0].teamName,
            teamPlayerCounts.get(self.world.teams[0].id, 0),
            self.world.teams[1].teamName,
            teamPlayerCounts.get(self.world.teams[1].id, 0),
            teamPlayerCounts.get('\x00', 0),
            self.maxPlayers, self.maxTotalPlayers,

        ))

    def _selectZone(self, teamId):
        return self.world.selectZone(teamId).id

    def _getTeamPlayerCounts(self):
        return self.world.getTeamPlayerCounts()

    @handler(RespawnRequestMsg, agentRequests)
    def reqRespawn(self, msg):
        try:
            player = self.world.getPlayer(msg.playerId)
            if not self.world.canRespawn():
                self.agentEvents.send(CannotRespawnMsg(msg.playerId, 'P',
                        msg.tag))
            elif not player.ghost:
                self.agentEvents.send(CannotRespawnMsg(msg.playerId, 'A',
                        msg.tag))
            elif player.respawnGauge > 0:
                self.agentEvents.send(CannotRespawnMsg(msg.playerId, 'T',
                        msg.tag))
            elif not player.inRespawnableZone():
                self.agentEvents.send(CannotRespawnMsg(msg.playerId, 'E',
                        msg.tag))
            elif player.currentZone.frozen:
                self.agentEvents.send(CannotRespawnMsg(msg.playerId, 'F',
                        msg.tag))
            else:
                self.gameRequests.send(RespawnMsg(msg.playerId,
                        player.currentZone.id))
        except Abort:
            pass

    @handler(UpdatePlayerStateMsg, agentRequests)
    def reqUpdateState(self, msg):
        try:
            player = self.world.getPlayer(msg.playerId)
            if player._state[msg.stateKey] == msg.value:
                if not msg.value:
                    return
                self.gameRequests.send(UpdatePlayerStateMsg(msg.playerId, False,
                        msg.stateKey))
            self.gameRequests.send(msg)
        except Abort:
            pass

    @handler(AimPlayerAtMsg, agentRequests)
    def reqAimPlayer(self, msg):
        thrust = min(1, max(0, msg.thrust))
        angle = (msg.angle + pi) % (2 * pi) - pi
        self.gameRequests.send(AimPlayerAtMsg(msg.playerId, angle, thrust))

    @handler(DeleteUpgradeMsg, agentRequests)
    def reqDelUpgrade(self, msg):
        try:
            player = self.world.getPlayer(msg.playerId)
            if (player.upgrade is not None and
                    player.upgrade.upgradeType != 'g'):
                self.gameRequests.send(msg)
        except Abort:
            pass

    @handler(RemovePlayerMsg, agentRequests)
    @handler(PlayerIsReadyMsg, agentRequests)
    def checkPlayerExists(self, msg):
        try:
            self.world.getPlayer(msg.playerId)
            self.gameRequests.send(msg)
        except Abort:
            pass

    @handler(ChatMsg, agentRequests)
    def chatSent(self, msg):
        try:
            player = self.world.getPlayer(msg.playerId)
            if msg.kind == 't' and not player.isFriendsWithTeam(
                    self.world.getTeam(msg.targetId)):
                # Cannot sent to opposing team.
                return
            if msg.kind == 'p':
                self.world.getPlayer(msg.targetId)  # Check player exists.
            self.gameRequests.send(msg)
        except Abort:
            pass

    @handler(SetPreferredTeamMsg, agentRequests)
    def reqPreferredTeam(self, msg):
        try:
            self.world.getPlayer(msg.playerId)
            teamName = msg.name.decode()[:MAX_TEAM_NAME_LENGTH]
            self.gameRequests.send(PreferredTeamSelectedMsg(msg.playerId,
                    self.world.isTournamentTeam(teamName), teamName.encode()))
        except Abort:
            pass

    @handler(SetPreferredSizeMsg, agentRequests)
    def reqPreferredSize(self, msg):
        try:
            self.world.getPlayer(msg.playerId)
            halfMapWidth = min(msg.halfMapWidth, MAX_HALF_WIDTH)
            mapHeight = min(msg.mapHeight, MAX_MAP_HEIGHT)
            self.gameRequests.send(SetPreferredSizeMsg(msg.playerId,
                    halfMapWidth, mapHeight))
        except Abort:
            pass

    @handler(SetPreferredDurationMsg, agentRequests)
    def reqPreferredDuration(self, msg):
        try:
            self.world.getPlayer(msg.playerId)
            duration = min(msg.duration, MAX_GAME_DURATION)
            self.gameRequests.send(SetPreferredDurationMsg(msg.playerId,
                    duration))
        except Abort:
            pass

    @handler(ChangeNicknameMsg, agentRequests)
    def reqChangeNickname(self, msg):
        if self.world.gameIsInProgress():
            return
        try:
            p = self.world.getPlayer(msg.playerId)
            nick = msg.nickname.decode()
            if not self.isValidNick(nick):
                return

            for player in self.world.players:
                if p != player and player.nick.lower() == nick.lower():
                    # Nick in use.
                    return

            if self.authTagManager is not None:
                if self.authTagManager.checkUsername(nick) and (p.user is None
                        or nick.lower() != p.user.username):
                    # Nick is someone else's username.
                    return

            self.gameRequests.send(msg)
            if p.user:
                p.user.setNick(nick)
        except Abort:
            pass

