import os
from twisted.internet import reactor, task

from trosnoth.model.mapLayout import LayoutDatabase
from trosnoth.game import makeLocalGame

class DummyApp(object):
    pass

def runTest():
    '''
    Run a world simulation with a bunch of AIs and print the instantaneous frame
    rate 5 times per second for 10 seconds.
    '''
    players = 100
    halfWidth = 2
    height = 1

    app = DummyApp()
    db = LayoutDatabase(app)
    game = makeLocalGame(os.path.basename(__file__), db, halfWidth, height)
    game.startGame()

    ais = []
    for i in xrange(players):
        ais.append(game.addAI('alpha'))

    task.LoopingCall(printRate, game).start(.2)
    reactor.callLater(10, finishTest)
    reactor.run()

def printRate(game):
    print game.world.frameRate

def finishTest():
    reactor.stop()

if __name__ == '__main__':
    runTest()
