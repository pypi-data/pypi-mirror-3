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

'''upgrades.py - defines the behaviour of upgrades.'''

import logging

import pygame

from trosnoth.utils.checkpoint import checkpoint
from trosnoth.model.shot import GrenadeShot

from trosnoth.messages import GrenadeExplosionMsg

log = logging.getLogger('upgrades')

upgradeOfType = {}
allUpgrades = set()

def registerUpgrade(upgradeClass):
    '''
    Marks the given upgrade class to be used in the game.
    '''
    specialUpgrade(upgradeClass)
    allUpgrades.add(upgradeClass)

    return upgradeClass

def specialUpgrade(upgradeClass):
    '''
    Marks the given upgrade class as a special upgrade that can be used only via
    the console.
    '''
    if upgradeClass.upgradeType in upgradeOfType:
        raise KeyError('2 upgrades with %r' % (upgradeClass.upgradeType,))
    upgradeOfType[upgradeClass.upgradeType] = upgradeClass

    return upgradeClass

class Upgrade(object):
    '''Represents an upgrade that can be bought.'''
    goneWhenDie = True
    defaultKey = None
    iconPath = None
    iconColourKey = (255, 255, 255)

    # Upgrades have an upgradeType: this must be a unique, single-character
    # value.
    def __init__(self, player):
        self.universe = player.universe
        self.player = player

    def __str__(self):
        return self.name

    def use(self):
        '''Initiate the upgrade (client-side)'''
        pass

    def delete(self):
        '''Performs any necessary tasks to remove this upgrade from the game.'''
        self.player.upgrade = None

    def timeIsUp(self):
        '''
        Called by the universe when the upgrade's time has run out.
        '''

@registerUpgrade
class Shield(Upgrade):
    '''
    shield: protects player from one shot
    '''
    upgradeType = 's'
    requiredStars = 4
    timeRemaining = 30
    shotsCanTake = 1
    name = 'Shield'
    action = 'shield'
    order = 20
    defaultKey = pygame.K_2
    iconPath = 'upgrade-shield.png'

    def __init__(self, player):
        super(Shield, self).__init__(player)
        self.protections = self.shotsCanTake
        checkpoint('Shield created')

@specialUpgrade
class PhaseShift(Upgrade):
    '''
    phase shift: affected player cannot be shot, but cannot shoot.
    '''
    upgradeType = 'h'
    requiredStars = 6
    timeRemaining = 25
    name = 'Phase Shift'
    action = 'phase shift'
    order = 40
    defaultKey = pygame.K_4
    iconPath = 'upgrade-phaseshift.png'

    def __init__(self, player):
        super(PhaseShift, self).__init__(player)
        checkpoint('Phase shift created')

@specialUpgrade
class Turret(Upgrade):
    '''
    turret: turns a player into a turret; a more powerful player, although one
    who is unable to move.
    '''
    upgradeType = 't'
    requiredStars = 8
    timeRemaining = 50
    name = 'Turret'
    action = 'turret'
    order = 10
    defaultKey = pygame.K_1
    iconPath = 'upgrade-turret.png'

    def use(self):
        '''Initiate the upgrade'''
        self.player.detachFromEverything()
        if self.player.currentZone.turretedPlayer is not None:
            self.player.currentZone.turretPlayer.upgrade.delete()
        self.player.currentZone.turretedPlayer = self.player

        # Arrest vertical movement so that upon losing the upgrade, the
        # player doesn't re-jump
        self.player.yVel = 0

        super(Turret, self).use()
        checkpoint('Turret used (client side)')

    def delete(self):
        '''Performs any necessary tasks to remove this upgrade from the game'''
        self.player.turretOverHeated = False
        self.player.turretHeat = 0.0
        self.player.currentZone.turretedPlayer = None
        super(Turret, self).delete()
        checkpoint('Turret deleted (client side)')

@registerUpgrade
class MinimapDisruption(Upgrade):
    upgradeType = 'm'
    requiredStars = 15
    timeRemaining = 40
    name = 'Minimap Disruption'
    action = 'minimap disruption'
    order = 30
    defaultKey = pygame.K_3
    iconPath = 'upgrade-minimap.png'

    def use(self):
        if self.player.team is not None:
            self.player.team.usingMinimapDisruption = True
            checkpoint('Minimap disruption used (client side)')

    def delete(self):
        if self.player.team is not None:
            self.player.team.usingMinimapDisruption = False
            super(MinimapDisruption, self).delete()

GRENADE_BLAST_RADIUS = 448

@registerUpgrade
class Grenade(Upgrade):
    upgradeType = 'g'
    requiredStars = 7
    timeRemaining = 2.5
    goneWhenDie = False
    numShots = 40
    name = 'Grenade'
    action = 'grenade'
    order = 50
    defaultKey = pygame.K_5
    iconPath = 'upgrade-grenade.png'

    def __init__(self, player):
        self.gr = None                          # Client-side.
        super(Grenade, self).__init__(player)
        checkpoint('Grenade upgrade created')

    def use(self):
        '''Initiate the upgrade.'''
        if self.gr is not None:
            log.warning('** Stray grenade')
            self.gr.delete()

        self.gr = GrenadeShot(self.player.universe, self.player)
        self.player.universe.addGrenade(self.gr)

        super(Grenade, self).use()
        checkpoint('Grenade used (client side)')

    def delete(self):
        '''Performs any necessary tasks to remove this upgrade from the game'''
        if self.gr is not None:
            self.universe.removeGrenade(self.gr)
            self.gr = None
        super(Grenade, self).delete()
        checkpoint('Grenade deleted (client side)')

    def timeIsUp(self):
        killerId = self.player.id
        xpos, ypos = self.gr.pos
        self.universe.eventPlug.send(GrenadeExplosionMsg(xpos, ypos))

        for player in self.universe.players:
            if (player.isFriendsWith(self.player) or player.phaseshift or
                    player.isInvulnerable() or player.turret or player.ghost):
                continue
            dist = ((player.pos[0] - xpos) ** 2 +
                    (player.pos[1] - ypos) ** 2) ** 0.5
            if dist <= GRENADE_BLAST_RADIUS:
                player.hurtBy(killerId, None, 'G')

@registerUpgrade
class Ricochet(Upgrade):
    upgradeType = 'r'
    requiredStars = 3
    timeRemaining = 10
    name = 'Ricochet'
    action = 'ricochet'
    order = 60
    defaultKey = pygame.K_6
    iconPath = 'upgrade-ricochet.png'

    def use(self):
        '''Initiate the upgrade'''
        super(Ricochet, self).use()
        checkpoint('Ricochet used (client side)')

    def delete(self):
        '''Performs any necessary tasks to remove this upgrade from the game'''
        super(Ricochet, self).delete()
        checkpoint('Ricochet delete (client side)')

@registerUpgrade
class Ninja (Upgrade):
    '''allows you to become invisible to all players on the opposing team'''
    upgradeType = 'n'
    requiredStars = 5
    timeRemaining = 25
    name = 'Ninja'
    action = 'phase shift' # So old phase shift hotkeys trigger ninja.
    order = 40
    defaultKey = pygame.K_4
    iconPath = 'upgrade-ninja.png'
    iconColourKey = (254, 254, 253)

    def use(self):
        '''Initiate the upgrade'''
        super(Ninja, self).use()
        checkpoint('Ninja used (client side)')

    def delete(self):
        '''Performs any necessary tasks to remove this upgrade from the game'''
        super(Ninja, self).delete()
        checkpoint('Ninja delete (client side)')

@registerUpgrade
class Shoxwave(Upgrade):
    '''
    shockwave: upgrade that will replace shots with a shockwave like that of the
    grenade vaporising all enemies and enemy shots in the radius of blast.
    '''
    upgradeType = 'w'
    requiredStars = 7
    timeRemaining = 45
    name = 'Shoxwave'
    action = 'shoxwave'
    order = 80
    defaultKey = pygame.K_7
    iconPath = 'upgrade-shoxwave.png'

    def use(self):
        '''Initiate the upgrade'''
        super(Shoxwave, self).use()
        checkpoint('Shoxwave used (client side)')

    def delete(self):
        super(Shoxwave, self).delete()
        checkpoint('Shoxwave delete (client side)')

@registerUpgrade
class MachineGun(Upgrade):
    upgradeType = 'x'
    requiredStars = 10
    timeRemaining = 30
    name = 'Machine Gun'
    action = 'turret'   # So that old turret hotkeys trigger machine gun.
    order = 10
    defaultKey = pygame.K_1
    iconPath = 'upgrade-machinegun.png'

    def use(self):
        self.player.mgBulletsRemaining = 15
        self.player.mgFiring = False

    def delete(self):
        super(MachineGun, self).delete()
        self.player.mgBulletsRemaining = 0

@specialUpgrade
class RespawnFreezer(Upgrade):
    '''
    Respawn freezer: upgrade that will render spawn points unusable.
    '''
    upgradeType = 'f'
    requiredStars = 8
    timeRemaining = 30
    name = 'Respawn Freezer'
    action = 'respawn freezer'
    order = 100
    defaultKey = pygame.K_8
    iconPath = 'upgrade-freezer.png'

    def use(self):
        '''Initiate the upgrade'''
        super(RespawnFreezer, self).use()
        self.player.currentZone.frozen = True
        checkpoint('Respawn Freezer used (client side)')

    def delete(self):
        '''Performs any necessary tasks to remove this upgrade from the game'''
        super(RespawnFreezer, self).delete()
        self.player.currentZone.frozen = False
        checkpoint('Respawn Freezer delete (client side)')

@specialUpgrade
class Directatorship(Upgrade):
    '''
    Directatorship: shielded ninja ricochet machine gunner.
    '''
    upgradeType = 'd'
    requiredStars = 150
    timeRemaining = 60
    name = 'Directatorship'
    action = 'directatorship'
    order = 200
    protections = 1
