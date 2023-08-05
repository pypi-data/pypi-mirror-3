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

'''modes.py: defines a set of pre-defined game modes'''


class PhysicsConstants(object):
    def __init__(self):
        self.setModeNormal()

    def hasMode(self, gameMode):
        return hasattr(self, 'setMode' + gameMode)

    def setMode(self, gameMode):
        try:
            fn = getattr(self, 'setMode' + gameMode)
        except (AttributeError, TypeError):
            return False

        fn()
        return True

    def _standard(self, pace=1, fireRate=1, gravity=1, jumpHeight=1,
            respawnRate=1, shotSpeed=1, shotLength=1, bounce=False,
            respawnHealth=1, shooting=True):

        self.shooting = shooting

        # Speed that shots travel at.
        self.shotSpeed = 600 * shotSpeed                      # pix/s
        self.shotLifetime = (1. / shotSpeed) * shotLength     # s

        # The following values control player movement.
        self.playerXVel = 360 * pace                  # pix/s
        self.playerSlowXVel = 180 * pace              # pix/s
        self.playerMaxGhostVel = 675. * pace          # pix/s
        self.playerJumpThrust = 540 * jumpHeight      # pix/s
        self.playerMaxFallVel = 540. * gravity        # pix/s
        self.playerMaxJumpTime = 0.278                # s
        self.playerGravity = 3672 * gravity           # pix/s/s
        self.playerOwnReloadTime = 1 / 2.7 / fireRate      # s
        self.playerNeutralReloadTime = 1 / 2. / fireRate   # s
        self.playerEnemyReloadTime = 1 / 1.4 / fireRate    # s
        self.playerTurretReloadTime = 0.083 / fireRate     # s
        self.playerMachineGunReloadTime = 4 / fireRate   # s
        self.playerMachineGunFireRate = 0.1 / fireRate   # s
        self.playerTurretHeatCapacity = 2.4 * fireRate
        self.playerShotHeat = 0.4
        self.playerRespawnTotal = 7.5 / respawnRate
        self.playerBounce = bounce
        self.playerRespawnHealth = respawnHealth
        self.playerShoxwaveReloadTime = self.playerEnemyReloadTime

        self.grenadeMaxFallVel = 540. * gravity
        self.grenadeGravity = 300 * gravity
        self.grenadeInitVel = 400 * pace

    def setModeNoShots(self):
        self._standard(shooting=False)

    def setModeLightning(self):
        self._standard(pace=1.75, fireRate=2)

    def setModeLowGravity(self):
        self._standard(gravity=0.25)

    def setModeNormal(self):
        self._standard()

    def setModeFastFire(self):
        self._standard(fireRate=3, shotSpeed=2)

    def setModeInsane(self):
        self._standard(pace=1.75, fireRate=3, jumpHeight=2, shotSpeed=2,
                        shotLength=2, respawnRate=60)

    def setModeFastRespawn(self):
        self._standard(respawnRate=60)

    def setModeSlow(self):
        self._standard(pace=0.5, gravity=0.25, jumpHeight=0.7, shotSpeed=0.5)

    def setModeHighFastFall(self):
        self._standard(jumpHeight=2, gravity=2)

    def setModeLaser(self):
        self._standard(shotSpeed=30, shotLength=100)

    def setModeManyShots(self):
        self._standard(shotLength=20)

    def setModeZeroG(self):
        self._standard(gravity=0.001)

    def setModeAntiG(self):
        self._standard(gravity=-0.1)

    def setModeBouncy(self):
        self._standard(bounce=True)

    def setModeHighBouncy(self):
        self._standard(bounce=True, jumpHeight=3)

    def setModeTwoLives(self):
        self._standard(respawnHealth=2)
