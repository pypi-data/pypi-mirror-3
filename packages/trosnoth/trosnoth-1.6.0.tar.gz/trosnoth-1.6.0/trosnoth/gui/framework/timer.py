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

from trosnoth.gui.framework import framework
from trosnoth.utils.event import Event

import datetime

class ITimer(framework.Element):
    def __init__(self):
        self.running = False

    def start(self):
        self.running = True
        return self

    def pause(self):
        self.running = False
        return self

    def tick(self, deltaT):
        raise NotImplementedError, "This is an abstract class"

    def getTimeString(self):
        raise NotImplementedError, "This is an abstract class"

class CountdownTimer(ITimer):
    '''@param amount    Amount of time to count down'''
    def __init__(self, countTo=0, highest = "days"):
        super(CountdownTimer,self).__init__()
        self.countTo = countTo
        self.counted = 0
        self.onCountedDown = Event()
        self.highest = highest

    def tick(self, deltaT):
        if self.running:
            self.counted += deltaT

            if self.counted > self.countTo:
                self.counted = self.countTo
                self.onCountedDown.execute()

    def getCurTime(self):
        return max(0, self.countTo - self.counted)

    def getTimeString(self):
        total = int(self.getCurTime())
        deltaResult = datetime.timedelta(seconds=total)
        seconds = deltaResult.days * 24 * 60 * 60 + deltaResult.seconds
        if self.highest == "seconds":
            return str(seconds)
        elif self.highest == "minutes":
            minutes, seconds = divmod(seconds, 60)
            return "%02d:%02d" % (minutes, seconds)
        elif self.highest == "hours":
            hours, minutes = divmod(minutes, 60)
            return "%d:%02d:%02d" % (hours, minutes, seconds)
        else:
            return str(deltaResult)


class Timer(ITimer):
    '''@param tick  Frequency with which onTick events are triggered.'''
    def __init__(self, tickDuration = 1, startAt = None, highest = "days"):
        super(Timer,self).__init__()
        if startAt is None:
            self.counted = 0
        else:
            self.counted = startAt
        self.tickDuration = tickDuration
        self.highest = highest

        self.onTick = Event()

    def tick(self, deltaT):
        if self.running:
            numTicked = self.counted / self.tickDuration
            self.counted += deltaT
            if (self.counted  / self.tickDuration) > numTicked:
                self.onTick.execute()

    def getTimeString(self):
        deltaResult = datetime.timedelta(seconds=int(max(0, self.counted)))
        seconds = deltaResult.days * 24 * 60 * 60 + deltaResult.seconds
        if self.highest == "seconds":
            return str(seconds)
        elif self.highest == "minutes":
            minutes, seconds = divmod(seconds, 60)
            return "%02d:%02d" % (minutes, seconds)
        elif self.highest == "hours":
            hours, minutes = divmod(minutes, 60)
            return "%d:%02d:%02d" % (hours, minutes, seconds)
        else:
            return str(deltaResult)

