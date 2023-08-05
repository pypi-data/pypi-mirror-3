from random import randrange

from twisted.internet import task, reactor

from trosnoth.network.netman import *
from trosnoth.utils import netmsg

# NOTE: To test how this works in the case where UDP fails, try editing
# netman.py and setting _doUdpSend() to do nothing.


class SomeMessage(netmsg.NetworkMessage):
    fields = 'data'
    packspec = 'I'
    idString = 'test'
    
class SomeReply(netmsg.NetworkMessage):
    fields = 'data'
    packspec = 'I'
    idString = 'yep.'
    

class Handler1(object):
    greeting = 'test_handler'
    messages = netmsg.MessageCollection(SomeMessage)

    def __init__(self, netman):
        self.netman = netman
        netman.addHandler(self)

    def newConnection(self, connectionId, ipAddr, port):
        print 'H1: new connection %d' % (connectionId,)
        print 'H1: peer on %s' % (self.netman.getAddress(connectionId),)

    def receiveMessage(self, connectionId, message):
        print 'H1: receive from %d %s' % (connectionId, message)
        opt = randrange(3)
        if opt == 0:
            print 'H1: sending reply via TCP'
            self.netman.sendTCP(connectionId, SomeReply(message.data))
        elif opt == 1:
            print 'H1: sending reply via UDP'
            self.netman.sendUDP(connectionId, SomeReply(message.data))
        else:
            print 'H1: Sending reply via fastest available means'
            self.netman.send(connectionId, SomeReply(message.data))
    def receiveBadString(self, connectionId, line):
        print 'H1: Unknown network message: %r' % (line,)
    def connectionLost(self, connectionId):
        print 'H1: lost connection %d' % (connectionId,)
    def connectionFailed(self, connectionId):
        print 'H1: connection %d failed' % (connectionId,)

class Handler2(object):
    greeting = 'test_handler'
    messages = netmsg.MessageCollection(SomeReply)

    def __init__(self, netman, name):
        self.name = name
        self.netman = netman
        self.netman.connect(self, 'localhost', 5678)
        task.LoopingCall(self.tick).start(3, False)
        self.connId = None

    def tick(self):
        if self.connId is None:
            return
        msg = SomeMessage(randrange(3000))
        opt = randrange(3)
        if opt == 0:
            print '%s: Sending %s via TCP' % (self.name, msg)
            self.netman.sendTCP(self.connId, msg)
        elif opt == 1:
            print '%s: Sending %s via UDP' % (self.name, msg)
            self.netman.sendUDP(self.connId, msg)
        else:
            print '%s: Sending %s via fastest available means' % (self.name, msg)
            self.netman.send(self.connId, msg)

    def connectionComplete(self, connectionId):
        print '%s: connection complete %d' % (self.name, connectionId,)
        print '%s: peer on %s' % (self.name, self.netman.getAddress(connectionId))
        self.connId = connectionId
    def receiveMessage(self, connectionId, message):
        print '%s: receive from %d %s' % (self.name, connectionId, message)
    def receiveBadString(self, connectionId, line):
        print '%s: Unknown network message: %r' % (self.name, line)
    def connectionLost(self, connectionId):
        print '%s: lost connection %d' % (self.name, connectionId)
    def connectionFailed(self, connectionId):
        print '%s: connection %d failed' % (self.name, connectionId)
        print '%s: trying again' % (self.name,)
        self.netman.connect(self, 'localhost', 5678)

# Construct net men.
nm1 = NetworkManager(5678, 5678)
nm2 = NetworkManager(5679, 5679)

# Construct handlers.
h1 = Handler1(nm1)
h2 = Handler2(nm2, 'H2')
h3 = Handler2(nm2, 'H3')

reactor.run()
