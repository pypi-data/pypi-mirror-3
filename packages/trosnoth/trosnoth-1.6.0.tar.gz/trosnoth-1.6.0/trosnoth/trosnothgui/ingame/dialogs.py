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

from trosnoth.gui.framework.dialogbox import (DialogBox, DialogResult,
        DialogBoxAttachedPoint)
from trosnoth.gui.common import ScaledSize, Area, ScaledLocation, Location
from trosnoth.gui.framework import elements, prompt

class JoinGameDialog(DialogBox):
    def __init__(self, app, gmInterface, world):
        super(JoinGameDialog, self).__init__(app, ScaledSize(512, 314),
                'Join Game')
        self.result = None
        self.gmInterface = gmInterface
        self.selectedTeam = None

        fonts = self.app.screenManager.fonts
        self.nickBox = prompt.InputBox(
            self.app,
            Area(DialogBoxAttachedPoint(self, ScaledSize(0, 40), 'midtop'),
                    ScaledSize(200, 60), 'midtop'),
            '',
            font = fonts.menuFont,
            maxLength = 30
        )
        self.nickBox.onClick.addListener(self.setFocus)
        self.nickBox.onTab.addListener(lambda sender: self.clearFocus())
        name = app.identitySettings.nick
        if name is not None:
            self.nickBox.setValue(name)

        colours = app.theme.colours
        self.cantJoinYet = elements.TextElement(
            self.app,
            '',
            fonts.ingameMenuFont,
            ScaledLocation(256, 115, 'center'),
            colours.cannotJoinColour,
        )

        teamA = world.teams[0]
        teamB = world.teams[1]

        self.elements = [
            elements.TextElement(
                self.app,
                'Please enter your nick:',
                fonts.smallMenuFont,
                Location(DialogBoxAttachedPoint(self, ScaledSize(0, 10),
                        'midtop'), 'midtop'),
                colours.black,
            ),
            self.nickBox,
            self.cantJoinYet,
            elements.TextElement(
                self.app,
                'Select team:',
                fonts.smallMenuFont,
                Location(DialogBoxAttachedPoint(self, ScaledSize(0, 130),
                        'midtop'), 'midtop'),
                colours.black,
            ),

            elements.TextButton(
                self.app,
                Location(DialogBoxAttachedPoint(self, ScaledSize(-25, 160),
                        'midtop'), 'topright'),
                str(teamA),
                fonts.menuFont,
                colours.team1msg,
                colours.white,
                onClick=lambda obj: self.joinTeam(teamA)
            ),
            elements.TextButton(
                self.app,
                Location(DialogBoxAttachedPoint(self, ScaledSize(25, 160),
                        'midtop'), 'topleft'),
                str(teamB),
                fonts.menuFont,
                colours.team2msg,
                colours.white,
                onClick=lambda obj: self.joinTeam(teamB)
            ),
            elements.TextButton(
                self.app,
                Location(DialogBoxAttachedPoint(self, ScaledSize(0, 210),
                        'midtop'), 'midtop'),
                'Automatic',
                fonts.menuFont,
                colours.inGameButtonColour,
                colours.white,
                onClick=lambda obj: self.joinTeam()
            ),

            elements.TextButton(
                self.app,
                Location(DialogBoxAttachedPoint(self, ScaledSize(0, -10),
                        'midbottom'), 'midbottom'),
                'Cancel',
                fonts.menuFont,
                colours.inGameButtonColour,
                colours.white,
                onClick=self.cancel
            )
        ]
        self.setColours(colours.joinGameBorderColour,
                colours.joinGameTitleColour, colours.joinGameBackgroundColour)
        self.setFocus(self.nickBox)

    def joinTeam(self, team = None):
        self.selectedTeam = team
        self.cantJoinYet.setText('')

        nick = self.nickBox.value
        if nick == '' or nick.isspace():
            # Disallow all-whitespace nicks
            return

        self.result = DialogResult.OK
        self.close()

    def cancel(self, sender):
        self.result = DialogResult.Cancel
        self.close()

class JoiningDialog(DialogBox):
    def __init__(self, app, gameMenuInterface):
        super(JoiningDialog, self).__init__(app, ScaledSize(530, 180),
                'Trosnoth')
        colours = app.theme.colours
        self.gmInterface = gameMenuInterface

        fonts = self.app.screenManager.fonts
        self.text = elements.TextElement(
            self.app,
            '',
            fonts.menuFont,
            Location(DialogBoxAttachedPoint(self, ScaledSize(0, 40), 'midtop'),
                    'midtop'),
            colour = colours.joiningColour
        )

        self.elements = [self.text,
            elements.TextButton(
                self.app,
                Location(DialogBoxAttachedPoint(self, ScaledSize(0, -10),
                        'midbottom'), 'midbottom'),
                'Cancel',
                fonts.menuFont,
                colours.inGameButtonColour,
                colours.white,
                onClick=gameMenuInterface.cancelJoin
            )
        ]
        self.setColours(colours.joinGameBorderColour,
                colours.joinGameTitleColour, colours.joinGameBackgroundColour)

    def show(self, nick):
        self.text.setText('Joining as %s...' % (nick,))
        DialogBox.show(self)
