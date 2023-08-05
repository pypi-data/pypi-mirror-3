import os
import time

from twisted.internet import reactor, task

from trosnoth.model.mapLayout import LayoutDatabase
from trosnoth.game import makeLocalGame, makeIsolatedGame
from trosnoth.network.netman import NetworkManager
from trosnoth.network.server import ServerNetHandler
from trosnoth.network.client import ClientNetHandler

class DummyApp(object):
    pass

def runTest():
    '''
    Creates a server and many AI clients and starts a game, reporting regularly on
    the amount of Network traffic for a period of time.
    '''
    players = 10
    halfWidth = 2
    height = 1
    duration = 10
    reportRate = 0.2

    app = DummyApp()
    netman = NetworkManager(0, 0)
    db = LayoutDatabase(app)
    game = makeLocalGame(os.path.basename(__file__), db, halfWidth, height)
    game.startGame()

    server = ServerNetHandler(netman, game)
    netman.addHandler(server)

    port = netman.getTCPPort()

    ais = []
    for i in xrange(players):
        make_ai(db, ais, port)

    task.LoopingCall(printRate, netman).start(reportRate)
    reactor.callLater(duration, finishTest)
    reactor.run()

def make_ai(db, ais, port):
    netman = NetworkManager(0, 0)
    handler = ClientNetHandler(netman)
    d = handler.makeConnection('localhost', port)
    @d.addCallback
    def gotConnection(r):
        game, eventPlug, controlPlug = makeIsolatedGame(db)
        handler.requestPlug.connectPlug(controlPlug)
        handler.eventPlug.connectPlug(eventPlug)
        ais.append(game.addAI('alpha'))
        game.syncWorld()

    @d.addErrback
    def connectionFail(r):
        print 'Connection failed: %r' % (r,)

def printRate(netman):
    rx = netman.rx
    tx = netman.tx
    t = time.time() - netman.startTime
    print 'av rx %.2f bytes/sec\tav tx %.2f bytes/sec' % (rx / t, tx / t)

def finishTest():
    reactor.stop()

if __name__ == '__main__':
    runTest()
