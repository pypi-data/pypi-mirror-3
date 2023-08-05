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

from trosnoth.gui.keyboard import VirtualKeySet

# Define virtual keys and their default bindings.
default_game_keys = VirtualKeySet((
    # Movement keys.
    ('left', pygame.K_a),
    ('down', pygame.K_s),
    ('right', pygame.K_d),
    ('jump', pygame.K_w),

    # Used in replay mode.
    ('follow', pygame.K_EQUALS),

    # Menu keys.
    ('menu', pygame.K_ESCAPE),

    ('mark zone', pygame.K_F1),

    ('select upgrade', pygame.K_b),
    ('activate upgrade', pygame.K_SPACE),
    ('change nickname', pygame.K_F12),
    ('more actions', pygame.K_v),
    ('respawn', pygame.K_r),

    ('no upgrade', pygame.K_0),

    ('abandon', pygame.K_m),
    ('chat', pygame.K_RETURN),
    ('leaderboard', pygame.K_p),
    ('toggle interface', pygame.K_DELETE),

    ('toggle terminal', pygame.K_SCROLLOCK),
))

from trosnoth.model.upgrades import allUpgrades

for upgradeClass in allUpgrades:
    if upgradeClass.defaultKey is not None:
        default_game_keys[upgradeClass.action] = upgradeClass.defaultKey
del upgradeClass
