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

import logging
import struct
import time

from twisted.internet import reactor
from twisted.internet.protocol import Factory, DatagramProtocol
from twisted.internet.error import CannotListenError
from twisted.protocols.basic import Int32StringReceiver

from trosnoth.utils import netmsg
from trosnoth.utils.twist import WeakCallLater

log = logging.getLogger('netman')

# Special network messages used by the Network Manager have id strings which
# begin with '\x07' in order to make it unlikely that their id strings will
# clash with those of normal network messages, which generally have readable
# id strings

class NotifyUDPInfo(netmsg.NetworkMessage):
    fields = 'udpPort', 'remoteId'
    packspec = 'II'
    idString = '\x07RId'

class UDPPing(netmsg.NetworkMessage):
    fields = 'payload'
    packspec = 'I'
    idString = '\x07boo'

class UDPReceived(netmsg.NetworkMessage):
    fields = 'payload'
    packspec = 'I'
    idString = '\x07AHH'

# Create a message collection for decoding these messages.
netmanMsgs = netmsg.MessageCollection(
    NotifyUDPInfo,
    UDPPing,
    UDPReceived,
)

class UDPProtocol(DatagramProtocol):
    def __init__(self, factory, port):
        '''
        port is the recommended UDP port. If unavailable, another port is used.
        '''
        self.factory = factory
        try:
            self.port = reactor.listenUDP(port, self)
        except CannotListenError:
            self.port = reactor.listenUDP(0, self)

    # To join a multicast group:
    # self.transport.joinGroup(multicastGroup)

    def send(self, string, address):
        self.transport.write(string, address)

    def datagramReceived(self, datagram, address):
        # First 4 characters are the connection id.
        if len(datagram) < 4:
            return
        connectionId = struct.unpack('!I', datagram[:4])[0]
        line = datagram[4:]
        self.factory._gotDatagram(connectionId, line, address)

class TCPReceiver(Int32StringReceiver):

    def connectionMade(self):
        self.handler = None
        self.connectionId = None

        # UDP-related members
        self.udpInfo = None
        self.udpValid = False
        self.udpPinger = None
        self.curPingValue = 0
        self.pingDelay = 1

        self.factory._newConnection(self)

    def sendMessage(self, msg):
        data = msg.pack()
        self.sendString(data)
        self.factory.tx += len(data)

    def connectionLost(self, reason):
        self.factory._lostConnection(self)

    def stringReceived(self, line):
        self.factory.rx += len(line)
        if self.handler is None:
            # First message received.
            self.factory._bindConnection(self, line)
            return

        # Translate special messages.
        try:
            msg = netmanMsgs.buildMessage(line)
        except netmsg.NetworkMessageError:
            # Not a special message: translate it according to the messages
            # that this handler recognises.
            try:
                msg = self.handler.messages.buildMessage(line)
            except netmsg.NetworkMessageError:
                # Unrecognised network message.
                if hasattr(self.handler, 'receiveBadString'):
                    self.handler.receiveBadString(self.connectionId, line)
                else:
                    remote = self.transport.getPeer()
                    log.warning('%s: bad string from %s: %r',
                            self.handler.__class__.__name__,
                            (remote.host, remote.port), line)
                return

            # Pass on the message.
            self.handler.receiveMessage(self.connectionId, msg)
            return

        # Process the special messages.
        if isinstance(msg, NotifyUDPInfo):
            # Record the remote id and take no action.
            self.udpInfo = msg
            self.udpValid = False

            # Start sending UDP pings to verify receipt.
            self.checkUdp()
        elif isinstance(msg, UDPPing):
            # Received UDP ping request.
            self.sendMessage(UDPReceived(msg.payload))
        elif isinstance(msg, UDPReceived):
            # A UDP ping response has been received. Check if it's valid.
            if msg.payload == self.curPingValue:
                self.udpPingSucceeded()

    def udpPingSucceeded(self):
        '''
        This is called automatically when a UDPReceived packet is received with
        a payload corresponding to the most recently sent ping.

        This method will automatically check UDP again in 30 seconds time.
        '''
        # Cancel any pending failure calls or checks.
        if self.udpPinger is not None and self.udpPinger.active():
            self.udpPinger.cancel()

        self.udpValid = True

        # Ping again in 30 seconds, just to be sure.
        self.udpPinger = WeakCallLater(30, self, 'checkUdp')
        self.curPingValue += 1  # Just to be sure it doesn't match.
        self.pingDelay = 1      # For next time the ping fails.

    def udpPingFailed(self):
        '''
        This is called automatically when 1 second passes after a ping has been
        sent. If udpPingSucceeded() is called first, it will cancel the calling
        of this method. Similarly, this method will adjust the current ping
        value so that udpPingSucceeded will not be called even if the ping
        response packet is subsequently received.

        This method tries to resend, waiting longer before resend each try
        until a maximum wait length of 30 seconds is reached.
        '''
        self.udpValid = False

        # Back off, but still ping again.
        self.pingDelay = min(30, self.pingDelay * 1.5)
        self.udpPinger = WeakCallLater(self.pingDelay, self, 'checkUdp')
        self.curPingValue += 1  # Just to be sure it doesn't match.

    def checkUdp(self):
        '''
        Assuming that the other end of the connection has already sent details
        about how to contact it by UDP, calling this method will begin sending
        UDP pings to see whether information sent via UDP is actually received.
        '''
        if self.udpInfo is None:
            return

        # Make sure that no-one else will call this function soon.
        if self.udpPinger is not None and self.udpPinger.active():
            self.udpPinger.cancel()

        # Select a ping value and send ping.
        self.curPingValue = (self.curPingValue + 1) % (2 ** 32)
        self.factory._sendUdpPing(self)

        # Set a timeout of 1 second on the ping.
        self.udpPinger = WeakCallLater(0.5, self, 'udpPingFailed')

class NetworkManager(Factory):
    '''
    To use the NetworkManager:
    1 Create a NetworkManager on your favourite TCP and UDP ports:
        nm = NetworkManager(6789, 6789)
    2 Add your favourite handlers to the factory:
        tsp = TrosnothServerProtocol()
        nm.addHandler(tsp)
      Note that this step is only necessary if you want to be able to accept
      incoming connections.
    3 If any incoming connections are made, the NetworkManager will call:
        handler.newConnection(connectionId, ipAddr, port)
      for the appropriate handler as determined by the handler greeting string.
    4 If any incoming messages are received, the NetworkManager will call:
        handler.receiveMessage(connectionId, message)
    5 If a connection is closed, the NetworkManager will call:
        handler.connectionLost(connectionId)

    * To make a connection:
        nm.connect(handler, address, tcpPort)
      Note that you can make a connection even with a handler that is not
      registered using nm.addHandler().
    * To send a message:
        nm.sendTCP(connectionId, message)
        nm.sendUDP(connectionId, message)
        nm.send(connectionId, message)
      Using nm.send() will use UDP where possible, but fall back to TCP if UDP
      to this host has not yet been verified.
    * To close a connection:
        nm.closeConnection(connectionId)
    * To unregister a handler:
        nm.removeHandler(handler)
    '''
    protocol = TCPReceiver

    def __init__(self, tcpPort, udpPort):
        if tcpPort is None:
            self._port = None
        else:
            self._port = reactor.listenTCP(tcpPort, self)

        if udpPort is None:
            udpPort = 0

        self._udp = UDPProtocol(self, udpPort)
        self._udpPort = self._udp.port.getHost().port

        self._handlers = {}         # greeting -> handler
        self._connections = {}      # connId -> connection
        self._attempting = {}       # (ip, port) -> (handler, connId)
        self._lastConnectionId = 0

        # For profiling.
        self.rx = 0
        self.tx = 0
        self.startTime = time.time()

    def kill(self):
        'Stops listening for incoming connections.'
        if self._port is not None:
            self._port.stopListening()
            self._port = None

    ##############
    # Handlers
    ##############

    # A handler MUST have:
    #   .greeting - must be a string used to choose handlers
    #   .messages - must behave like a netmsg.MessageCollection, used to
    #       interpret incoming messages.
    #   .newConnection(connectionId, ipAddr, port) - called when a new incoming
    #       connection is completed.
    #   .connectionComplete(connectionId) - called when a connection initiated
    #       by netman.connect() is completed.
    #   .receiveMessage(connectionId, message)
    #   .receiveBadString(connectionId, line)
    #   .connectionLost(connectionId)
    #   .connectionFailed(connectionId)

    def addHandler(self, handler):
        if handler.greeting in self._handlers:
            raise KeyError('handler already registered with greeting %r' %
                    (handler.greeting,))
        self._handlers[handler.greeting] = handler

    def removeHandler(self, handler):
        if self._handlers.get(handler.greeting) != handler:
            raise ValueError('handler not registered yet')
        del self._handlers[handler.greeting]

    ##############
    # Connections
    ##############

    def connect(self, handler, ipAddress, port, timeout=7):
        result = self._newConnectionId()
        self._connections[result] = None

        connector = reactor.connectTCP(ipAddress, port, self, timeout)
        self._attempting[connector] = (handler, result)

        return result

    def isConnectionValid(self, connectionId):
        return self._connections.get(connectionId) is not None

    def closeConnection(self, connectionId):
        # Silently fail if the connection id is invalid.
        try:
            connection = self._connections[connectionId]
        except KeyError:
            return

        # If the connection is not complete, do nothing.
        if connection is None:
            return

        # Disconnect.
        connection.transport.loseConnection()
        del self._connections[connectionId]

    ###############
    # Transmission
    ###############

    def sendTCP(self, connectionId, message):
        try:
            connection = self._connections[connectionId]
        except KeyError:
            raise ValueError('%d is not a valid connectionId' % (connectionId,))

        if connection is None:
            raise ValueError('connection not completely initialised yet')

        connection.sendMessage(message)

    def sendUDP(self, connectionId, message):
        try:
            connection = self._connections[connectionId]
        except KeyError:
            raise ValueError('%d is not a valid connectionId' % (connectionId,))

        if connection is None:
            raise ValueError('connection not completely initialised yet')
        udpInfo = connection.udpInfo
        if udpInfo is None:
            raise ValueError('connection has not yet received UDP info')

        # Pack the remote id in with the message and send to the correct
        # IP address and port.
        self._doUdpSend(connection, udpInfo, message)

    def send(self, connectionId, message):
        'Uses UDP if possible, TCP otherwise.'
        try:
            connection = self._connections[connectionId]
        except KeyError:
            raise ValueError('%r is not a valid connectionId' % (connectionId,))

        if connection is None:
            raise ValueError('connection not completely initialised yet')

        udpInfo = connection.udpInfo
        if udpInfo is None or not connection.udpValid:
            # Revert to TCP if UDP info is not yet received or UDP pings have
            # not yet got through.
            connection.sendMessage(message)
        else:
            # Use UDP where possible.
            self._doUdpSend(connection, udpInfo, message)

    ###############
    # Queries
    ###############

    def getTCPPort(self):
        return self._port.getHost().port

    def getAddress(self, connectionId):
        'Returns the (ipAddr, port) for the given connection.'
        try:
            connection = self._connections[connectionId]
        except KeyError:
            raise ValueError('%d is not a valid connectionId' % (connectionId,))

        if connection is None:
            raise ValueError('connection not completely initialised yet')

        address = connection.transport.getPeer()
        return (address.host, address.port)

    def getUDPStatus(self, connectionId):
        '''
        Returns True if UDP can be sent to this connection, False otherwise.
        Note that if you want to send a message using UDP but fall back to TCP
        if it's not verified yet, you can use the .send() method.
        '''

        try:
            connection = self._connections[connectionId]
        except KeyError:
            raise ValueError('%d is not a valid connectionId' % (connectionId,))

        if connection is None:
            raise ValueError('connection not completely initialised yet')

        udpInfo = connection.udpInfo
        if udpInfo is None or not connection.udpValid:
            # UDP info is not yet received or UDP pings have not yet got
            # through.
            return False
        else:
            return True

    ###############
    # Internals
    ###############

    def startedConnecting(self, connector):
        # Required by twisted.
        pass

    def clientConnectionLost(self, connector, reason):
        # Required by twisted.
        pass

    def buildProtocol(self, addr):
        result = Factory.buildProtocol(self, addr)
        return result

    def clientConnectionFailed(self, connector, reason):
        try:
            handler, connectionId = self._attempting[connector]
        except KeyError:
            # Should never happen, but it does.
            # There's not much we can do here since we can't get the connId.
            log.warning('NetworkManager: clientConnectionFailed without '
                    '_attempting')
            return

        del self._attempting[connector]
        del self._connections[connectionId]

        handler.connectionFailed(connectionId)

    def _doUdpSend(self, connection, udpInfo, message):
        self._udp.send(struct.pack('!I', udpInfo.remoteId) + message.pack(),
                (connection.transport.getPeer().host, udpInfo.udpPort))

    def _newConnection(self, connection):
        # Check if this is a connection made by me.
        try:
            connector = connection.transport.connector
        except AttributeError:
            # Remotely-initiated connection.
            return
        try:
            handler, connectionId = self._attempting[connector]
        except KeyError:
            # Remotely-initiated connection.
            return

        connection.handler = handler
        connection.connectionId = connectionId
        self._connections[connectionId] = connection

        # Send the greeting string.
        self.tx += len(handler.greeting)
        connection.sendString(handler.greeting)

        # Also send the remote id.
        connection.sendMessage(NotifyUDPInfo(self._udpPort, connectionId))

        # Clean up and notify the handler of completion.
        del self._attempting[connector]
        handler.connectionComplete(connectionId)

    def _lostConnection(self, connection):
        if connection.handler is None:
            # Not yet completed.
            return

        # Delete this connection id.
        try:
            del self._connections[connection.connectionId]
        except KeyError:
            # Just to be safe.
            pass

        # Notify the handler.
        connection.handler.connectionLost(connection.connectionId)

    def _bindConnection(self, connection, greeting):
        'Select the handler for incoming connection.'
        # Check if greeting is recognised.
        try:
            handler = self._handlers[greeting]
        except KeyError:
            # Greeting not recognised. Drop connection.
            connection.transport.loseConnection()
            return

        # Assign a connection id.
        try:
            connection.connectionId = connectionId = self._newConnectionId()
        except OverflowError:
            # Cannot accept any new connections.
            connection.transport.loseConnection()
            return
        connection.handler = handler
        self._connections[connectionId] = connection

        # Send the remote id to the connection.
        connection.sendMessage(NotifyUDPInfo(self._udpPort, connectionId))

        # Notify the handler.
        handler.newConnection(connection.connectionId,
                connection.transport.getPeer().host,
                connection.transport.getPeer().port)

    def _newConnectionId(self):
        startId = self._lastConnectionId
        self._lastConnectionId = (self._lastConnectionId + 1) % (2**32)
        while self._lastConnectionId != startId:
            if self._lastConnectionId not in self._connections:
                return self._lastConnectionId
            self._lastConnectionId = (self._lastConnectionId + 1) % (2**32)
        raise OverflowError('Run out of connection ids')

    def _gotDatagram(self, connectionId, line, address):
        try:
            connection = self._connections[connectionId]
        except KeyError:
            # Unrecognised id.
            return

        if connection is None:
            # Connection not yet completed.
            return

        # Check that this is coming from the correct IP address.
        if connection.transport.getPeer().host != address[0]:
            return

        # Translate the message.
        connection.stringReceived(line)

    def _sendUdpPing(self, connection):
        '''
        Called by a connection when it wants to send a UDP ping to its other
        end. This should only be called once the UDP info from the other end
        has been received.
        The payload of the ping is taken from connection.curPingValue.
        '''
        message = UDPPing(connection.curPingValue)
        self._doUdpSend(connection, connection.udpInfo, message)
