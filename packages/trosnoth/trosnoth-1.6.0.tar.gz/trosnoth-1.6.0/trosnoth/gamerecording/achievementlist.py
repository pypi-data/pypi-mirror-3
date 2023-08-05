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

from collections import defaultdict
import string
import logging

from trosnoth.model.universe import Abort
from trosnoth.model.upgrades import allUpgrades
from trosnoth.model.zone import ZoneState
from trosnoth.messages import (AchievementUnlockedMsg, TaggingZoneMsg,
        PlayerKilledMsg, PlayerHasUpgradeMsg, ShotFiredMsg, DeleteUpgradeMsg,
        ChatMsg, ShotAbsorbedMsg, RespawnMsg, RemovePlayerMsg, GameOverMsg,
        AchievementProgressMsg)
from trosnoth.utils.event import Event

log = logging.getLogger('achievementlist')

###########
# Helpers #
###########

def checkPlayerId(fn):
    def newFn(self, msg):
        if msg.playerId == self.player.id:
            return fn(self, msg)
    newFn.__name__ = fn.__name__
    return newFn

############################
# Achievement base classes #
############################

class Achievement(object):

    keepProgress = False
    afterGame = False

    oncePerGame = False
    oncePerTeamPerGame = False

    def rejoined(self, player):
        pass

    def processMessage(self, msg):
        msgType = type(msg).__name__
        methodname = 'got%s' % (msgType,)
        if hasattr(self, methodname):
            proc = getattr(self, methodname)
            proc(msg)

    def _sendUnlocked(self, player):
        self.outPlug.send(AchievementUnlockedMsg(player.id,
                self.idstring.encode()))
        log.debug(self.achievementString(player))

    def achievementString(self, player):
        if self.name == "":
            return 'Achievement unlocked by %s! - %s' % (player.nick,
                                                         self.idstring)
        else:
            return 'Achievement unlocked by %s! - %s' % (player.nick,
                                                         self.name)

    def __str__(self):
        return '%s' % self.idstring

    def __repr__(self):
        return '%s' % self.idstring

    @classmethod
    def describe(cls):
        '''
        Used when saving achievement meta-information to file. Should be
        overwritten by higher level classes.
        '''
        information = {'name': cls.name,
                       'description': cls.description,
                       'type': 'boolean'}
        return {cls.idstring: information}

class PlayerAchievement(Achievement):
    perPlayer = True
    def __init__(self, player, world, outPlug):
        super(PlayerAchievement, self).__init__()
        self.player = player
        self.world = world
        self.outPlug = outPlug

    def rejoined(self, player):
        self.player = player


class PlayerlessAchievement(Achievement):
    perPlayer = False

    def achievementUnlocked(self, playerList):
        if not self.unlocked:
            self.unlocked = True
            for player in playerList:
                self._sendUnlocked(player)

    def listeningForMessages(self):
        return not self.unlocked

class OncePerGame(PlayerlessAchievement):
    oncePerGame = True

    def __init__(self, world, outPlug):
        super(OncePerGame, self).__init__()
        self.world = world
        self.outPlug = outPlug
        self.unlocked = False

class OncePerTeamPerGame(PlayerlessAchievement):
    oncePerTeamPerGame = True

    def __init__(self, world, team, outPlug):
        super(OncePerTeamPerGame, self).__init__()
        self.world = world
        self.outPlug = outPlug
        self.team = team
        self.unlocked = False

class OncePerPlayerPerGame(PlayerAchievement):
    def __init__(self, player, world, outPlug):
        super(OncePerPlayerPerGame, self).__init__(player, world, outPlug)
        self.unlocked = False

    def achievementUnlocked(self):
        if not self.unlocked:
            self.unlocked = True
            self._sendUnlocked(self.player)

    def listeningForMessages(self):
        return not self.unlocked

class NoLimit(PlayerAchievement):
    def __init__(self, player, world, outPlug):
        super(NoLimit, self).__init__(player, world, outPlug)
        self.unlocked = False

    def achievementUnlocked(self):
        self.unlocked = True
        self._sendUnlocked(self.player)

    def listeningForMessages(self):
        return True

class OnceEverPerPlayer(PlayerAchievement):
    '''
    self.unlocked is "unlocked this time".
    self.previouslyUnlocked is "unlocked previously".
    '''
    keepProgress = True
    def __init__(self, player, world, outPlug):
        super(OnceEverPerPlayer, self).__init__(player, world, outPlug)
        self.unlocked = False
        self.previouslyUnlocked = False
        if self.player is not None and not self.player.bot:
            self.readExistingData()

    def readExistingData(self):
        user = self.player.user
        if user is None:
            self.previouslyUnlocked = False
            self.progress = 0
        else:
            userAchievements = user.achievements.get(self.idstring, {})
            self.previouslyUnlocked = userAchievements.get('unlocked', False)
            self.progress = userAchievements.get('progress', 0)

    def achievementUnlocked(self):
        if not self.unlocked and not self.previouslyUnlocked:
            self.unlocked = True
            self._sendUnlocked(self.player)

    def listeningForMessages(self):
        return not self.unlocked and not self.previouslyUnlocked

    def getJsonString(self):
        return {
            'unlocked' : self.unlocked or self.previouslyUnlocked,
            'progress' : self.progress,
        }


###################
# Streak subclass #
###################

class IncrementingAchievement(Achievement):
    requiredQuantity = -1
    def __init__(self, player, world, outPlug):
        self.progress = 0
        super(IncrementingAchievement, self).__init__(player, world, outPlug)

    def increment(self, amount=1):
        self.progress = min(self.requiredQuantity, self.progress + amount)

        if self.progress == self.requiredQuantity:
            self.achievementUnlocked()

    def reset(self):
        self.progress = 0

    def __str__(self):
        return "%s: %d/%d" % (self.idstring, self.progress,
                self.requiredQuantity)

    @classmethod
    def describe(self):
        information = {'name': self.name,
                       'description': self.description,
                       'type': 'incremental',
                       'requirements': self.requiredQuantity,
                       'keepProgress': self.keepProgress}
        return {self.idstring: information}

class Streak(IncrementingAchievement):
    '''
    Base class for streak achivements. Subclasses must define:
     * streakTarget - the number to aim for
     * incrementTrigger - a Trigger class on which increments occur
     * resetTrigger (optional) - a Trigger class on which resets occur
    '''
    resetTrigger = None

    def __init__(self, player, world, outPlug):
        self.progress = 0
        super(Streak, self).__init__(player, world, outPlug)
        self.incrementTrigger = self.incrementTrigger(player, world)
        self.incrementTrigger.onTrigger.addListener(self.increment)
        if self.resetTrigger is not None:
            self.resetTrigger = self.resetTrigger(player, world)
            self.resetTrigger.onTrigger.addListener(self.reset)
        self.requiredQuantity = self.streakTarget

    def processMessage(self, msg):
        msgClass = msg.__class__
        if msgClass in self.incrementTrigger.messages:
            self.incrementTrigger.processMessage(msg)
        if (self.resetTrigger is not None and msgClass in
                self.resetTrigger.messages):
            self.resetTrigger.processMessage(msg)

    def rejoined(self, player):
        super(Streak, self).rejoined(player)
        if self.resetTrigger is not None:
            self.resetTrigger.rejoined(player)
        self.incrementTrigger.rejoined(player)

class Trigger(object):
    def __init__(self, player, world):
        self.player = player
        self.world = world
        self.onTrigger = Event()

    def processMessage(self, msg):
        msgType = type(msg).__name__
        methodname = 'got%s' % (msgType,)
        proc = getattr(self, methodname)
        proc(msg)

    def rejoined(self, player):
        self.player = player

class ZoneTagTrigger(Trigger):
    messages = (TaggingZoneMsg,)

    @checkPlayerId
    def gotTaggingZoneMsg(self, msg):
        self.onTrigger.execute()

class TagAssistTrigger(Trigger):
    messages = (TaggingZoneMsg,)

    def processMessage(self, msg):
        if (self.player.team and msg.teamId == self.player.team.id):
            if msg.playerId == self.player.id:
                return
            zone = self.world.getZone(msg.zoneId)
            if self.player in zone.players:
                self.onTrigger.execute()

class PlayerDeathTrigger(Trigger):
    messages = (PlayerKilledMsg,)

    def processMessage(self, msg):
        if msg.targetId == self.player.id:
            self.onTrigger.execute()

class PlayerKillTrigger(Trigger):
    messages = (PlayerKilledMsg,)

    def gotPlayerKilledMsg(self, msg):
        if msg.killerId == self.player.id:
            self.onTrigger.execute()

class UseUpgradeTrigger(Trigger):
    messages = (PlayerHasUpgradeMsg,)

    @checkPlayerId
    def processMessage(self, msg):
        self.onTrigger.execute()

class FireShotTrigger(Trigger):
    messages = (ShotFiredMsg,)

    @checkPlayerId
    def processMessage(self, msg):
        self.onTrigger.execute()

class EarnStarTrigger(PlayerKillTrigger, ZoneTagTrigger):
    messages = (PlayerKilledMsg, TaggingZoneMsg)

class WinTrigger(Trigger):
    messages = (GameOverMsg,)

    def gotGameOverMsg(self, msg):
        if (msg.teamId == '\x00' or self.world.getTeam(msg.teamId) !=
                self.player.team):
            return

        playerCount = 0

        for player in self.world.players:
            if not player.bot:
                playerCount += 1

        if playerCount >= 6:
            self.onTrigger.execute()

##########################
# Achievement subclasses #
##########################

class ListeningAchievement(Achievement):
    messages = (AchievementProgressMsg,)

    @checkPlayerId
    def gotAchievementProgressMsg(self, msg):
        if msg.achievementId == self.idstring:
            self.achievementUnlocked()

class KilledSomeoneAchievement(Achievement):
    messages = (PlayerKilledMsg,)

    def gotPlayerKilledMsg(self, msg):
        if msg.killerId == self.player.id:
            self.killedSomeone(msg)

    def killedSomeone(self, msg):
        pass # To be implemented in subclasses

class ChecklistAchievement(Achievement):
    requiredItems = set()
    def __init__(self, player, world, outPlug):
        self.progress = set()
        super(ChecklistAchievement, self).__init__(player, world, outPlug)

    def addItem(self, item):
        self.progress.add(item)

        if self.requiredItems == self.progress:
            self.achievementUnlocked()

    def __str__(self):
        return "%s: %d/%d items" % (self.idstring, len(self.progress),
                len(self.requiredItems))

    @classmethod
    def describe(self):
        information = {'name': self.name,
                       'description': self.description,
                       'type': 'checklist',
                       'requirements': list(self.requiredItems),
                       'keepProgress': self.keepProgress}
        return {self.idstring: information}

class PersistedChecklistAchievement(ChecklistAchievement, OnceEverPerPlayer):
    def readExistingData(self):
        user = self.player.user
        if user is None:
            self.previouslyUnlocked = False
            self.progress = set()
        else:
            userAchievements = user.achievements.get(self.idstring, {})
            self.previouslyUnlocked = userAchievements.get('unlocked', False)
            self.progress = set(userAchievements.get('progress', []))

    def getJsonString(self):
        return {
            'unlocked' : self.unlocked or self.previouslyUnlocked,
            # JSON doesn't support sets:
            'progress' : list(self.progress),
        }

class TimedAchievement(Achievement):
    requiredValue = -1
    timeWindow = -1

    def __init__(self, player, world, outPlug):
        super(TimedAchievement, self).__init__(player, world, outPlug)
        self.rollingList = []

    def addToList(self):
        now = self.world.getElapsedTime()
        self.rollingList.append(now)

        while (len(self.rollingList) > 0 and (now - self.rollingList[0]) >
                self.timeWindow):
            del self.rollingList[0]

        if len(self.rollingList) >= self.requiredValue:
            self.achievementUnlocked()
            self.rollingList = []


class QuickKillAchievement(TimedAchievement, KilledSomeoneAchievement):
    deathTypes = ''

    def killedSomeone(self, msg):
        if msg.deathType in self.deathTypes:
            self.addToList()

##################################
# Collection of all achievements #
##################################

class AchievementSet(object):
    def __init__(self, template=None):
        self.all = []
        self.byId = {}
        self.oncePerGame = []
        self.oncePerTeamPerGame = []
        self.perPlayer = []
        if template:
            for achievement in template.all:
                self.register(achievement)

    def getAchievementDetails(self, idstring):
        achievement = self.byId[idstring]
        if achievement.name == "":
            return idstring, achievement.description
        else:
            return achievement.name, achievement.description

    def register(self, achievement):
        if achievement.idstring in self.byId:
            raise KeyError('achievement with id %r already registered' % (
                    achievement.idstring,))

        self.all.append(achievement)
        self.byId[achievement.idstring] = achievement

        if achievement.oncePerGame:
            self.oncePerGame.append(achievement)
        elif achievement.oncePerTeamPerGame:
            self.oncePerTeamPerGame.append(achievement)
        else:
            assert achievement.perPlayer
            self.perPlayer.append(achievement)
        return achievement

availableAchievements = AchievementSet()

#########################
# Concrete Achievements #
#########################

@availableAchievements.register
class MultiTagSmall(Streak, OncePerPlayerPerGame):
    idstring = 'multiTagSmall'
    name = 'I Ain\'t Even Winded'
    description = 'Capture three zones in a single life'

    incrementTrigger = ZoneTagTrigger
    resetTrigger = PlayerDeathTrigger
    streakTarget = 3
    messages = incrementTrigger.messages + resetTrigger.messages

@availableAchievements.register
class MultiTagMedium(Streak, OncePerPlayerPerGame):
    idstring = 'multiTagMedium'
    name = 'The Long Way Home'
    description = 'Capture five zones in a single life'

    incrementTrigger = ZoneTagTrigger
    resetTrigger = PlayerDeathTrigger
    streakTarget = 5
    messages = incrementTrigger.messages + resetTrigger.messages

@availableAchievements.register
class MultiTagLarge(Streak, OncePerPlayerPerGame):
    idstring = 'multiTagLarge'
    name = 'Cross-Country Marathon'
    description = 'Capture eight zones in a single life'

    incrementTrigger = ZoneTagTrigger
    resetTrigger = PlayerDeathTrigger
    streakTarget = 8
    messages = incrementTrigger.messages + resetTrigger.messages

@availableAchievements.register
class TotalTagsSmall(Streak, OnceEverPerPlayer):
    idstring = 'totalTagsSmall'
    name = 'Cultural Assimilation'
    description = 'Capture 20 zones'

    incrementTrigger = ZoneTagTrigger
    streakTarget = 20
    messages = incrementTrigger.messages

@availableAchievements.register
class TotalTagsMedium(Streak, OnceEverPerPlayer):
    idstring = 'totalTagsMedium'
    name = 'Globalization'
    description = 'Capture 50 zones'

    incrementTrigger = ZoneTagTrigger
    streakTarget = 50
    messages = incrementTrigger.messages

@availableAchievements.register
class MultiKillSmall(Streak, OncePerPlayerPerGame):
    idstring = 'multikillSmall'
    name = 'Triple Threat'
    description = 'Kill three enemies in a single life'

    incrementTrigger = PlayerKillTrigger
    resetTrigger = PlayerDeathTrigger
    streakTarget = 3
    messages = list(set(incrementTrigger.messages + resetTrigger.messages))

@availableAchievements.register
class MultiKillMedium(Streak, OncePerPlayerPerGame):
    idstring = 'multikillMedium'
    name = 'High Five'
    description = 'Kill five enemies in a single life'

    incrementTrigger = PlayerKillTrigger
    resetTrigger = PlayerDeathTrigger
    streakTarget = 5
    messages = list(set(incrementTrigger.messages + resetTrigger.messages))

@availableAchievements.register
class MultiKillLarge(Streak, OncePerPlayerPerGame):
    idstring = 'multikillLarge'
    name = "That's the Badger"
    description = 'Kill nine enemies in a single life'

    incrementTrigger = PlayerKillTrigger
    resetTrigger = PlayerDeathTrigger
    streakTarget = 9
    messages = list(set(incrementTrigger.messages + resetTrigger.messages))

@availableAchievements.register
class TotalKillsSmall(Streak, OnceEverPerPlayer):
    idstring = 'totalKillsSmall'
    name = 'Family Friendly Fun'
    description = 'Kill 50 enemies'

    incrementTrigger = PlayerKillTrigger
    streakTarget = 50
    messages = incrementTrigger.messages

@availableAchievements.register
class TotalKillsMedium(Streak, OnceEverPerPlayer):
    idstring = 'totalKillsMedium'
    name = 'We All Fall Down'
    description = 'Kill 100 enemies'

    incrementTrigger = PlayerKillTrigger
    streakTarget = 100
    messages = incrementTrigger.messages

@availableAchievements.register
class ShoppingSpree(Streak, OncePerPlayerPerGame):
    idstring = 'multiUpgradesSmall'
    name =  'Shopping Spree'
    description = 'Buy two upgrades in a single life'

    incrementTrigger = UseUpgradeTrigger
    resetTrigger = PlayerDeathTrigger
    streakTarget = 2
    messages = incrementTrigger.messages + resetTrigger.messages

@availableAchievements.register
class SmartShopper(Streak, OncePerPlayerPerGame):
    idstring = 'multiUpgradesMedium'
    name = 'Smart Shopper'
    description = 'Buy five upgrades in a single game'

    incrementTrigger = UseUpgradeTrigger
    streakTarget = 5
    messages = incrementTrigger.messages

@availableAchievements.register
class BulletsSmall(Streak, OncePerPlayerPerGame):
    idstring = 'bulletsSmall'
    name = 'Machine Gunner'
    description = 'Shoot 100 bullets in a single life'

    incrementTrigger = FireShotTrigger
    resetTrigger = PlayerDeathTrigger
    streakTarget = 100
    messages = incrementTrigger.messages + resetTrigger.messages

@availableAchievements.register
class BulletsMedium(Streak, OncePerPlayerPerGame):
    idstring = 'bulletsMedium'
    name = 'Ammunition Overdrive'
    description = 'Shoot 500 bullets in a single game'

    incrementTrigger = FireShotTrigger
    streakTarget = 500
    messages = incrementTrigger.messages

@availableAchievements.register
class WinnerTiny(Streak, OnceEverPerPlayer):
    idstring = 'winnerTiny'
    name = 'Trosnoth Newbie'
    description = 'Win your first game of Trosnoth (minimum 6 players)'
    afterGame = True

    incrementTrigger = WinTrigger
    streakTarget = 1
    messages = incrementTrigger.messages

@availableAchievements.register
class WinnerSmall(Streak, OnceEverPerPlayer):
    idstring = 'winnerSmall'
    name = 'Trosnoth Amateur'
    description = 'Win 5 games of Trosnoth (minimum 6 players)'
    afterGame = True

    incrementTrigger = WinTrigger
    streakTarget = 5
    messages = incrementTrigger.messages

@availableAchievements.register
class WinnerMedium(Streak, OnceEverPerPlayer):
    idstring = 'winnerMedium'
    name = 'Trosnoth Consultant'
    description = 'Win 10 games of Trosnoth (minimum 6 players)'
    afterGame = True

    incrementTrigger = WinTrigger
    streakTarget = 10
    messages = incrementTrigger.messages

@availableAchievements.register
class WinnerLarge(Streak, OnceEverPerPlayer):
    idstring = 'winnerLarge'
    name = 'Trosnoth Professional'
    description = 'Win 20 games of Trosnoth (minimum 6 players)'
    afterGame = True

    incrementTrigger = WinTrigger
    streakTarget = 20
    messages = incrementTrigger.messages

@availableAchievements.register
class WinnerHuge(Streak, OnceEverPerPlayer):
    idstring = 'winnerHuge'
    name = 'Trosnoth Expert'
    description = 'Win 50 games of Trosnoth (minimum 6 players)'

    incrementTrigger = WinTrigger
    streakTarget = 50
    messages = incrementTrigger.messages

@availableAchievements.register
class AssistTags(Streak, OncePerPlayerPerGame):
    idstring = 'assistTags'
    name = 'Credit to Team'
    description = 'Assist in the tagging of five zones in a single game'

    incrementTrigger = TagAssistTrigger
    streakTarget = 5
    messages = incrementTrigger.messages

@availableAchievements.register
class QuickKillSmall(QuickKillAchievement, NoLimit):
    requiredValue = 2
    timeWindow = 5
    deathTypes = 'ST'
    idstring = 'quickKillSmall'
    name = 'Double Kill'
    description = 'Kill two enemies within five seconds (no grenades)'

@availableAchievements.register
class QuickKillMedium(QuickKillAchievement, NoLimit):
    requiredValue = 3
    timeWindow = 5
    deathTypes = 'ST'
    idstring = 'quickKillMedium'
    name = 'Triple Kill'
    description = 'Kill three enemies within five seconds (no grenades)'

@availableAchievements.register
class GrenadeMultiKill(QuickKillAchievement, NoLimit):
    requiredValue = 3
    # Processing of achievements should happen within 0.25 secs
    timeWindow = 0.25
    deathTypes = 'G'
    idstring = 'grenadeMultikill'
    name = "It's Super Effective!"
    description = 'Kill three enemies with a single grenade'

@availableAchievements.register
class RicochetAchievement(ListeningAchievement, OncePerPlayerPerGame):
    name = 'Bouncy Flag'
    description = ('Kill an enemy with a bullet that has ricocheted at least '
            'once')
    idstring = 'ricochetKill'

@availableAchievements.register
class AccuracySmall(ListeningAchievement, OncePerPlayerPerGame):
    name = 'Boom, Headshot'
    description = 'Have an accuracy of 10% or higher during a game'
    idstring = 'accuracySmall'

@availableAchievements.register
class AccuracyMedium(ListeningAchievement, OncePerPlayerPerGame):
    name = "Sniping's a Good Job, Mate"
    description = 'Have an accuracy of 15% or higher during a game'
    idstring = 'accuracyMedium'

@availableAchievements.register
class AccuracyLarge(ListeningAchievement, OncePerPlayerPerGame):
    name = 'Professionals Have Standards'
    description = 'Have an accuracy of 20% or higher during a game'
    idstring = 'accuracyLarge'

@availableAchievements.register
class StatScore(ListeningAchievement, OncePerPlayerPerGame):
    name = 'Master of the Internet'
    description = 'Reach a stats score of 1337 or higher during a game'
    idstring = 'statScore'

@availableAchievements.register
class TotalAliveTime(ListeningAchievement, OnceEverPerPlayer):
    name = 'Long Live the King'
    description = 'Rack up a total of 1000 seconds of alive time'
    idstring = 'totalAliveTime'

@availableAchievements.register
class StayingAlive(ListeningAchievement, OncePerPlayerPerGame):
    name = 'Never Asleep on the Job'
    description = 'Be alive at least 75% of the time'
    idstring = 'stayingAlive'

@availableAchievements.register
class AliveStreak(ListeningAchievement, OncePerPlayerPerGame):
    name = 'Still Alive'
    description = 'Stay alive for at least 180 seconds in a single life'
    idstring = 'aliveStreak'

@availableAchievements.register
class UseStarsEfficiently(ListeningAchievement, OncePerPlayerPerGame):
    name = 'Waste Not, Want Not'
    description = ('Use or contribute at least 50% of the stars you earn '
            'during a game')
    idstring = 'useStarsEfficiently'

@availableAchievements.register
class LongRangeKill(ListeningAchievement, OncePerPlayerPerGame):
    name = 'Long-Range Ballistics'
    description = 'Kill an enemy at the maximum range of your gun'
    idstring = 'longRangeKill'

# More complicated ones:
@availableAchievements.register
class TagsAndKills(OncePerPlayerPerGame):
    name = 'All-Rounder'
    description = 'Kill 10 people and tag 5 zones in a single life'
    idstring = 'tagsAndKills'

    status = [0, 0]
    requiredQuantity = [10, 5]
    messages = (TaggingZoneMsg, PlayerKilledMsg)

    @checkPlayerId
    def gotTaggingZoneMsg(self, msg):
        self.status[1] = min(self.status[1] + 1, self.requiredQuantity[1])
##        print "Status: %s" % repr(self.status)
        if self.status == self.requiredQuantity:
            self.achievementUnlocked()

    def gotPlayerKilledMsg(self, msg):
        if msg.targetId == self.player.id:
            self.status = [0, 0]
        elif msg.killerId == self.player.id:
            self.status[0] = min(self.status[0] + 1, self.requiredQuantity[0])
##            print "Status: %s" % repr(self.status)
            if self.status == self.requiredQuantity:
                self.achievementUnlocked()

@availableAchievements.register
class DestroyStars(KilledSomeoneAchievement, IncrementingAchievement,
        OnceEverPerPlayer):
    idstring = 'destroyStars'
    name = 'The Recession we Had to Have'
    description = 'Destroy 100 stars by killing the players carrying them'
    requiredQuantity = 100

    def killedSomeone(self, msg):
        self.increment(msg.stars)

@availableAchievements.register
class EarnStars(IncrementingAchievement, OnceEverPerPlayer):
    idstring = 'earnStars'
    name = 'Stimulus Package'
    description = 'Earn 100 stars'

    incrementTrigger = EarnStarTrigger
    requiredQuantity = 100
    messages = incrementTrigger.messages

@availableAchievements.register
class BuyEveryUpgrade(PersistedChecklistAchievement):
    idstring = 'buyEveryUpgrade'
    name = 'Technology Whiz'
    description = 'Use every upgrade at least once'
    requiredItems = set(u.upgradeType for u in allUpgrades)
    messages = (PlayerHasUpgradeMsg,)

    @checkPlayerId
    def gotPlayerHasUpgradeMsg(self, msg):
        if msg.reasonId == 'B':
            self.addItem(msg.upgradeType)

@availableAchievements.register
class UseMinimapDisruption(OncePerPlayerPerGame):
    idstring = 'minimapDisruption'
    name = 'The Rader Appears to be... Jammed!'
    description = 'Use a minimap disruption'
    messages = (PlayerHasUpgradeMsg,)

    @checkPlayerId
    def gotPlayerHasUpgradeMsg(self, msg):
        if msg.upgradeType == 'm' and msg.reasonId == 'B':
            self.achievementUnlocked()

#disabled @availableAchievements.register
class AbandonEarly(OncePerPlayerPerGame):
    idstring = 'abandonEarly'
    name = 'Reduce, Reuse, Recycle'
    description = 'Abandon a turret or phase shift before it runs out'
    messages = (DeleteUpgradeMsg,)

    @checkPlayerId
    def gotDeleteUpgradeMsg(self, msg):
        '''
        Don't award if it was within 3 seconds of running out anyway.
        '''
        if (msg.deleteReason == 'A' and msg.upgradeType in 'th' and
                self.player.upgradeGauge >= 3):
            self.achievementUnlocked()

@availableAchievements.register
class GoodManners(OncePerPlayerPerGame):
    idstring = 'goodManners'
    name = 'Good Manners'
    description = 'Say "gg" after the game finishes'
    afterGame = True
    messages = (ChatMsg,)

    @checkPlayerId
    def gotChatMsg(self, msg):
        if msg.kind == 'o' and msg.text.decode().lower().strip() == 'gg':
            self.achievementUnlocked()

@availableAchievements.register
class DarkZoneKills(IncrementingAchievement, KilledSomeoneAchievement,
        OncePerPlayerPerGame):
    idstring = 'darkZoneKills'
    name = 'Behind Enemy Lines'
    description = "Kill five enemies when you're in a dark zone of their colour"
    requiredQuantity = 5

    def killedSomeone(self, msg):
        if self.player.team is None:
            return
        if (self.player.isEnemyTeam(self.player.currentZone.zoneOwner)
                and not self.player.ghost):
            self.increment()

@availableAchievements.register
class NinjaKill(KilledSomeoneAchievement, OncePerPlayerPerGame):
    idstring = 'ninjaKill'
    name = "Ninjas Can't Catch You if You're on Fire"
    description = 'Kill an invisible ninja'

    def killedSomeone(self, msg):
        if msg.upgradeType == 'n':
            self.achievementUnlocked()

@availableAchievements.register
class AntiDisruption(KilledSomeoneAchievement, OncePerPlayerPerGame):
    idstring = 'antiDisruption'
    name = "Back Online"
    description = 'Kill an enemy who is using a Minimap Disruption'

    def killedSomeone(self, msg):
        if msg.upgradeType == 'm':
            self.achievementUnlocked()

@availableAchievements.register
class ChokepointSpam(IncrementingAchievement, KilledSomeoneAchievement,
        OncePerPlayerPerGame):

    idstring = 'chokepointSpam'
    name = "Chokepoint Checkmate"
    description = 'Kill three players without moving or dying (no upgrades)'
    requiredQuantity = 3

    x = y = 0

    messages = (PlayerKilledMsg, ShotFiredMsg)

    # Strictly speaking, the player is still able to move or die, but if they
    # don't shoot from exactly the same spot it won't count anyway.

    @checkPlayerId
    def gotShotFiredMsg(self, msg):
        if msg.xpos != self.x or msg.ypos != self.y:
            self.reset()

        self.x = msg.xpos
        self.y = msg.ypos

    def killedSomeone(self, msg):
        if self.player.upgrade is None:
            self.increment()


#disabled @availableAchievements.register
class PhaseShiftAbsorb(IncrementingAchievement, OncePerPlayerPerGame):
    idstring = 'phaseShiftAbsorb'
    name = "Can't Touch This"
    description = 'Get hit by 30 bullets in a single phase shift'
    requiredQuantity = 30
    messages = (ShotAbsorbedMsg, DeleteUpgradeMsg)

    def gotShotAbsorbedMsg(self, msg):
        if (msg.targetId == self.player.id and self.player.upgrade is not None
                and self.player.upgrade.upgradeType == 'h'):
            self.increment()

    @checkPlayerId
    def gotDeleteUpgradeMsg(self, msg):
        if msg.upgradeType == 'h':
            self.reset()

@availableAchievements.register
class KillEnemyWithStars(KilledSomeoneAchievement, OncePerPlayerPerGame):
    name = 'Stop Right There, Criminal Scum'
    description = 'Kill an enemy holding five stars or more'
    idstring = 'killEnemyWithStars'

    def killedSomeone(self, msg):
        if msg.stars >= 5:
            self.achievementUnlocked()

@availableAchievements.register
class KillAsRabbit(KilledSomeoneAchievement, OncePerPlayerPerGame):
    name = 'Never Surrender'
    description = 'Kill an enemy after losing a game'
    idstring = 'killAsRabbit'
    afterGame = True

    def killedSomeone(self, msg):
        if (self.player.team is not None and
                self.player.isEnemyTeam(self.world.getWinningTeam())):
            self.achievementUnlocked()

@availableAchievements.register
class RabbitKill(KilledSomeoneAchievement, OncePerPlayerPerGame):
    name = 'Icing on the Cake'
    description = 'Kill an enemy after winning a game'
    idstring = 'killRabbit'
    afterGame = True

    def killedSomeone(self, msg):
        if (self.world.getWinningTeam() == self.player.team and
                self.player.isEnemyTeam(self.world.getPlayer(msg.targetId
                ).team)):
            self.achievementUnlocked()

#disabled @availableAchievements.register
class TurretKill(KilledSomeoneAchievement, OncePerPlayerPerGame):
    name = 'Sentry Mode Activated'
    description = 'Kill an enemy as a turret'
    idstring = 'turretKill'

    def killedSomeone(self, msg):
        if (self.player.upgrade is not None and self.player.upgrade.upgradeType
                == 't'):
            self.achievementUnlocked()

@availableAchievements.register
class FirstKill(OncePerGame):
    name = 'First Blood'
    description = 'Make the first kill of the game'
    idstring = 'firstKill'
    messages = (PlayerKilledMsg,)

    def gotPlayerKilledMsg(self, msg):
        if not self.unlocked:
            try:
                killer = self.world.getPlayer(msg.killerId)
            except Abort:
                return
            else:
                players = set([killer])
                self.achievementUnlocked(players)

@availableAchievements.register
class FirstTag(OncePerGame):
    name = 'Game On'
    description = 'Tag or assist in the tagging of the first zone in a game'
    idstring = 'firstTag'
    messages = (TaggingZoneMsg,)

    def gotTaggingZoneMsg(self, msg):
        if not self.unlocked:
            zone = self.world.getZone(msg.zoneId)
            team = self.world.getTeam(msg.teamId)
            helpers = set([])
            for player in zone.players:
                if player.team == team:
                    helpers.add(player)
            self.achievementUnlocked(helpers)

@availableAchievements.register
class FirstRespawn(OncePerGame):
    name = 'Finger on the Trigger'
    description = 'Be the first person to respawn (minimum 6 players)'
    idstring = 'firstRespawn'
    messages = (RespawnMsg,)

    def gotRespawnMsg(self, msg):
        if not self.unlocked:
            if len(self.world.players) < 6:
                self.achievementUnlocked([])
            else:
                player = self.world.getPlayer(msg.playerId)
                self.achievementUnlocked([player])

@availableAchievements.register
class LastTag(OncePerGame):
    name = 'And the Dirt is Gone'
    description = 'Tag or assist in the tagging of the final zone'
    idstring = 'finalTag'
    messages = (TaggingZoneMsg,)

    def gotTaggingZoneMsg(self, msg):
        team = self.world.getTeam(msg.teamId)

        if team and team.opposingTeam.numOrbsOwned == 0:
            zone = self.world.getZone(msg.zoneId)
            winners = set([])
            for player in zone.players:
                if player.team == team:
                    winners.add(player)
            self.achievementUnlocked(winners)

@availableAchievements.register
class Domination(KilledSomeoneAchievement, OncePerPlayerPerGame):
    name = 'Domination'
    description = 'Kill the same enemy five times in a single game'
    idstring = 'domination'
    requiredQuantity = 5

    def __init__(self, player, world, outPlug):
        super(Domination, self).__init__(player, world, outPlug)
        self.playerKills = defaultdict(int)

    def killedSomeone(self, msg):
        nick = self.world.getPlayer(msg.targetId).identifyingName
        self.playerKills[nick] += 1
        if self.playerKills[nick] == self.requiredQuantity:
            self.achievementUnlocked()

@availableAchievements.register
class MinimapDisruptionTag(OncePerPlayerPerGame):
    name = 'Under the Radar'
    description = 'Tag a zone while the enemy\'s minimap is disrupted'
    idstring = 'disruptionTag'
    messages = (TaggingZoneMsg,)

    @checkPlayerId
    def gotTaggingZoneMsg(self, msg):
        for player in self.world.players:
            if (player.team == self.player.team and player.upgrade is not None
                    and player.upgrade.upgradeType == 'm'):
                self.achievementUnlocked()
                break

@availableAchievements.register
class MutualKill(NoLimit):
    name = 'Eye for an Eye'
    description = 'Kill an enemy at the same time he kills you'
    idstring = 'mutualKill'
    messages = (PlayerKilledMsg, RespawnMsg, RemovePlayerMsg)

    def __init__(self, player, world, outPlug):
        super(MutualKill, self).__init__(player, world, outPlug)
        # Keep a record of the people we kill. If they kill us while they're
        # dead, achievement unlocked.  Similarly, keep a record of who killed
        # us. If we kill them while we're dead, achievement unlocked.
        self.ourKiller = None
        self.kills = set([])


    def gotPlayerKilledMsg(self, msg):
        if msg.targetId == self.player.id:
            self.ourKiller = msg.killerId
            if msg.killerId in self.kills:
                self.achievementUnlocked()
        elif msg.killerId == self.player.id:
            self.kills.add(msg.targetId)
            if msg.targetId == self.ourKiller:
                self.achievementUnlocked()

    def gotRespawnMsg(self, msg):
        if msg.playerId == self.player.id:
            self.ourKiller = None
        else:
            self.tryRemove(msg.playerId)

    def tryRemove(self, playerId):
        if playerId in self.kills:
            self.kills.remove(playerId)

    def gotRemovePlayerMsg(self, msg):
        self.tryRemove(msg.playerId)

@availableAchievements.register
class SnatchedZone(OncePerPlayerPerGame):
    idstring = 'snatched'
    name = 'Snatched from the Jaws'
    # This should not be awarded if the tagging team would have been able to tag
    # anyway
    description = 'Tag a zone just before an enemy was about to respawn in it'
    snatchTime = 0.5
    messages = (TaggingZoneMsg,)

    @checkPlayerId
    def gotTaggingZoneMsg(self, msg):
        zone = self.world.getZone(msg.zoneId)
        team = self.world.getTeam(msg.teamId)

        almostDefenders = 0
        for ghost in zone.nonPlayers:
            assert ghost.ghost
            if ghost.team != team and ghost.respawnGauge < self.snatchTime:
                almostDefenders += 1
        actualDefenders = 0
        actualAttackers = 0
        for player in zone.players:
            if player.team == team:
                actualAttackers += 1
            else:
                if not player.turret:
                    actualDefenders += 1
        if (not ZoneState.canTag(actualAttackers, actualDefenders +
                almostDefenders) and zone.previousOwner is not None):
            # Couldn't have tagged if we'd been half a second later
            self.achievementUnlocked()

@availableAchievements.register
class KilledByNobody(KilledSomeoneAchievement, OncePerPlayerPerGame):
    name = 'And Who Deserves the Blame?'
    description = 'Die with no-one being awarded a kill'
    idstring = 'killedByNobody'
    messages = (PlayerKilledMsg,)

    def gotPlayerKilledMsg(self, msg):
        if msg.targetId == self.player.id and msg.killerId == '\x00':
            self.achievementUnlocked()

@availableAchievements.register
class ShieldRevenge(OncePerPlayerPerGame):
    name = 'Shields Up, Weapons Online'
    description = 'Kill the enemy who shot your shield within ten seconds'
    idstring = 'shieldRevenge'

    timeWindow = 10 # Seconds
    messages = (ShotAbsorbedMsg, PlayerKilledMsg)

    def __init__(self, player, world, outPlug):
        super(ShieldRevenge, self).__init__(player, world, outPlug)
        self.shieldKillers = []

    def gotShotAbsorbedMsg(self, msg):
        if msg.targetId == '\x00':
            return
        if (msg.targetId == self.player.id and self.player.upgrade is not None
                and self.player.upgrade.upgradeType == 's'):
            # Our shield got hit
            self.shieldKillers.append((self.world.getElapsedTime(),
                    self.world.getPlayer(msg.shooterId)))

    def gotPlayerKilledMsg(self, msg):
        if msg.killerId == self.player.id:
            self.killedSomeone(msg)
        elif msg.targetId == self.player.id:
            self.gotKilled(msg)

    def gotKilled(self, msg):
        self.shieldKillers = []

    def killedSomeone(self, msg):
        target = self.world.getPlayer(msg.targetId)
        currentTime = self.world.getElapsedTime()
        for time, attacker in list(self.shieldKillers):
            if currentTime - time > self.timeWindow:
                self.shieldKillers.remove((time, attacker))
            elif attacker == target:
                self.achievementUnlocked()
                break

@availableAchievements.register
class ShieldThenKill(OncePerPlayerPerGame):
    name = 'Armour-Piercing Bullets'
    description = 'Kill an enemy after destroying their shields'
    idstring = 'destroyShield'

    timeWindow = 10 # Seconds
    messages = (ShotAbsorbedMsg, PlayerKilledMsg)

    def __init__(self, player, world, outPlug):
        super(ShieldThenKill, self).__init__(player, world, outPlug)
        self.shieldsKilled = []

    def gotShotAbsorbedMsg(self, msg):
        if msg.targetId == '\x00':
            return
        target = self.world.getPlayer(msg.targetId)
        if (msg.shooterId == self.player.id and target.upgrade is not None and
                target.upgrade.upgradeType == 's'):
            # We hit their shield
            self.shieldsKilled.append((self.world.getElapsedTime(), target))

    def gotPlayerKilledMsg(self, msg):
        if msg.targetId == self.player.id:
            self.gotKilled(msg)
        elif msg.killerId == self.player.id:
            self.killedSomeone(msg)

    def gotKilled(self, msg):
        self.shieldsKilled = []

    def killedSomeone(self, msg):
        target = self.world.getPlayer(msg.targetId)
        currentTime = self.world.getElapsedTime()
        for time, victim in list(self.shieldsKilled):
            if currentTime - time > self.timeWindow:
                self.shieldsKilled.remove((time, victim))
            elif victim == target:
                self.achievementUnlocked()
                break

@availableAchievements.register
class ShieldDefense(OncePerPlayerPerGame):
    name = 'Strategic Deployment'
    description = 'Activate a shield just before being shot'
    idstring = 'shieldDefense'

    timeWindow = 0.2 # seconds
    messages = (PlayerHasUpgradeMsg, ShotAbsorbedMsg)
    shieldTime = None

    @checkPlayerId
    def gotPlayerHasUpgradeMsg(self, msg):
        if msg.upgradeType == 's':
            self.shieldTime = self.world.getElapsedTime()

    def gotShotAbsorbedMsg(self, msg):
        if msg.targetId == self.player.id and self.shieldTime is not None:
            currentTime = self.world.getElapsedTime()
            if (currentTime - self.shieldTime) <= self.timeWindow:
                self.achievementUnlocked()

@availableAchievements.register
class LastManStanding(OncePerTeamPerGame):
    name = 'Never Give Up'
    description = 'Be the last surviving member of your team'
    idstring = 'surviveLast'
    afterGame = True
    messages = (PlayerKilledMsg, GameOverMsg)

    def __init__(self, world, team, outPlug):
        super(LastManStanding, self).__init__(world, team, outPlug)

    def gotPlayerKilledMsg(self, msg):
        self.check()
    def gotGameOverMsg(self, msg):
        self.check()

    def check(self):
        remaining = []

        for player in self.world.players:
            if player.team == self.team:
                remaining.append(player)

        if len(remaining) == 1:
            self.achievementUnlocked([remaining[0]])

##################
# Leader Killing #
##################
leaderAchievements = {
                      'adonal': 'Drum Solo',
                      'dcatch': 'Jerakeen Genocide',
                      'dmenge': "Trolling Ain't Easy",
                      'jbartl': 'The Bigger They Are...',
                      'jowen':  'Zergling Rush',
                      'jredmo': 'Kernel Panic',
                      'khethe': 'Vespene Geyser Exhausted',
                      'kjohns': 'All Your Bass are Belong to Us',
                      'lsharl': 'Knight of Catan',
                      'mbrand': 'How do I shot web?',
                      'mwalla': "School's Out",
                      'shorn':  'Employee of the Month',
                      'tirwin': 'Uncomfortably Energetic',
                      'tryan':  'Nerf Warfare'
                      }

leaderNames =        {'adonal': 'ErbaneOrb',
                      'dcatch': 'Kindred',
                      'dmenge': 'Cricket',
                      'jbartl': 'Hrodga',
                      'jowen':  'Nobody',
                      'jredmo': 'Avatar',
                      'khethe': 'Scarecrow',
                      'kjohns': 'Kain',
                      'lsharl': 'Dr. Strangelove',
                      'mbrand': 'PorridgeLord',
                      'mwalla': 'Jupator',
                      'shorn':  'Clamburger',
                      'tirwin': 'Bundy',
                      'tryan':  'Acne'
                      }

leaderAchievements = additionalLeaders = {} # We are not on camp.

def getLeaderDescription(name):
    return 'Kill %s three times' % (leaderNames[name],)
def stripPunctuation(nick):
    exclude = set(string.punctuation + ' ')
    return ''.join(ch for ch in nick if ch not in exclude)

for username, achievementName in leaderAchievements.iteritems():
    @availableAchievements.register
    class LeaderMultiKill(KilledSomeoneAchievement, IncrementingAchievement,
            OnceEverPerPlayer):
        requiredQuantity = 3
        idstring = 'leader' + stripPunctuation(username)
        name = achievementName
        description = getLeaderDescription(username)
        username = username

        def killedSomeone(self, msg):
            player = self.world.getPlayer(msg.targetId)
            if player.user is None:
                return
            username = player.user.username
            if username == self.username:
                self.increment()

#disabled @availableAchievements.register
class DeveloperKills(KilledSomeoneAchievement, IncrementingAchievement,
        OnceEverPerPlayer):
    idstring = 'developerKills'
    name = 'Developer Destroyer'
    description = 'Rack up 10 developer kills'
    requiredQuantity = 10

    developers = ('jbartl', 'adonal', 'shorn',
                  'hrodga', 'erbaneorb', 'clamburger')

    def killedSomeone(self, msg):
        player = self.world.getPlayer(msg.targetId)
        if player.user is None:
            return
        nick = stripPunctuation(player.user.username).lower()
        if nick in self.developers:
            self.increment()

def lower(string):
    return string.lower()

#disabled @availableAchievements.register
class KillEveryLeader(KilledSomeoneAchievement, PersistedChecklistAchievement):
    idstring = 'killEveryLeader'
    name = 'Leaders vs Campers'
    description = 'Kill every leader at least once'
    requiredItems = set(map(stripPunctuation,
                            map(lower, leaderAchievements.keys()
                                    + additionalLeaders.keys())))

    def killedSomeone(self, msg):
        player = self.world.getPlayer(msg.targetId)
        if player.user is None:
            return
        nick = stripPunctuation(player.user.username).lower()
        if nick in self.requiredItems:
            self.addItem(nick)
