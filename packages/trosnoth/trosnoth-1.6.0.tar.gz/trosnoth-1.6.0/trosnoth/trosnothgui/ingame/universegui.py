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

'''
Provides a layer between a universe and the GUI, turning
players, shots, grenades into sprites, and drawing mapblocks.
'''

from trosnoth.trosnothgui.ingame.sprites import (PlayerSprite, ShotSprite,
        GrenadeSprite, ExplosionSprite, CollectableStarSprite,
        ShoxwaveExplosionSprite)

class UniverseGUI(object):
    def __init__(self, app, gameViewer, universe):
        self.app = app
        self.gameViewer = gameViewer
        self.universe = universe
        self.playerSprites = {}     # playerId -> PlayerSprite
        self.shotSprites = {}       # (playerId, shotId) -> PlayerSprite
        self.grenadeSprites = {}    # playerId -> GrenadeSprite
        self.collectableStarSprites = {}    # starId -> CollectableStarSprite
        self.extraSprites = set()

    @property
    def zones(self):
        return self.universe.zones

    @property
    def map(self):
        return self.universe.map

    @property
    def zoneBlocks(self):
        return self.universe.zoneBlocks

    def getPlayerSprite(self, playerId):
        player = self.universe.getPlayer(playerId)
        if player is None:
            return None

        try:
            p = self.playerSprites[playerId]
        except KeyError:
            self.playerSprites[player.id] = p = PlayerSprite(self.app, self,
                    player)
            return p

        if p.spriteTeam != player.team:
            # Player has changed teams.
            self.playerSprites[player.id] = p = PlayerSprite(self.app, self,
                    player)
        return p

    def iterPlayers(self):
        untouched = set(self.playerSprites.iterkeys())
        for player in self.universe.players:
            yield self.getPlayerSprite(player.id)
            untouched.discard(player.id)

        # Clean up old players.
        for playerId in untouched:
            del self.playerSprites[playerId]

    def iterGrenades(self):
        untouched = set(self.grenadeSprites.iterkeys())
        for grenade in self.universe.grenades:
            try:
                yield self.grenadeSprites[grenade.player.id]
            except KeyError:
                self.grenadeSprites[grenade.player.id] = g = (
                        GrenadeSprite(self.app, grenade))
                yield g
            else:
                untouched.discard(grenade.player.id)

        # Clean up old players.
        for grenadeId in untouched:
            del self.grenadeSprites[grenadeId]

    def iterShots(self):
        untouched = set(self.shotSprites.iterkeys())
        for shot in self.universe.shots:
            try:
                yield self.shotSprites[shot.originatingPlayer.id, shot.id]
            except KeyError:
                self.shotSprites[shot.originatingPlayer.id, shot.id] = s = (
                        ShotSprite(self.app, shot))
                yield s
            else:
                untouched.discard((shot.originatingPlayer.id, shot.id))

        # Clean up old shots.
        for playerId, shotId in untouched:
            del self.shotSprites[playerId, shotId]

    def iterCollectableStars(self):
        untouched = set(self.collectableStarSprites.iterkeys())
        for star in self.universe.collectableStars.itervalues():
            try:
                yield self.collectableStarSprites[star.id]
            except KeyError:
                self.collectableStarSprites[star.id] = s = (
                        CollectableStarSprite(self.app, star))
                yield s
            else:
                untouched.discard(star.id)

        # Clean up old shots.
        for starId in untouched:
            del self.collectableStarSprites[starId]

    def iterExtras(self):
        for sprite in list(self.extraSprites):
            if sprite.isDead():
                self.extraSprites.remove(sprite)
            yield sprite

    def getPlayerCount(self):
        return len(self.universe.players)

    def hasPlayer(self, player):
        return player.id in self.playerSprites

    def getPlayersInZone(self, zone):
        result = []
        for p in list(zone.players) + list(zone.nonPlayers):
            ps = self.getPlayerSprite(p.id)
            if ps is not None:
                result.append(ps)
        return result

    def addExplosion(self, pos):
        self.extraSprites.add(ExplosionSprite(self.app, pos))

    def addShoxwaveExplosion(self, pos):
        self.extraSprites.add(ShoxwaveExplosionSprite(self.app, pos))

    def tick(self, deltaT):
        for player in self.iterPlayers():
            player.update()
        for shot in self.iterShots():
            shot.update()
        for grenade in self.iterGrenades():
            grenade.update()
        for star in self.iterCollectableStars():
            star.update()
        for sprite in self.iterExtras():
            sprite.update()
