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

'''viewManager.py - defines the ViewManager class which deals with drawing the
state of a universe to the screen.'''

from math import sin, cos
import logging

import pygame

from trosnoth.utils.utils import timeNow
from trosnoth.trosnothgui.ingame.minimap import MiniMap
from trosnoth.gui.framework import framework, elements
from trosnoth.trosnothgui.ingame.leaderboard import LeaderBoard
from trosnoth.trosnothgui.ingame.statusBar import ZoneProgressBar
from trosnoth.trosnothgui.ingame.gameTimer import GameTimer
from trosnoth.trosnothgui.ingame.universegui import UniverseGUI
from trosnoth.model.map import MapLayout
from trosnoth.model.universe_base import GameState
from trosnoth.model.utils import getZonesInRect, getBlocksInRect

from trosnoth.model.player import Player

from trosnoth.gui.common import Location, FullScreenAttachedPoint

ZONE_OFFSETS = {
    'top': (512, 0),
    'btm': (512, 384),
    'fwd': ((1536, 384), (0, 0)),
    'bck': ((1536, 0), (0, 384)),
}
ZONE_SIZE = (2048, 768)
BODY_BLOCK_SIZE = (1024, 384)
INTERFACE_BLOCK_SIZE = (512, 384)

BACKDROP_COLOUR_KEY = (255, 255, 255)

log = logging.getLogger('viewManager')

class ViewManager(framework.Element):
    '''A ViewManager object takes a given universe, and displays a screenfull
    of the current state of the universe on the specified screen object.  This
    class displays only a section of the universe and no other information
    (scores, menu etc.).

    Note: self._focus represents the position that the ViewManager is currently
    looking at.  self.target is what the ViewManager should be trying to look
    at.

    self.target = None - the ViewManager will use its algorithm to follow a
        point of action.
    self.target = (x, y) - the ViewManager will look at the specified point.
    self.target = player - the ViewManager will follow the specified player.
    '''

    # The fastest speed that the viewing position can shift in pixels per sec
    maxSpeed = 1800
    acceleration = 1080

    # How far ahead of the targeted player we should look.
    lengthFromPlayer = 125

    def __init__(self, app, universe, target=None, replay=False):
        '''Called upon creation of a ViewManager object.  screen is a pygame
        screen object.  universe is the Universe object to draw.  target is
        either a point, a Player object, or None.  If target is None, the view
        manager will follow the action, otherwise it will follow the specified
        point or player.'''
        super(ViewManager, self).__init__(app)
        self.universe = universe
        self.replay = replay

        # self._focus represents the point where the viewManager is currently
        # looking.
        self._focus = (universe.map.layout.centreX, universe.map.layout.centreY)
        self._oldTargetPt = self._focus
        self.lastUpdateTime = timeNow()
        self.speed = 0          # Speed that the focus is moving.

        self.backgroundDrawer = BackgroundDrawer(app, universe)
        self.sRect = None

        # Now fill the backdrop with what we're looking at now.
        self.appResized()
        self.setTarget(target)

    def appResized(self):
        self.sRect = sRect = pygame.Rect((0,0), self.app.screenManager.size)
        centre = sRect.center
        if not self.replay:
            sRect.width = min(1024, sRect.width)
            sRect.height = min(768, sRect.height)
        sRect.center = centre

    def setTarget(self, target):
        '''Makes the viewManager's target the specified value.'''
        self.target = target
        if isinstance(self.target, Player):
            # Move directly to looking at player.
            self._focus = target.pos
        elif isinstance(self.target, (tuple, list)):
            pass
        else:
            self.autoFocusInfo = [0, set()]
            self._oldTargetPt = self._focus

    def getTargetPoint(self):
        '''Returns the position of the current target.'''
        if self.target is None:
            return self._focus
        if isinstance(self.target, Player):
            return self.target.pos
        return self.target

    def draw(self, screen):
        '''Draws the current state of the universe at the current viewing
        location on the screen.  Does not call pygame.display.flip()'''

        # Update where we're looking at.
        self.updateFocus()

        if self.sRect.topleft != (0, 0):
            screen.fill((0, 0, 0))

        oldClip = screen.get_clip()

        screen.set_clip(self.sRect)
        self.backgroundDrawer.draw(screen, self.sRect, self._focus)
        self._drawSprites(screen)
        screen.set_clip(oldClip)

    def _drawSprites(self, screen):
        focus = self._focus
        area = self.sRect

        # Go through and update the positions of the players on the screen.
        ntGroup = pygame.sprite.Group()
        visPlayers = pygame.sprite.Group()
        for player in self.universe.iterPlayers():
            if not player.invisible or player.isFriendsWith(self.target):
                # Calculate the position of the player.
                player.rect.center = [player.pos[i] - focus[i] + area.center[i]
                        for i in (0, 1)]

                # Check if this player needs its nametag shown.
                if player.rect.colliderect(area):
                    visPlayers.add(player)
                    player.nametag.rect.midtop = player.rect.midbottom
                    # Check that entire nametag's on screen.
                    if player.nametag.rect.left < area.left:
                        player.nametag.rect.left = area.left
                    elif player.nametag.rect.right > area.right:
                        player.nametag.rect.right = area.right
                    if player.nametag.rect.top < area.top:
                        player.nametag.rect.top = area.top
                    elif player.nametag.rect.bottom > area.bottom:
                        player.nametag.rect.bottom = area.bottom
                    ntGroup.add(player.nametag)

                    # Place the star rectangle below the nametag.
                    mx, my = player.nametag.rect.midbottom
                    player.starTally.setStars(player.stars)
                    player.starTally.rect.midtop = (mx, my-5)
                    ntGroup.add(player.starTally)

        # Draw the on-screen players and nametags.
        visPlayers.draw(screen)
        ntGroup.draw(screen)
        ntGroup.empty()

        def drawSprite(sprite):
            # Calculate the position of the sprite.
            sprite.rect.center = [sprite.pos[i] - focus[i] + area.center[i] for
                    i in (0, 1)]
            if sprite.rect.colliderect(area):
                screen.blit(sprite.image, sprite.rect)

        # Draw the shots.
        for shot in self.universe.iterShots():
            drawSprite(shot)
        for star in self.universe.iterCollectableStars():
            drawSprite(star)

        try:
            # Draw the grenades.
            for grenade in self.universe.iterGrenades():
                drawSprite(grenade)
        except Exception, e:
            log.exception(str(e))

        for sprite in self.universe.iterExtras():
            drawSprite(sprite)

    def updateFocus(self):
        '''Updates the location that the ViewManager is focused on.  First
        calculates where it would ideally be focused, then moves the focus
        towards that point. The focus cannot move faster than self.maxSpeed
        pix/s, and will only accelerate or decelerate at self.acceleration
        pix/s/s. This method returns the negative of the amount scrolled by.
        This is useful for moving the backdrop by the right amount.
        '''

        # Calculate where we should be looking at.
        if isinstance(self.target, Player):
            # Take into account where the player's looking.
            plPos = self.target.pos

            if self.app.displaySettings.centreOnPlayer:
                targetPt = plPos
            else:
                radius = self.target.ghostThrust * self.lengthFromPlayer
                #distanceToTarget
                #if radius == None or radius > self.lengthFromPlayer:
                #    radius = self.lengthFromPlayer

                plAngle = self.target.angleFacing
                targetPt = (plPos[0] + radius * sin(plAngle),
                            plPos[1] - radius * cos(plAngle))

            # If the player no longer exists, look wherever we want.
            if not self.universe.hasPlayer(self.target):
                self.setTarget(None)
        elif isinstance(self.target, (tuple, list)):
            targetPt = self.target
        else:
            # Follow the action.
            countdown, players = self.autoFocusInfo

            if self.universe.getPlayerCount() == 0:
                # No players anywhere. No change.
                targetPt = tuple(self._focus)
                players = []
            else:
                # First check for non-existent players.
                for p in players:
                    if not self.universe.hasPlayer(p):
                        players.remove(p)

                # Every 10 iterations recheck for players that have entered view
                # area.
                r = pygame.Rect(self.sRect)
                r.center = self._oldTargetPt
                if countdown <= 0:
                    players = set()
                    for p in self.universe.iterPlayers():
                        if r.collidepoint(p.pos):
                            players.add(p)
                    countdown = 10
                else:
                    # Keep track of which players are still visible.
                    for p in list(players):
                        if not r.collidepoint(p.pos):
                            players.remove(p)
                    countdown -= 1

                if len(players) == 0:
                    # No players in view. Look for action.
                    maxP = 0
                    curZone = None
                    for z in self.universe.zones:
                        count = len(self.universe.getPlayersInZone(z))
                        if count > maxP:
                            maxP = count
                            curZone = z
                    if curZone is None:
                        players = []
                    else:
                        players = self.universe.getPlayersInZone(curZone)

                    targetPt = tuple(self._focus)
                    countdown = 20

                # Look at centre-of-range of these players.
                if len(players) > 0:
                    minPos = [min(p.pos[i] for p in players) for i in (0, 1)]
                    maxPos = [max(p.pos[i] for p in players) for i in (0, 1)]
                    targetPt = [0.5 * (minPos[i] + maxPos[i]) for i in (0, 1)]
            self.autoFocusInfo = (countdown, players)

        # Calculate time that's passed.
        now = timeNow()
        deltaT = now - self.lastUpdateTime
        self.lastUpdateTime = now

        # Calculate distance to target.
        self._oldTargetPt = targetPt
        sTarget = sum((targetPt[i] - self._focus[i])**2 for i in (0, 1)) ** 0.5

        if sTarget == 0:
            return (0, 0)

        # If smooth panning is switched off, jump to location.
        if (self.target is not None and not
                self.app.displaySettings.smoothPanning):
            s = sTarget
        else:
            # Calculate the maximum velocity that will result in deceleration to
            # reach target. This is based on v**2 = u**2 + 2as
            vDecel = (2. * self.acceleration * sTarget) ** 0.5

            # Actual velocity is limited by this and maximum velocity.
            self.speed = min(self.maxSpeed, vDecel, self.speed +
                    self.acceleration * deltaT)

            # Distance travelled should never overshoot the target.
            s = min(sTarget, self.speed * deltaT)

        # How far does the backdrop need to move by?
        #  (This will be negative what the focus moves by.)
        deltaBackdrop = tuple(round(-s * (targetPt[i] - self._focus[i]) /
                sTarget, 0) for i in (0, 1))

        # Calculate the new focus.
        self._focus = tuple(round(self._focus[i] - deltaBackdrop[i], 0) for i
                in (0, 1))

    def getZoneAtPoint(self, pt):
        x, y = screenToMapPos(pt, self._focus, self.sRect)

        i, j = MapLayout.getMapBlockIndices(x, y)
        try:
            return self.universe.map.zoneBlocks[i][j].getZoneAtPoint(x, y)
        except IndexError:
            return None

class BackgroundDrawer(object):
    def __init__(self, app, universe):
        self.app = app
        self.scenery = Scenery(app, universe)
        self.aBackgrounds = AlphaBackgrounds(app, universe)
        self.sBackgrounds = SolidBackgrounds(app, universe)
        self.orbs = OrbDrawer(app, universe)
        self.debugs = DebugDrawer(app, universe)

    def draw(self, screen, sRect, focus):
        self.scenery.draw(screen, sRect, focus)
        if self.app.displaySettings.windowsTranslucent:
            self.aBackgrounds.draw(screen, sRect, focus)
        self.sBackgrounds.draw(screen, sRect, focus)
        self.orbs.draw(screen, sRect, focus)
        self.debugs.draw(screen, sRect, focus)

class Scenery(object):
    def __init__(self, app, universe, distance=3):
        self.universe = universe
        self.image = app.theme.sprites.scenery
        self.scale = 1. / distance

    def draw(self, screen, area, focus):
        worldRect = viewRectToMap(focus, area)

        regions = []
        for block in getBlocksInRect(self.universe, worldRect):
            bd = block.defn
            pos = mapPosToScreen(bd.pos, focus, area)
            if bd.kind in ('top', 'btm'):
                if bd.zone is None:
                    regions.append(pygame.Rect(pos, BODY_BLOCK_SIZE))
                    continue
            elif bd.zone1 is None or bd.zone2 is None:
                regions.append(pygame.Rect(pos, INTERFACE_BLOCK_SIZE))
                continue

            r = WINDOW_RECT[bd.kind]
            regions.append(pygame.Rect(r[0] + pos[0], r[1] + pos[1], r[2],
                    r[3]))

        x0, y0 = mapPosToScreen((0, 0), focus, area)
        if area.top < y0:
            r = pygame.Rect(area)
            r.bottom = y0
            regions.append(r)
        if area.left < x0:
            r = pygame.Rect(area)
            r.right = x0
            regions.append(r)
        x1, y1 = mapPosToScreen(self.universe.map.layout.worldSize, focus, area)
        if area.bottom > y1:
            r = pygame.Rect(area)
            r.top = y1
            regions.append(r)
        if area.right > x1:
            r = pygame.Rect(area)
            r.left = x1
            regions.append(r)

        clip = screen.get_clip()
        for region in regions:
            region = region.clip(clip)
            screen.set_clip(region)
            self.drawRegion(screen, region, worldRect.topleft)
        screen.set_clip(clip)

    def drawRegion(self, screen, area, focus):
        w, h = self.image.get_size()
        x = area.left - ((focus[0] * self.scale + area.left) % w)
        y0 = y = area.top - ((focus[1] * self.scale + area.top) % h)

        while x < area.right:
            while y < area.bottom:
                screen.blit(self.image, (x, y))
                y += h
            x += w
            y = y0

class OrbDrawer(object):
    def __init__(self, app, world):
        self.app = app
        self.universe = world

    def draw(self, screen, area, focus):
        worldRect = viewRectToMap(focus, area)

        for zone in getZonesInRect(self.universe, worldRect):
            pic = self.app.theme.sprites.orb(zone.orbOwner)
            r = pic.get_rect()
            r.center = mapPosToScreen(zone.defn.pos, focus, area)
            screen.blit(pic, r)

class DebugDrawer(object):
    def __init__(self, app, world):
        self.app = app
        self.universe = world

    def draw(self, screen, area, focus):
        if not self.app.displaySettings.showObstacles:
            return

        from trosnoth.model.obstacles import Obstacle, Corner

        worldRect = viewRectToMap(focus, area)
        for block in getBlocksInRect(self.universe, worldRect):
            for obs in block.defn.obstacles:
                if isinstance(obs, Obstacle):
                    pt1 = mapPosToScreen(obs.pt1, focus, area)
                    pt2 = mapPosToScreen(obs.pt2, focus, area)
                    pygame.draw.line(screen, (255, 0, 0), pt1, pt2, 2)
                elif isinstance(obs, Corner):
                    pt1 = mapPosToScreen( [obs.pt[i] - obs.offset[i] * 10 for i
                            in (0, 1)], focus, area)
                    pt2 = mapPosToScreen( [obs.pt[i] - (obs.offset[i] +
                            obs.delta[i]) * 10 for i in (0, 1)], focus, area)
                    pygame.draw.line(screen, (255, 255, 0), pt1, pt2, 2)
                    pt2 = (int(pt2[0]), int(pt2[1]))
                    pygame.draw.circle(screen, (255, 255, 0), pt2, 3, 0)

class SolidBackgrounds(object):
    def __init__(self, app, world):
        self.app = app
        self.universe = world
        self.bkgCache = BackgroundCache(app)

    def draw(self, screen, area, focus):
        worldRect = viewRectToMap(focus, area)

        for block in getBlocksInRect(self.universe, worldRect):
            pic = self.bkgCache.get(block)
            if pic is not None:
                screen.blit(pic, mapPosToScreen(block.defn.pos, focus, area))

class BackgroundCache(object):
    def __init__(self, app, capacity=15):
        self.app = app
        self.capacity = capacity
        self.cache = {}
        self.order = []

    def get(self, block):
        pic1 = self.app.theme.sprites.blockBackground(block)
        if block.defn.graphics is not None:
            pic2 = block.defn.graphics.graphic
        else:
            pic2 = None

        if (pic1, pic2) in self.cache:
            self.order.remove((pic1, pic2))
            self.order.insert(0, (pic1, pic2))
            return self.cache[pic1, pic2]

        pic = self._makePic(pic1, pic2)
        self.cache[pic1, pic2] = pic
        self.order.insert(0, (pic1, pic2))
        if len(self.order) > self.capacity:
            del self.cache[self.order.pop(-1)]
        return pic

    def _makePic(self, pic1, pic2):
        if pic1 is None:
            return pic2
        if pic2 is None:
            return pic1
        pic = pic1.copy()
        pic.blit(pic2, (0, 0))
        return pic

WINDOW_RECT = {
    'top': (185, 57, 654, 327),
    'btm': (185, 0, 654, 327),
    'fwd': (93, 29, 326, 326),
    'bck': (93, 29, 326, 326),
}

class AlphaBackgrounds(object):
    def __init__(self, app, world):
        self.app = app
        self.universe = world

    def draw(self, screen, area, focus):
        worldRect = viewRectToMap(focus, area)

        for block in getBlocksInRect(self.universe, worldRect):
            pic = self.app.theme.sprites.blockAlphaBackground(block)
            if pic is not None:
                pic.set_alpha(96)
                blitPart(screen, pic, mapPosToScreen(block.defn.pos, focus,
                        area), pygame.Rect(WINDOW_RECT[block.defn.kind]))

def blitPart(surface, source, dest, part):
    '''
    Performs a blit, positioning the source on the surface as for
    surface.blit(source, dest), but only blits the subrect part. part is a rect
    relative to the top-left corner of the source image.
    '''
    surface.blit(source, (dest[0] + part.left, dest[1] + part.top), part)

def viewRectToMap(focus, area):
    return pygame.Rect(
        (focus[0] - area.centerx + area.left,
        focus[1] - area.centery + area.top), area.size)

def zonePosToScreen(pt, focus, area):
    return mapPosToScreen((pt[0] - 1024, pt[1] - 384), focus, area)

def mapPosToScreen(pt, focus, area):
    return (pt[0] - focus[0] + area.centerx,
            pt[1] - focus[1] + area.centery)

def screenToMapPos(pt, focus, area):
    return (pt[0] + focus[0] - area.centerx,
            pt[1] + focus[1] - area.centery)

class PregameMessage(elements.TextElement):
    def __init__(self, app, pos=None):
        if pos is None:
            pos = Location(FullScreenAttachedPoint((0, -150), 'center'),
                    'center')
        super(PregameMessage, self).__init__(
            app,
            '',
            app.screenManager.fonts.bigMenuFont,
            pos,
            app.theme.colours.pregameMessageColour,
            shadow = True
        )
        self.setShadowColour((0,0,0))

class GameViewer(framework.CompoundElement):
    '''The gameviewer comprises a viewmanager and a minimap, which can be
    switched on or off.'''

    zoneBarHeight = 25

    def __init__(self, app, gameInterface, game, replay):
        super(GameViewer, self).__init__(app)
        self.replay = replay
        self.interface = gameInterface
        self.game = game
        self.gameController = game.gameController
        self.world = game.world
        self.worldgui = UniverseGUI(app, self, self.world)
        self.app = app

        self.viewManager = ViewManager(self.app, self.worldgui, replay=replay)

        self.timerBar = GameTimer(app, game)
        
        self.miniMap = None
        self.pregameMessage = None
        self.leaderboard = None
        self.zoneBar = None
        self.makeMiniMap()

        self.elements = [self.viewManager, self.pregameMessage]
        self._screenSize = tuple(app.screenManager.size)

        self.teamsDisrupted = set()

        self.toggleInterface()
        self.toggleLeaderBoard()

    def getZoneAtPoint(self, pos):
        '''
        Returns the zone at the given screen position. This may be on the
        minimap or the main view.
        '''
        zone = self.miniMap.getZoneAtPoint(pos)
        if zone is None:
            zone = self.viewManager.getZoneAtPoint(pos)
        return zone

    def resizeIfNeeded(self):
        '''
        Checks whether the application has resized and adjusts accordingly.
        '''
        if self._screenSize == self.app.screenManager.size:
            return
        self._screenSize = tuple(self.app.screenManager.size)

        self.viewManager.appResized()
        # Recreate the minimap.
        showHUD = self.miniMap in self.elements
        showLeader = self.leaderboard in self.elements
        self.makeMiniMap()
        if showHUD:
            self.toggleInterface()
        if showLeader:
            self.toggleLeaderBoard()


    def makeMiniMap(self):
        self.miniMap = MiniMap(self.app, 20, self.world, self.viewManager)
        xPos = -10
        yPos = self.miniMap.getRect().bottom + self.zoneBarHeight - 5
        messagePos = Location(FullScreenAttachedPoint((xPos, yPos),
                'topright'), 'topright')
        self.pregameMessage = PregameMessage(self.app, messagePos)
        self.zoneBar = ZoneProgressBar(self.app, self.world, self)
        self.leaderboard = LeaderBoard(self.app, self.game, self)

        self.elements = [self.viewManager, self.pregameMessage]

    def updatePregameMessage(self):
        text = ''
        if self.gameController.state() == GameState.InProgress:
            text = ''
        elif self.gameController.state() == GameState.PreGame:
            text = 'Indicate "Ready" to begin'
        elif self.gameController.state() == GameState.Starting:
            text = 'Prepare yourself...'
        else:
            pi = self.interface.runningPlayerInterface
            if pi is not None and pi.player is not None:
                team = pi.player.team
                if team is None:
                    text = 'Waiting for more ready players.'
                elif team is self.world.getWinningTeam():
                    text = 'Congratulations!'
                else:
                    text = 'Better luck next time!'
            else:
                text = 'Game is over!'
        self.pregameMessage.setText(text)

    def setTarget(self, target):
        'Target should be a player, a point, or None.'
        self.viewManager.setTarget(target)

    def tick(self, deltaT):
        self.resizeIfNeeded()
        self.worldgui.tick(deltaT)
        self.updatePregameMessage()

        target = self.viewManager.target
        if isinstance(target, Player) and target.isMinimapDisrupted:
            self.miniMap.disrupted()
            self.zoneBar.disrupt = True
        else:
            self.miniMap.endDisruption()
            self.zoneBar.disrupt = False

        super(GameViewer, self).tick(deltaT)

    def toggleInterface(self):
        if self.miniMap in self.elements:
            self.elements.remove(self.zoneBar)
            self.elements.remove(self.timerBar)
            self.elements.remove(self.miniMap)
        else:
            self.elements.append(self.zoneBar)
            self.elements.append(self.timerBar)
            self.elements.append(self.miniMap)
            self.timerBar.syncTimer()

    def toggleLeaderBoard(self):
        if self.leaderboard in self.elements:
            self.elements.remove(self.leaderboard)
        else:
            self.elements.append(self.leaderboard)