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

import pygame
from trosnoth.gui.framework import framework
from trosnoth.utils.checkpoint import checkpoint
from trosnoth.messages import (UpdatePlayerStateMsg, AimPlayerAtMsg,
        ShootMsg)
from math import atan2

class PlayerInterface(framework.Element):
    '''Interface for controlling a player.'''

    # The virtual keys we care about.
    state_vkeys = frozenset(['left', 'right', 'jump', 'down'])

    def __init__(self, app, gameInterface, playerId):
        super(PlayerInterface, self).__init__(app)

        world = gameInterface.world
        self.gameInterface = gameInterface
        self.keyMapping = gameInterface.keyMapping

        self.receiving = True

        self.world = world
        self.worldGui = gameInterface.gameViewer.worldgui
        self.playerId = playerId

        self.mousePos = (0, 0)
        pygame.mouse.get_rel()

        # Make sure the viewer is focusing on this player.
        self.gameInterface.gameViewer.setTarget(self.player)

    @property
    def player(self):
        return self.world.playerWithId[self.playerId]

    @property
    def playerSprite(self):
        return self.worldGui.getPlayerSprite(self.playerId)

    def tick(self, deltaT):
        pos = pygame.mouse.get_pos()
        spritePos = self.playerSprite.rect.center
        self.mousePos = (pos[0] - spritePos[0], pos[1] - spritePos[1])
        self.updatePlayerViewAngle()
        if self.player.canShoot():
        	if self.player.mgFiring:
        	    if self.player.machineGunner:
        	    	self._fireShot()


    def updatePlayerViewAngle(self):
        '''Updates the viewing angle of the player based on the mouse pointer
        being at the position pos. This gets its own method because it needs
        to happen as the result of a mouse motion and of the viewManager
        scrolling the screen.'''
        dx, dy = self.mousePos
        pos = (self.playerSprite.rect.center[0] + dx,
               self.playerSprite.rect.center[1] + dy)

        if self.playerSprite.rect.collidepoint(pos):
            return

        # Angle is measured clockwise from vertical.
        theta = atan2(dx, -dy)
        dist = (dx ** 2 + dy ** 2) ** 0.5

        # Calculate a thrust value based on distance.
        if dist < 25:
            thrust = 0.0
        elif dist > 125:
            thrust = 1.0
        else:
            thrust = (dist - 25) / 100.

        self.gameInterface.controller.send(AimPlayerAtMsg(self.player.id,
                theta, thrust))

    def processEvent(self, event):
        '''Event processing works in the following way:
        1. If there is a prompt on screen, the prompt will either use the
        event, or pass it on.
        2. If passed on, the event will be sent back to the main class, for it
        to process whether player movement uses this event. If it doesn't use
        the event, it will pass it back.
        3. If so, the hotkey manager will see if the event means anything to it.
        If not, that's the end, the event is ignored.'''

        # Handle events specific to in-game.
        if self.player:
            if event.type == pygame.KEYDOWN:
                try:
                    stateKey = self.keyMapping[event.key]
                except KeyError:
                    return event

                if stateKey not in self.state_vkeys:
                    return event

                self.gameInterface.controller.send(UpdatePlayerStateMsg(
                        self.player.id, True, stateKey))
            elif event.type == pygame.KEYUP:
                try:
                    stateKey = self.keyMapping[event.key]
                except KeyError:
                    return event

                if stateKey not in self.state_vkeys:
                    return event

                self.gameInterface.controller.send(UpdatePlayerStateMsg(
                        self.player.id, False, stateKey))
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.player.ghost:
                        self.gameInterface.detailsInterface.doAction('respawn')
                    elif self.player.machineGunner:
                    	self.player.mgFiring = True

                    else:
                        # Fire a shot.
                        self._fireShot()
            elif event.type == pygame.MOUSEBUTTONUP:
            	if self.player.machineGunner:
            		self.player.mgFiring = False

            else:
                return event

    def _fireShot(self):
        '''Fires a shot in the direction the player's currently looking.'''
        player = self.player

        self.gameInterface.controller.send(ShootMsg(player.id))

        checkpoint('Player: fire shot')

