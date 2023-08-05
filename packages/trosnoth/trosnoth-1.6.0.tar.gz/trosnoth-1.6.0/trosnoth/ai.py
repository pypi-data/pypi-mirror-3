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
import random

from trosnoth.utils.components import Component, Plug, handler
from trosnoth.messages import (TaggingZoneMsg, ShootMsg, RespawnMsg,
        RespawnRequestMsg, PlayerKilledMsg, JoinRequestMsg, JoinSuccessfulMsg,
        CannotJoinMsg, UpdatePlayerStateMsg, AimPlayerAtMsg, RemovePlayerMsg,
        BuyUpgradeMsg, ChatMsg)
from trosnoth.model.universe_base import NeutralTeamId
from trosnoth.utils.twist import WeakCallLater, WeakLoopingCall
import trosnoth.ais
from math import atan2

log = logging.getLogger('ai')

def listAIs(playableOnly=False):
    '''
    Returns a list of strings of the available AI classes.
    '''
    results = []
    try:
        files = os.listdir(os.path.dirname(trosnoth.ais.__file__))
    except OSError:
        # Probably frozen in a zip. Use a standard list.
        aiNames = ['alpha', 'simple', 'john', 'test']
    else:
        aiNames = [os.path.splitext(f)[0] for f in files if f.endswith('.py')]

    for aiName in aiNames:
        c = __import__('trosnoth.ais.%s' % (aiName,), fromlist=['AIClass'])
        if hasattr(c, 'AIClass') and (c.AIClass.playable or not
                playableOnly):
            results.append(aiName)
    return results

def makeAIAgent(world, aiName):
    c = __import__('trosnoth.ais.%s' % (aiName,), fromlist=['AIClass'])
    return AIAgent(world, c.AIClass)

class AIAgent(Component):
    '''
    Base class for an AI agent.
    '''
    eventPlug = Plug()
    requestPlug = Plug()
    aiPlug = Plug()

    def __init__(self, world, aiClass):
        Component.__init__(self)
        self.world = world
        self.aiClass = aiClass
        self.ai = None
        self.playerId = None
        self.team = None
        self._reqNicks = {}
        self._loop = WeakLoopingCall(self, '_tick')

    def start(self, team=None):
        self.team = team
        self._loop.start(2)

    def stop(self):
        self._loop.stop()

    def _tick(self):
        if self.ai is not None:
            return
        if not self.world.state.aisEnabled():
            return

        nick = self.aiClass.nick

        if self.team is None:
            teamId = NeutralTeamId
        else:
            teamId = self.team.id

        reqTag = random.randrange(1<<32)
        self._joinGame(nick, teamId, reqTag, 1)

    def _joinGame(self, nick, teamId, reqTag, attempt):
        self._reqNicks[reqTag] = (nick, attempt)
        nick = '%s-%d' % (nick, attempt)
        msg = JoinRequestMsg(teamId, reqTag, nick=nick.encode(), bot=True)
        msg.localBotRequest = True
        self.requestPlug.send(msg)
        return reqTag

    @handler(JoinSuccessfulMsg, eventPlug)
    def _joinSuccessful(self, msg):
        if msg.tag in self._reqNicks:
            del self._reqNicks[msg.tag]
        player = self.world.playerWithId[msg.playerId]
        self.ai = self.aiClass(self.world, player)
        self.playerId = player.id
        self.aiPlug.connectPlug(self.ai.plug)

    @handler(CannotJoinMsg, eventPlug)
    def _joinFailed(self, msg):
        r = msg.reasonId
        if msg.tag in self._reqNicks:
            nick, attempt = self._reqNicks.pop(msg.tag)
        else:
            nick = None

        if r == 'F':
            log.error('Join failed for AI %r (full)', nick)
        elif r == 'W':
            log.error('Join failed for AI %r (wait)', nick)
        elif r == 'A':
            log.error('Join failed for AI %r (not authenticated)', nick)
            self.stop()
        elif r == 'N':
            if nick is None:
                log.warning('Join failed for AI %r (nick)',
                        self.aiClass.__name__)
            else:
                attempt += 1
                self._joinGame(nick, msg.teamId, msg.tag, attempt)
        elif r == 'U':
            log.error('Join failed for AI %r (user already in auth game)', nick)
            self.stop()
        else:
            log.error('Join failed for AI %r (%r)', nick, r)

    @handler(RemovePlayerMsg, eventPlug)
    def _removePlayer(self, msg):
        if msg.playerId == self.playerId:
            self.ai.disable()
            self.ai = None
            self.playerId = None
            self.aiPlug.disconnectAll()

    @eventPlug.defaultHandler
    def gotEventMsg(self, msg):
        self.aiPlug.send(msg)

    @aiPlug.defaultHandler
    def gotAIMsg(self, msg):
        self.requestPlug.send(msg)

class AI(Component):
    playable = False    # Change to True in playable subclasses.
    plug = Plug()

    def __init__(self, world, player):
        Component.__init__(self)
        self.world = world
        self.player = player
        self.start()

    def start(self):
        raise NotImplementedError

    def disable(self):
        raise NotImplementedError

    @plug.defaultHandler
    def _ignoreMessage(self, msg):
        pass

    def doMoveRight(self):
        if self.alreadyRemoved():
            return
        self.plug.send(UpdatePlayerStateMsg(self.player.id, True,
                stateKey='right'))
        self.plug.send(UpdatePlayerStateMsg(self.player.id, False,
                stateKey='left'))

    def doMoveLeft(self):
        if self.alreadyRemoved():
            return
        self.plug.send(UpdatePlayerStateMsg(self.player.id, True,
                stateKey='left'))
        self.plug.send(UpdatePlayerStateMsg(self.player.id, False,
                stateKey='right'))

    def doStop(self):
        if self.alreadyRemoved():
            return
        self.plug.send(UpdatePlayerStateMsg(self.player.id, False,
                stateKey='right'))
        self.plug.send(UpdatePlayerStateMsg(self.player.id, False,
                stateKey='left'))

    def doDrop(self):
        if self.alreadyRemoved():
            return
        self.plug.send(UpdatePlayerStateMsg(self.player.id, True,
                stateKey='down'))
        WeakCallLater(0.1, self, '_releaseDropKey')

    def _releaseDropKey(self):
        if self.alreadyRemoved():
            return
        self.plug.send(UpdatePlayerStateMsg(self.player.id, False,
                stateKey='down'))

    def doJump(self):
        if self.alreadyRemoved():
            return
        self.plug.send(UpdatePlayerStateMsg(self.player.id, True,
                stateKey='jump'))

    def doStopJump(self):
        if self.alreadyRemoved():
            return
        self.plug.send(UpdatePlayerStateMsg(self.player.id, False,
                stateKey='jump'))

    def doAimAt(self, angle, thrust=1.0):
        if self.alreadyRemoved():
            return
        self.plug.send(AimPlayerAtMsg(self.player.id, angle, thrust))

    def doAimAtPoint(self, pos, thrust=1.0):
        if self.alreadyRemoved():
            return
        x1, y1 = self.player.pos
        x2, y2 = pos
        angle = atan2(x2 - x1, -(y2 - y1))
        self.doAimAt(angle, thrust)

    def doShoot(self):
        if self.alreadyRemoved():
            return
        self.plug.send(ShootMsg(self.player.id))

    def doRespawn(self):
        '''
        Attempts to respawn.
        '''
        if self.alreadyRemoved():
            return
        self.plug.send(RespawnRequestMsg(self.player.id,
                random.randrange(1<<32)))

    def doBuyUpgrade(self, upgradeKind):
        '''
        Attempts to purchase an upgrade of the given kind.
        '''
        if self.alreadyRemoved():
            return
        self.plug.send(BuyUpgradeMsg(self.player.id, upgradeKind.upgradeType,
                random.randrange(1<<32)))

    @handler(RespawnMsg, plug)
    def _respawned(self, msg):
        if msg.playerId == self.player.id:
            self.respawned()
    def respawned(self):
        pass

    @handler(PlayerKilledMsg, plug)
    def _playerKilled(self, msg):
        if msg.targetId == self.player.id:
            self.died(msg.killerId)
        try:
            target = self.world.playerWithId[msg.targetId]
        except KeyError:
            target = None
        self.someoneDied(target, msg.killerId)

    def died(self, killerId):
        pass

    def someoneDied(self, target, killerId):
        pass

    @handler(TaggingZoneMsg, plug)
    def _zoneTagged(self, msg):
        self.zoneTagged(msg.zoneId, msg.playerId)

    def zoneTagged(self, zoneId, playerId):
        pass

    def doSendPublicChat(self, message):
        if self.alreadyRemoved():
            return
        self.plug.send(ChatMsg(self.player.id, 'o', '\x00', message.encode()))

    def alreadyRemoved(self):
        if self.player.id == -1:
            log.warning('AI trying to continue after being removed: %s' %
                    (self.__class__.__name__,))
            return True
        return False
