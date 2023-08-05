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

from trosnoth.utils.netmsg import NetworkMessage
from trosnoth.utils.message import Message

class PlayerHasElephantMsg(NetworkMessage):
    idString = 'jken'
    fields = 'playerId'
    packspec = 'c'

####################
# Communication
####################

class ChatFromServerMsg(NetworkMessage):
    idString = 'ahoy'
    fields = 'text'
    packspec = '*'

class ChatMsg(NetworkMessage):
    '''
    kind may be 't' for team, 'p' for private, 'o' for open.
    '''
    idString = 'chat'
    fields = 'playerId', 'kind', 'targetId', 'text'
    packspec = 'ccc*'

class MarkZoneMsg(NetworkMessage):
    idString = 'Mrk1'
    fields = 'playerId', 'zoneId', 'value'
    packspec = 'cIb'

####################
# Gameplay
####################

class TaggingZoneMsg(NetworkMessage):
    idString = 'Tag!'
    fields = 'zoneId', 'playerId', 'teamId'
    packspec = 'Icc'

class CreateCollectableStarMsg(NetworkMessage):
    idString = 'StCr'
    fields = 'starId', 'teamId', 'xPos', 'yPos'
    packspec = 'ccff'

class RemoveCollectableStarMsg(NetworkMessage):
    idString = 'StCo'
    fields = 'starId', 'playerId'
    packspec = 'cc'

class StarReboundedMsg(NetworkMessage):
    idString = 'StRb'
    fields = 'starId', 'xpos', 'ypos', 'xvel', 'yvel'
    packspec = 'cffff'

class PlayerUpdateMsg(NetworkMessage):
    '''
    attached may be:
        'f' - falling
        'g' - on ground
        'l' - on wall to left of player
        'r' - on wall to right of player
    '''
    idString = 'PlUp'
    fields = ('playerId', 'xPos', 'yPos', 'yVel', 'angle', 'ghostThrust',
            'attached', 'keys')
    packspec = 'cfffffc*'

class RespawnMsg(NetworkMessage):
    idString = 'Resp'
    fields = 'playerId', 'zoneId'
    packspec = 'cI'

class RespawnRequestMsg(NetworkMessage):
    idString = 'Resp'
    fields = 'playerId', 'tag'
    packspec = 'cI'

class CannotRespawnMsg(NetworkMessage):
    '''
    reasonId may be:
        P: game hasn't started
        A: Already Alive
        T: Can't respawn yet
        E: In enemy zone
        F: Frozen Zone
    '''
    idString = 'NoRs'
    fields = 'playerId', 'reasonId', 'tag'
    packspec = 'ccI'

class PlayerKilledMsg(NetworkMessage):
    '''
    deathType may be:
        S: shot
        T: Turret, tagged
        G: Grenaded
        W: Shoxwave
        O: Off the map mercy killing
    '''
    idString = 'Dead'
    fields = 'targetId', 'killerId', 'shotId', 'stars', 'upgradeType', 'deathType'
    packspec = 'ccIfcc'

class PlayerHitMsg(NetworkMessage):
    '''
    When a health or shield point should be taken off.
    '''
    idString = 'ShAb'
    fields = 'targetId', 'shooterId', 'shotId'
    packspec = 'ccI'

class ShotAbsorbedMsg(NetworkMessage):
    '''
    When a the shot has hit its target, but does nothing.
    '''
    idString = 'PlHt'
    fields = 'targetId', 'shooterId', 'shotId'
    packspec = 'ccI'


####################
# Game
####################

class ChangeNicknameMsg(NetworkMessage):
    idString = 'Nick'
    fields = 'playerId', 'nickname'
    packspec = 'c*'

class PlayerIsReadyMsg(NetworkMessage):
    idString = 'Redy'
    fields = 'playerId', 'ready', 'tournament'
    packspec = 'c??'

class SetPreferredTeamMsg(NetworkMessage):
    idString = 'TmNm'
    fields = 'playerId', 'name'
    packspec = 'c*'

class PreferredTeamSelectedMsg(NetworkMessage):
    idString = 'TmNm'
    fields = 'playerId', 'tournament', 'name'
    packspec = 'c?*'

class SetPreferredSizeMsg(NetworkMessage):
    idString = 'Size'
    fields = 'playerId', 'halfMapWidth', 'mapHeight'
    packspec = 'cBB'

class SetPreferredDurationMsg(NetworkMessage):
    '''
    duration is in seconds.
    '''
    idString = 'Dr8n'
    fields = 'playerId', 'duration'
    packspec = 'cI'

class GameStartMsg(NetworkMessage):
    idString = 'Go!!'
    fields = 'timeLimit'
    packspec = 'd'

class GameOverMsg(NetworkMessage):
    idString = 'Stop'
    fields = 'teamId', 'timeOver'
    packspec = 'cB'

class ReturnToLobbyMsg(NetworkMessage):
    idString = 'Loby'
    fields = ()
    packspec = ''

class SetGameModeMsg(NetworkMessage):
    idString = 'Mode'
    fields = 'gameMode'
    packspec = '*'

class SetGameSpeedMsg(NetworkMessage):
    idString = 'Spee'
    fields = 'gameSpeed'
    packspec = 'f'

class SetTeamNameMsg(NetworkMessage):
    idString = 'Team'
    fields = 'teamId', 'name'
    packspec = 'c*'

class StartingSoonMsg(NetworkMessage):
    idString = 'Wait'
    fields = 'delay'
    packspec = 'd'

class ChangeTimeLimitMsg(NetworkMessage):
    idString = 'Time'
    fields = 'timeLimit'
    packspec = 'd'

class ChangePlayerLimitsMsg(NetworkMessage):
    idString = 'PlNo'
    fields = 'maxPerTeam', 'maxTotal'
    packspec = 'II'

####################
# Players
####################

class AddPlayerMsg(NetworkMessage):
    idString = 'NewP'
    fields = 'playerId', 'teamId', 'zoneId', 'dead', 'bot', 'nick'
    packspec = 'ccIbb*'

class SetPlayerTeamMsg(NetworkMessage):
    idString = 'PlTm'
    fields = 'playerId', 'teamId'
    packspec = 'cc'

class RemovePlayerMsg(NetworkMessage):
    idString = 'DelP'
    fields = 'playerId'
    packspec = 'c'

class JoinRequestMsg(NetworkMessage):
    idString = 'Join'
    fields = 'teamId', 'tag', 'authTag', 'bot', 'nick'
    packspec = 'cIQb*'
    authTag = 0
    localBotRequest = False     # Intentionally not sent over wire.

class JoinApproved(Message):
    '''
    Validator talking to id manager.
    '''
    fields = 'teamId', 'tag', 'zoneId', 'nick', 'username', 'bot'

class CannotJoinMsg(NetworkMessage):
    '''
    reasonId may be:
        F - game/team is full
        W - rejoining too soon
        A - not authorised
        N - nick in use
        B - bad nick
        U - user already in game
    '''
    idString = 'NotP'
    fields = 'reasonId', 'teamId', 'tag', 'waitTime'
    packspec = 'ccIf'
    waitTime = 0 # Default value.

class JoinSuccessfulMsg(NetworkMessage):
    '''
    Send back to the agent which requested to join if the join has succeeded.
    '''
    idString = 'OwnP'
    fields = 'playerId', 'tag', 'username'
    packspec = 'cI*'

class UpdatePlayerStateMsg(NetworkMessage):
    idString = 'Pres'
    fields = 'playerId', 'value', 'stateKey'
    packspec = 'cb*'

class AimPlayerAtMsg(NetworkMessage):
    idString = 'Aim@'
    fields = 'playerId', 'angle', 'thrust'
    packspec = 'cff'

####################
# Setup
####################

class InitClientMsg(NetworkMessage):
    idString = 'wlcm'
    fields = 'settings'
    packspec = '*'

class ConnectionLostMsg(Message):
    fields = ()

class WorldResetMsg(NetworkMessage):
    idString = 'rset'
    fields = ()
    packspec = ''

class QueryWorldParametersMsg(NetworkMessage):
    idString = 'What'
    fields = 'tag',
    packspec = 'I'

class SetWorldParametersMsg(NetworkMessage):
    idString = 'Set.'
    fields = 'tag', 'settings'
    packspec = 'I*'

class WorldParametersReceived(Message):
    fields = ()

class RequestMapBlockLayoutMsg(NetworkMessage):
    idString = 'RqMB'
    fields = 'tag', 'key'
    packspec = 'I*'

class MapBlockLayoutMsg(NetworkMessage):
    idString = 'MapB'
    fields = 'tag', 'data'
    packspec = 'I*'

class RequestPlayersMsg(NetworkMessage):
    idString = 'RqPl'
    fields = ()
    packspec = ''

class RequestZonesMsg(NetworkMessage):
    idString = 'RqZn'
    fields = ()
    packspec = ''

class RequestGameSpeedMsg(NetworkMessage):
    idString = 'RqGS'
    fields = ()
    packspec = ''

class RequestGameModeMsg(NetworkMessage):
    idString = 'RqGM'
    fields = ()
    packspec = ''

class ZoneStateMsg(NetworkMessage):
    '''
    marks is a string of team ids of teams who have marked this zone
    '''
    idString = 'ZnSt'
    fields = 'zoneId', 'teamId', 'dark', 'marks'
    packspec = 'Icb*'

####################
# Shot
####################

class ShootMsg(NetworkMessage):
    '''
    agent -> validator
    '''
    idString = 'shot'
    fields = 'playerId'
    packspec = 'c'

class FireShotMsg(NetworkMessage):
    '''
    validator -> id manager
    '''
    idString = 'shot'
    fields = 'playerId', 'angle', 'xpos', 'ypos', 'type'
    packspec = 'cfffc'

class ShotFiredMsg(NetworkMessage):
    '''
    id manager -> agents
    '''
    idString = 'SHOT'
    fields = 'playerId', 'shotId', 'angle', 'xpos', 'ypos', 'type'
    packspec = 'cIfffc'

class KillShotMsg(NetworkMessage):
    '''
    When the shot has hit a wall or run out of time.
    '''
    idString = 'KiSh'
    fields = 'shooterId', 'shotId'
    packspec = 'cI'

class FireShoxwaveMsg(NetworkMessage):
    '''
    id manager -> agents
    '''
    idString = 'Shox'
    fields = 'playerId', 'xpos', 'ypos'
    packspec = 'cff'

####################
# Upgrades
####################

class DeleteUpgradeMsg(NetworkMessage):
    '''
    deleteReason may be:
        'D' - player died
        'T' - upgrade an out of time
        'A' - abandoned
        'S' - shield that was shot
        'X' - removed by server
    '''
    idString = 'DUpg'
    fields = 'playerId', 'upgradeType', 'deleteReason'
    packspec = 'ccc'

class BuyUpgradeMsg(NetworkMessage):
    '''
    Signal from interface that a buy has been requested.

    Tag is an arbitrary integer which is returned in PlayerHasUpgradeMsg or
    PlayerStarsSpentMsg to indicate the request to which this response is being
    made.
    '''
    idString = 'GetU'
    fields = 'playerId', 'upgradeType', 'tag'
    packspec = 'ccI'

class PlayerHasUpgradeMsg(NetworkMessage):
    '''
    Signal from validator that the player now has the specified upgrade.
    Recipients of this message should not decrement player star counts except
    due to receipt of a PlayerStarsSpentMsg.

    reasonId may be:
        'B' - upgrade was bought by player
        'S' - upgrade was given by server
        'X' - reason unknown
    '''
    idString = 'GotU'
    fields = 'playerId', 'upgradeType', 'reasonId'
    packspec = 'ccc'

class PlayerStarsSpentMsg(NetworkMessage):
    idString = 'Spnt'
    fields = 'playerId', 'count'
    packspec = 'cI'

class CannotBuyUpgradeMsg(NetworkMessage):
    '''
    Tag is the value sent in BuyUpgradeMsg.
    reasonId may be:
        'N' - not enough stars
        'A' - already have upgrade
        'D' - player is dead
        'P' - game has not yet started
        'T' - there's already a turret in the zone
        'E' - too close to zone edge
        'O' - too close to orb
        'F' - not in a dark friendly zone
        'M' - your team has a minimap disruption in use
        'I' - invalid upgrade type
    '''
    idString = 'NotU'
    fields = 'playerId', 'reasonId', 'tag'
    packspec = 'ccI'

class GrenadeExplosionMsg(NetworkMessage):
    idString = 'BOOM'
    fields = 'xpos', 'ypos'
    packspec = 'ff'

class GrenadeReboundedMsg(NetworkMessage):
    idString = 'UhOh'
    fields = 'playerId', 'xpos', 'ypos', 'xvel', 'yvel'
    packspec = 'cffff'

class UpgradeChangedMsg(NetworkMessage):
    '''
    A message for the clients that informs them of a change in an upgrade stat.
    statType may be:
        'S' - star cost
        'T' - time limit
        'X' - explosion radius
    '''
    idString = 'UpCh'
    fields = 'upgradeType', 'statType', 'newValue'
    packspec = 'ccf'

############################
# Achievements
############################

class AchievementUnlockedMsg(NetworkMessage):
    idString = 'Achm'
    fields = 'playerId', 'achievementId'
    packspec = 'c*'
    
class AchievementProgressMsg(NetworkMessage):
    idString = 'AchP'
    fields = 'playerId', 'achievementId'
    packspec = 'c*'

############################
# Connection
############################

class RequestUDPStatusMsg(NetworkMessage):
    idString = 'rUDP'
    fields = ()
    packspec = ''

class NotifyUDPStatusMsg(NetworkMessage):
    idString = 'vUDP'
    fields = 'connected'
    packspec = 'b'

############################
# Message Collections
############################

tcpMessages = set([
    ChatFromServerMsg,
    ChatMsg,
    GameStartMsg,
    GameOverMsg,
    ReturnToLobbyMsg,
    SetGameModeMsg,
    SetTeamNameMsg,
    StartingSoonMsg,
    AddPlayerMsg,
    RemovePlayerMsg,
    JoinSuccessfulMsg,
    CannotJoinMsg,
    InitClientMsg,
    QueryWorldParametersMsg,
    SetWorldParametersMsg,
    RequestMapBlockLayoutMsg,
    MapBlockLayoutMsg,
    RequestPlayersMsg,
    AchievementUnlockedMsg,
    RequestZonesMsg,
    ZoneStateMsg,
    RequestUDPStatusMsg,
    NotifyUDPStatusMsg,
    PlayerHasUpgradeMsg,
    PlayerIsReadyMsg,
    SetPreferredTeamMsg,
    SetPreferredSizeMsg,
    SetPreferredDurationMsg,
    SetPlayerTeamMsg,
    CreateCollectableStarMsg,
    RemoveCollectableStarMsg,
    PlayerHasElephantMsg,
    ChangeNicknameMsg,
    ChangeTimeLimitMsg,
    UpgradeChangedMsg
])
