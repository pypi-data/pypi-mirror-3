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

class NameTag(pygame.sprite.Sprite):
    '''Sprite object that every player has which indicates the player's nick.'''
    def __init__(self, app, nick):
        pygame.sprite.Sprite.__init__(self)
        self.app = app

        if len(nick) > 15:
            nick = nick[:13] + '...'
        self.nick = nick
        colours = app.theme.colours
        nameFont = app.fonts.nameFont
        self.image = nameFont.render(app, self.nick, True,
                colours.nameTagShadow)
        foreground = nameFont.render(app, self.nick, True,
                colours.nameTagColour)
        self.image.blit(foreground, (-2, -2))

        self.image.set_colorkey((0,0,0))
        self.rect = self.image.get_rect()

class StarTally(pygame.sprite.Sprite):
    def __init__(self, app, stars):
        pygame.sprite.Sprite.__init__(self)
        self.app = app
        self.image = None
        self.rect = None

        self.setStars(stars)

    def setStars(self, stars):
        pic = self.app.theme.sprites.smallStar
        stars = max(stars, 0)

        if stars <= 5:
            self.image = pygame.Surface((12*stars+2, 13))
            # Blit the stars.
            for i in xrange(stars):
                self.image.blit(pic, (i*12, 0))

            self.rect = self.image.get_rect()
        else:
            self.image = pygame.Surface((62, 26))
            # Blit the stars.
            for i in xrange(5):
                self.image.blit(pic, (i*12-1, 0))
            for i in xrange(stars-5):
                self.image.blit(pic, (i*12-1, 13))

            self.rect = self.image.get_rect()
        self.image.set_colorkey((0, 0, 0))

