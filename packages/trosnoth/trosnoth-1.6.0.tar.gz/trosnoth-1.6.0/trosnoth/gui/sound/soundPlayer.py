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
import trosnoth.data.sound as sound
from trosnoth.data import getPath

class SoundAction(object):
    def __init__(self, filename, startChannelIndex, numChannels):
        assert numChannels > 0
        if not pygame.mixer.get_init():
            self.channels = []
            return

        self.sound = pygame.mixer.Sound(getPath(sound, filename))
        endChannelIndex = startChannelIndex+numChannels
        self.currentIndex = 0
        self.channels = [pygame.mixer.Channel(i) for i in
                range(startChannelIndex, endChannelIndex)]
        self.channelVolume = 1

    def play(self, volume=1):
        if not pygame.mixer.get_init():
            return

        finalVol = volume * self.channelVolume
        if finalVol < 0.01:
            return
        # Put the first channel to the back
        channel = self.channels[self.currentIndex]
        self.currentIndex += 1
        self.currentIndex %= len(self.channels)
        channel.set_volume(finalVol)
        channel.play(self.sound)

    def setVolume(self, val):
        self.sound.set_volume(val)

    def setChannelsVolume(self, val):
        self.channelVolume = val
        for channel in self.channels:
            channel.set_volume(val)

class SoundPlayer(object):
    def __init__(self):
        self.sounds = {}
        self.masterVolume = 1
        self._channelsUsed = 0

    def addSound(self, filename, action, maxSimultaneous = 8):
        if not pygame.mixer.get_init():
            return

        self.sounds[action] = SoundAction(filename, self._channelsUsed,
                maxSimultaneous)
        # In case a sound is added after the volume has been set:
        self.sounds[action].setChannelsVolume(self.masterVolume)

        self._channelsUsed += maxSimultaneous
        if self._channelsUsed > pygame.mixer.get_num_channels():
            pygame.mixer.set_num_channels(self._channelsUsed)

    def play(self, action, volume = 1):
        if not pygame.mixer.get_init():
            return

        self.sounds[action].play(volume)

    def setSoundVolume(self, action, val):
        self.sounds[action].setVolume(val)

    def setMasterVolume(self, val):
        self.masterVolume = val
        for action in self.sounds.values():
            action.setChannelsVolume(val)
