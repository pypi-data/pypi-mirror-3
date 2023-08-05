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

from optparse import OptionParser

from trosnoth.run.main import Main
from trosnoth.utils.utils import initLogging, Function

def makeOptionParser():
    parser = OptionParser()
    parser.add_option('-u', '--auth-server', action='store', dest='server',
        help='connect to the given authentication server')
    parser.add_option('-p', '--play-menu', action='store_const', dest='mode',
        const='play', help='launch the play menu')
    parser.add_option('--key-settings', action='store_const', dest='mode',
        const='keysettings', help='launch the keyboard settings screen')
    parser.add_option('--archives', action='store_const', dest='mode',
        const='archives', help='launch the archives screen')
    parser.add_option('-s', '--solo', action='store_const', dest='mode',
        const='solo', default='normal',
        help='run Trosnoth in solo mode.')
    parser.add_option('-i', '--isolate', action='store_const', dest='mode',
        const='isolate',
        help='run Trosnoth in isolated test mode. Creates client and server '
        'Universe objects, but does not use the network to connect them.')
    parser.add_option('-t', '--test', action='store_true', dest='testMode',
        help='run Trosnoth in test mode. This means that players will get 20 '
        'stars each and upgrades will only cost 1 star.')
    parser.add_option('-c', '--checkpoint', action='store_true', dest='checkpoint',
        help='store which checkpoints have been reached.')
    parser.add_option('-b', '--testblock', action='store', dest='mapBlock',
        help='tests the map block with the given filename.')
    parser.add_option('-a', '--aicount', action='store', dest='aiCount',
        help='the number of AIs to include.')
    parser.add_option('-w', '--halfwidth', action='store', dest='halfWidth',
        help='the half map width')
    parser.add_option('-H', '--height', action='store', dest='height',
        help='the map height')
    parser.add_option('-S', '--stack-teams', action='store_true', dest='stackTeams',
        help='stack all the AI players on one team.')
    parser.add_option('-A', '--aiclass', action='store', dest='aiClass',
        help='the name of the module to import from trosnoth.ais.')
    parser.add_option('--list-ais', action='store_const', dest='mode',
        const='listais', help='list available AI classes and exit')
    parser.add_option('-d', '--debug', action='store_true', dest='debug',
        help='show debug-level messages on console')
    parser.add_option('-l', '--log-file', action='store', dest='logFile',
        help='file to write logs to')
    return parser

def listAIs():
    import trosnoth.ai
    print 'Available AI classes:'
    for name in trosnoth.ai.listAIs():
        print '  %s' % (name,)
    return

class processOptions(Function):
    TESTMODE_AI_COUNT = 7
    TESTMODE_HALF_WIDTH = 1
    TESTMODE_HEIGHT = 1
    BLOCKTEST_HALF_WIDTH = 2
    BLOCKTEST_HEIGHT = 1

    def run(self, options, parser):
        if options.server is not None:
            if options.mode != 'normal':
                parser.error('multiple modes specified')
            options.mode = 'auth'

        if options.mode == 'normal' and (options.testMode or options.mapBlock or
                options.aiCount or options.halfWidth or options.height or
                options.stackTeams or options.aiClass):
            options.mode = 'solo'
        if options.aiClass is None:
            options.aiClass = 'alpha'

        if options.mode == 'auth':
            if ':' in options.server:
                host, port = options.server.split(':', 1)
                try:
                    port = int(port)
                except ValueError:
                    parser.error('%r is not a valid port' % (port,))
            else:
                host = options.server
                port = 6787
            options.host, options.port = host, port
        elif options.mode in ('solo', 'isolate'):
            isolate = options.mode == 'isolate'
            options.mode = 'solo'
            if options.mapBlock is None:
                mapBlocks  =[]
                aiCount = options.aiCount or self.TESTMODE_AI_COUNT
                halfWidth = options.halfWidth or self.TESTMODE_HALF_WIDTH
                height = options.height or self.TESTMODE_HEIGHT
                startInLobby = False
            else:
                mapBlocks = [options.mapBlock]
                aiCount = options.aiCount or 0
                halfWidth = options.halfWidth or self.BLOCKTEST_HALF_WIDTH
                height = options.height or self.BLOCKTEST_HEIGHT
                startInLobby = True
            options.soloArgs = dict(isolate=isolate, testMode=options.testMode,
                mapBlocks=mapBlocks, size=(int(halfWidth), int(height)),
                aiCount=int(aiCount), lobby=startInLobby,
                stackTeams=options.stackTeams, aiClass=options.aiClass)

        elif options.mode not in ('normal', 'listais', 'play', 'keysettings', 'archives'):
            assert False, 'Unknown mode'

class main(Function):
    parser = makeOptionParser()

    listAIs = listAIs
    appFactory = Main

    def run(self):
        options, args = self.parser.parse_args()
        if len(args) > 0:
            self.parser.error('no arguments expected')

        initLogging(options.debug, options.logFile)

        processOptions(options, self.parser)

        if options.mode == 'listais':
            self.listAIs()
            return

        if options.mode == 'normal':
            mainObject = self.makeNormalApp()
        elif options.mode == 'auth':
            mainObject = self.makeAuthApp(options)
        elif options.mode in ('play', 'keysettings', 'archives'):
            mainObject = self.makeSubscreenApp(options.mode)
        elif options.mode == 'solo':
            mainObject = self.makeSoloApp(options)
        else:
            assert False, 'Unknown mode'

        try:
            mainObject.run_twisted()
        finally:
            if options.checkpoint:
                self.saveCheckpoints()

    def makeNormalApp(self):
        return self.appFactory()

    def makeAuthApp(self, options):
        return self.appFactory(serverDetails=(options.host, options.port))

    def makeSubscreenApp(self, mode):
        return self.appFactory(screen=mode)

    def makeSoloApp(self, options):
        from trosnoth.run import solotest
        return solotest.Main(**options.soloArgs)

    def saveCheckpoints(self):
        from trosnoth.utils.checkpoint import saveCheckpoints
        saveCheckpoints()

if __name__ == '__main__':
    main()

