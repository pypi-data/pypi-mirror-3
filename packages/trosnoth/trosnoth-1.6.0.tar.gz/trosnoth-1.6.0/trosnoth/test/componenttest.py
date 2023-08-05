# Trosnoth (UberTweak Platform Game)
# Copyright (C) 2006-2007  Joshua Bartlett
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

from trosnoth.utils.components import Component, Plug

class MessageSender(Component):
    sendPlug = Plug()

    
    def sendMessage(self, msg):
        sendPlug.send(msg)

class MessageReceiver(Component):
    receivePlug = Plug()

    def __init__(self):
        self.messageList = []

    @receivePlug.defaultHandler
    def _receiveMessage(self, msg):
        self.messageList.append(msg)

    
    def nextMessageShouldBe(self, msgType, **kwargs):
        msg = messageList.pop()
        assert type(msg) == msgType
        for key, val in kwargs:
            assert getattr(msg, key) == val

# sender = MessageSender()
# idManager.plug.connect(sender.sendPlug)
# idManager.outPlug.connect(messageReceiver.receivePlug)

# sender.sendMessage(ReqPlayerMsg(...))
# messageReceiver.nextMessageShouldBe(AddPlayer, nick='ErbaneOrb', teamId='A')
