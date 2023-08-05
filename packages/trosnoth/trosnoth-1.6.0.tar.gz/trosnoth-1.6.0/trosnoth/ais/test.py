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

from trosnoth.ais.alpha import AlphaAI

from twisted.internet import task

class TestingAI(AlphaAI):
    nick = 'TestAI'
    playable = True

    # Use these toggles to change the behaviour of the bots.
    canMove = True
    canShoot = True
    canJump = True
    upgradeType = None

    def start(self):
        super(TestingAI, self).start()
        self._loop = task.LoopingCall(self.tick)
        self._loop.start(0.5)

    def tick(self):
        if (not self.player.dead and self.player.upgrade is None
               and self.upgradeType is not None):
            self.doBuyUpgrade(self.upgradeType)

    def shoot(self):
        if self.canShoot:
            super(TestingAI, self).shoot()

    def changeXDir(self):
        if self.canMove:
            super(TestingAI, self).changeXDir()

    def jumpAgain(self):
        if self.canJump:
            super(TestingAI, self).jumpAgain()

AIClass = TestingAI
