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

import base64
import logging

from trosnoth.utils.components import Component, Plug
from trosnoth.utils.utils import timeNow
from trosnoth.utils.event import Event
from trosnoth.network.client import clientMsgs
from trosnoth.utils.netmsg import MessageTypeError

log = logging.getLogger('replays')

# Remove the newline character at the end, since we never care
def getLine(file):
    line = file.readline()
    if (line.endswith('\n')):
        return line[:len(line)-1]
    return line


class ReplayRecorder(Component):
    inPlug = Plug()

    FLUSH_AFTER = 20
    def __init__(self, world, filename):
        Component.__init__(self)
        self.filename = filename
        self.world = world
        self.file = open(self.filename, 'w')
        self.numTilFlush = self.FLUSH_AFTER
        self.timeStarted = self.world.getElapsedTime()
        self.stopped = False

    def timeStamp(self):
        return self.world.getElapsedTime() - self.timeStarted

    @inPlug.defaultHandler
    def gotMessage(self, msg):
        if self.stopped:
            return
        datagram = base64.b64encode(msg.pack())
        string = '%#.3f %s\n' % (self.timeStamp(), datagram)
        self.file.write(string)
        self.numTilFlush -= 1
        if self.numTilFlush <= 0:
            self.numTilFlush = self.FLUSH_AFTER
            self.file.flush()

    def stop(self):
        if not self.stopped:
            self.file.flush()
            self.file.close()
            self.stopped = True

from twisted.internet import reactor

class ReplayPlayer(Component):
    '''
    Emulates a normal server by outputting the same messages that a server once
    did
    '''
    inPlug = Plug()
    outPlug = Plug()

    MESSAGES_TO_LOAD = 500
    MINIMUM_MESSAGES = 150
    def __init__(self, world, filename):
        Component.__init__(self)
        self.file = open(filename, 'r')
        self.messagesToReplay = []
        self.finished = False
        self.world = world
        self.onFinished = Event()


    def begin(self):
        self.loadMessages(self.MESSAGES_TO_LOAD)
        self.timeStarted = self.world.getElapsedTime()
        reactor.callLater(0, self.tick)


    def loadMessages(self, number):
        assert not self.finished
        for i in range(0, number):
            line = getLine(self.file)
            if line == '':
                self.finished = True
                break
            try:
                s_time, encoded = line.split(' ', 2)
                time = float(s_time)
                datagram = base64.b64decode(encoded)
                msg = clientMsgs.buildMessage(datagram)
            except MessageTypeError:
                log.warning('WARNING: UNKNOWN MESSAGE: %s' % (datagram,))
            except:
                log.warning('WARNING:  UNKNOWN LINE: %s' % (line,))
            else:
                self.messagesToReplay.append((time, msg))


    def tick(self):
        while len(self.messagesToReplay) > 0:
            time, msg = self.messagesToReplay[0]
            if time <= self.world.getElapsedTime():
                self.outPlug.send(msg)
                del self.messagesToReplay[0]
            else:
                break
        if (not self.finished and len(self.messagesToReplay) <
                self.MINIMUM_MESSAGES):
            self.loadMessages(self.MESSAGES_TO_LOAD -
                    len(self.messagesToReplay))

        if len(self.messagesToReplay) == 0 and self.finished:
            self.onFinished.execute()
        else:
            reactor.callLater(0, self.tick)

    def unpause(self):
        # Reset the reference time, adding the duration that we were paused
        self.timeStarted += (timeNow() - self.timePaused)

