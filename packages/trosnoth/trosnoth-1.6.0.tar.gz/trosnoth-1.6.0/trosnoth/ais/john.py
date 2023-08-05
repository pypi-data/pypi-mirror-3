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
from trosnoth.ai import AI
import trosnoth.model.shot as shot

from trosnoth.model.upgrades import *
from twisted.internet import reactor, task

class JohnAI(AI):
    '''
    In version 1.1.3 the computer(AI) players have the following functions:
    1. The robot runs "intelligently" around the map until it gets confused with a block.
    2. The robot's shooting is randomly off to make it more human like.
    3. The  robot gets confused less
    4. The robot talks less
    5. The robot gets confused by Minimap Disruption
    6. The robot don't shoot players that are invisible.
    7. Uses Grenades when there are 3 players in its current zone
    This file was edited by John "AIMaker" Board at home. 28/12/10 3:57 PM
    '''

    nick = 'JohnAI'
    playable = True

    def start(self):
        self._pauseTimer = None
        self._loop = task.LoopingCall(self.tick)
        self._loop.start(0.5)
        self.numOfKills = 0
        self.rank = ""

    def disable(self):
        self._loop.stop()
        if self._pauseTimer is not None:
            self._pauseTimer.cancel()


    def tick(self):
        self.beforeX = self.player.pos[0]
        if self.player.dead:
            if self.player.inRespawnableZone():
                self.doAimAt(0, thrust=0)
                if self.player.respawnGauge == 0:
                    self.doRespawn()
            else:
                self.aimAtFriendlyZone()
        else:
            if self._pauseTimer is None:
                self.startPlayerMoving()
            if self.player.canShoot():
                self.fireAtNearestEnemy()
            self.useUpgrade()

    def promote(self):
        currRank = self.rank
        if self.numOfKills > 1:
            self.rank = "Private"
        if self.numOfKills > 5:
            self.rank = "Private Second Class"
        if self.numOfKills > 10:
            self.rank = "Private First Class"
        if self.numOfKills > 15:
            self.rank = "Corporal"
        if self.numOfKills > 20:
            self.rank = "Sergeant"
        if self.numOfKills > 25:
            self.rank = "Staff Sergeant"
        if self.numOfKills > 30:
            self.rank = "Sergeant First Class"
        if self.numOfKills > 35:
            self.rank = "Master Sergeant"
        if self.numOfKills > 40:
            self.rank = "Sergeant Major"
        if self.numOfKills > 45:
            self.rank = "Warrant Officer"
        if self.numOfKills > 50:
            self.rank = "Chief Warrant Officer"
        if self.numOfKills > 55:
            self.rank = "Second Lieutenant"
        if self.numOfKills > 60:
            self.rank = "First Lieutenant"
        if self.numOfKills > 65:
            self.rank = "Capitan"
        if self.numOfKills > 70:
            self.rank = "Major"
        if self.numOfKills > 75:
            self.rank = "Lieutenant Colonel"
        if self.numOfKills > 80:
            self.rank = "Colonel"
        if self.numOfKills > 85:
            self.rank = "Brigadier General"
        if self.numOfKills > 90:
            self.rank = "Major General"
        if self.numOfKills > 95:
            self.rank = "Lieutenant General"
        if self.numOfKills > 100:
            self.rank = "General"
        if not self.rank == currRank:
            msg = str(self.player.nick) + "'s rank was set to " + self.rank + ", Congrats."
            self.doSendPublicChat(msg)

    def checkEnemyUpgrade(self):
        enemies = [p for p in self.world.players if not
                   (p.dead or self.player.isFriendsWith(p))]
        upgrade = [str(p.upgrade) for p in enemies if not p.upgrade == None]
        return upgrade

    def useUpgrade(self):
        if len(self.getEnemyPlayersInZone()) > 3:
            self.doBuyUpgrade(Grenade)
            doChat = random.randint(0,5)
            if doChat == 3:
                msg = random.choice(["bombs away","Its a showdown, let me share this pineapple between us","KABOOM"])
                self.doSendPublicChat(msg)
            
    def aimAtFriendlyZone(self):
        zones = [z for z in self.world.zones if z.orbOwner == self.player.team]
        if len(zones) == 0:
            return

        def getZoneDistance(zone):
            x1, y1 = self.player.pos
            x2, y2 = zone.defn.pos
            return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

        bestZone = min(zones, key=getZoneDistance)
        self.doAimAtPoint(bestZone.defn.pos)

    def fireAtNearestEnemy(self):
        enemies = [p for p in self.world.players if not
                (p.dead or p.invisible or self.player.isFriendsWith(p))]
        if len(enemies) == 0:
            return

        def getPlayerDistance(p):
            x1, y1 = self.player.pos
            x2, y2 = p.pos
            return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

        nearestEnemy = min(enemies, key=getPlayerDistance)
        if getPlayerDistance(nearestEnemy) < 300:                       #If you get closer than these many pixles you will get shot at, orig value = 512, it is determind by the difficulty rating
            if not nearestEnemy.invisible == True:                #This if statement is here to make the AIs not shoot at ninjaed players
                pos = (nearestEnemy.pos[0] + (random.random() * 100),   #These lines take the nearestEnemy.pos aand tweak the randomly to give the a human error.
                   nearestEnemy.pos[1] + (random.random() * 100))
                self.doAimAtPoint(pos)
                self.doShoot()

    def totalOfEnemies(self):
        enemies = [p for p in self.world.players if not
                (p.dead or self.player.isFriendsWith(p))]
        return len(enemies)
    
    def getEnemyPlayersInZone(self):
        zone = self.player.currentZone
        return [p for p in zone.players
                if not self.player.isFriendsWith(p)]

    def getEnemyPlayerCount(self):
        return len(self.getEnemyPlayersInZone())

    def died(self, killerId):
        self._pauseTimer = None
        self.doStop()
        self.aimAtFriendlyZone()
        radSend = random.randint(0,5)
        if radSend == 1:
            msg = random.choice(['HMMMMMMMMM','Time To Improve Stratergy','Respawning in 3..2..1....','AUGHHHHHHHH']) #Add messages at will
            self.doSendPublicChat(msg)  

    def respawned(self):
        self.startPlayerMoving()

    def startPlayerMoving(self):
        self.pauseAndReconsider()

    def posOfOrb(self):    
        return self.player.currentZone.defn.pos

    def pauseAndReconsider(self):
        self.beforeX = self.player.pos[0]
        if self.player.dead:
            self._pauseTimer = None
            return

        # Pause again in between 0.5 and 2.5 seconds time.
        t = random.random() * 0.2 + 0.2
        self._pauseTimer = reactor.callLater(t, self.pauseAndReconsider)

        # Decide on a direction.
        def getPlayerDistance(p):
            x1, y1 = self.player.pos
            x2, y2 = p.pos
            return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
        enemies = [p for p in self.world.players if not
                (p.dead or self.player.isFriendsWith(p))]
        if len(enemies) > 0:
            nearestEnemy = min(enemies, key=getPlayerDistance)
        if "Minimap Disruption" in self.checkEnemyUpgrade():
                self.randomMove()
        if len(enemies) > 0:
            if self.player.currentZone.orbOwner == self.player.team:
                x = nearestEnemy.pos[0]
                y = nearestEnemy.pos[1]
                self.moveToward(x,y)
        elif not self.player.currentZone.orbOwner == self.player.team:
            if self.getEnemyPlayerCount() == 0:
                x = self.posOfOrb()[0]
                y = self.posOfOrb()[1]
                self.moveToward(x,y)

    def randomMove(self):
        d = random.choice(['drop','jump','left','right'])
        if d == 'drop':
            self.doDrop()
        if d == 'jump':
            self.doJump()
        if d == 'left':
            self.doMoveLeft()
        if d == 'right':
            self.doMoveRight()

        
        
    def someoneDied(self, target, killerId):
        if (not self.player.isFriendsWith(target)) and not target.bot:
            self.numOfKills = self.numOfKills + 1
            self.promote()
            radSend = random.randint(0,5)
            if radSend == 1:
                msg = random.choice(['HAHAHAHAHAHAH','You Can Play Harder!','Robots Rule!', 'You Should Protect Doug', 'Lynched!', "I'm a Meteor", "It's Over Nine THOUSAAAAAAND", 'Mwahhhhhahhahahhhhahh', 'May The Power Be With Us!', 'Robots are Go!', "Hoodwinked!"]) #Add messages at will.
                self.doSendPublicChat(msg)

    def moveToward(self,x,y):
        if x > self.player.pos[0] and self.player.isAttachedToWall():
            self.doAimAt(pi/2.)
            self.doMoveRight()
            self.doJump()
        if x < self.player.pos[0] and self.player.isAttachedToWall():
            self.doAimAt(-pi/2.)
            self.doMoveLeft()
            self.doJump()
        if x > self.player.pos[0] and self.player.isOnGround():
            self.doAimAt(pi/2.)
            self.doMoveRight()
            self.doJump()
        if x < self.player.pos[0] and self.player.isOnGround():
            self.doAimAt(-pi/2.)
            self.doMoveLeft()
            self.doJump()
        if y > self.player.pos[1] and self.player.isOnPlatform():
            self.doDrop()
        if y < self.player.pos[1]:
            self.doJump()
        if x == self.player.pos[0] and y < self.player.pos[1]:
            self.doJump()
        if x == self.player.pos[0] and y > self.player.pos[1]:
            self.doDrop()

AIClass = JohnAI
