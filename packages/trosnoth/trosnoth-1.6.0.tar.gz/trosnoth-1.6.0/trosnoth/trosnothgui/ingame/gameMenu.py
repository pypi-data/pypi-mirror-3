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

from trosnoth.trosnothgui.ingame.ingameMenu import InGameMenu
from trosnoth.trosnothgui.ingame.dialogs import JoinGameDialog, JoiningDialog
from trosnoth.gui.framework.dialogbox import DialogResult
from trosnoth.gui.errors import MultiWindowException
from trosnoth.model.universe_base import GameState
from trosnoth.utils.twist import WeakCallLater

class GameMenu(InGameMenu):
    '''This is not actually a menu any more, but rather a controller used only
    when joining the game.'''

    def __init__(self, app, gameInterface, game):
        super(GameMenu, self).__init__(app)
        self.gameController = game.gameController
        self.world = game.world
        self.interface = gameInterface
        self.joined = False
        self.joiningInfo = None
        self.gameInterface = gameInterface

        self.joiningScreen = JoiningDialog(self.app, self)

        self.joinGameDialog = JoinGameDialog(self.app, self, self.world)
        self.joinGameDialog.onClose.addListener(self._joinDlgClose)
        self.joinGameDialog.show()

        if self.gameController.state() in (GameState.Lobby, GameState.Ended):
            WeakCallLater(0.1, self, 'gotWorldParameters')

    def gotWorldParameters(self):
        if (self.joinGameDialog.showing and self.gameController.state() in
                (GameState.Lobby, GameState.Ended)):
            nick = self.app.identitySettings.nick
            if nick is not None:
                self.joinGameDialog.close()
                self.attemptGameJoin(nick, None)
                return

    def cleanUp(self):
        try:
            self.joinGameDialog.close()
        except MultiWindowException:
            pass
        try:
            self.joiningScreen.close()
        except MultiWindowException:
            pass

    def _joinDlgClose(self):
        if self.joinGameDialog.result is None:
            return
        elif self.joinGameDialog.result != DialogResult.OK:
            self.interface.disconnect()
        else:
            nick = self.joinGameDialog.nickBox.value.strip()
            self.app.identitySettings.setNick(nick)

            team = self.joinGameDialog.selectedTeam
            self.attemptGameJoin(nick, team)

    def attemptGameJoin(self, nick, team):
        self.joiningInfo = nick, team
        self.joiningScreen.show(nick)
        self.interface.joinGame(nick, team).addCallback(self.joinComplete
                ).addErrback(self.joinErrback)

    def showMessage(self, text):
        self.joinGameDialog.cantJoinYet.setText(text)

    def cancelJoin(self, sender):
        self.joiningScreen.close()
        self.joinGameDialog.show()

    def joinComplete(self, result):
        if result[0] == 'success':
            # Join was successful.
            player = result[1]
            self.joined = True
            self.interface.joined(player)
            self.joiningScreen.close()
            self.interface.gameViewer.leaderboard.update()
            return

        self.joiningScreen.close()
        self.joinGameDialog.show()

        if result[0] == 'full':
            # Team is full.
            self.showMessage('That team is full!')
        elif result[0] == 'over':
            # The game is over.
            self.showMessage('The game is over!')
        elif result[0] == 'nick':
            # Nickname is already being used.
            self.showMessage('That name is already being used!')
        elif result[0] == 'badn':
            # Nickname is too short or long.
            self.showMessage('That name is not allowed!')
        elif result[0] == 'auth':
            self.showMessage('You are not authorised to join!')
        elif result[0] == 'user':
            self.showMessage('Cannot join the same game twice!')
        elif result[0] == 'wait':
            # Need to wait a few seconds before rejoining.
            self.showMessage('You need to wait ' + result[1] +
                    ' seconds before rejoining.')
        elif result[0] == 'timeout':
            self.showMessage('Join timed out.')
        elif result[0] == 'error':
            # Python error.
            self.showMessage('Join failed: python error')
        elif result[0] == 'cancel':
            # Do nothing: join cancelled.
            pass
        else:
            # Unknown reason.
            self.showMessage('Join failed: ' + result[0])

    def joinErrback(self, error):
        'Errback for joining game.'
        error.printTraceback()
        self.joinComplete(['There was an error'])
