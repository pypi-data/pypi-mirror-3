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

import pygame

from trosnoth.gui.framework import framework, prompt
from trosnoth.gui.framework.elements import TextElement
from trosnoth.gui.framework.checkbox import CheckBox
from trosnoth.gui.framework.tab import Tab
from trosnoth.trosnothgui.common import button
from trosnoth.gui.common import ScaledLocation, ScaledArea
from trosnoth.utils.event import Event

class DisplaySettingsTab(Tab, framework.TabFriendlyCompoundElement):
    def __init__(self, app, onClose=None):
        super(DisplaySettingsTab, self).__init__(app, 'Display')

        self.onClose = Event()
        if onClose is not None:
            self.onClose.addListener(onClose)

        font = self.app.screenManager.fonts.bigMenuFont
        smallNoteFont = self.app.screenManager.fonts.smallNoteFont

        colour = self.app.theme.colours.headingColour
        def mkText(text, x, y, textFont=font, anchor='topright'):
            return TextElement(self.app, text, textFont,
                    ScaledLocation(x, y, anchor),
                    colour)

        self.text = [
            mkText('X', 640, 250),
            mkText('Screen resolution', 430, 250),
            mkText('Fullscreen mode', 430, 315),
            mkText('Use alpha channel', 430, 380),
            mkText('Translucent windows', 430, 445),
            mkText('Looks pretty but slows things down', 520, 452,
                    smallNoteFont, 'topleft'),
            mkText('Smooth panning', 430, 510),
            mkText('Centre on player', 430, 575),
        ]

        self.invalidInputText = TextElement(self.app, '', font,
                ScaledLocation(512, 185,'midtop'), (192, 0, 0))

        self.widthInput = prompt.InputBox(self.app,
                ScaledArea(460, 235, 150, 60),
                initValue=str(self.app.screenManager.size[0]), font=font,
                maxLength=4, validator=prompt.intValidator)

        self.widthInput.onEnter.addListener(lambda sender: self.saveSettings())
        self.widthInput.onClick.addListener(self.setFocus)
        self.widthInput.onTab.addListener(self.tabNext)

        self.heightInput = prompt.InputBox(self.app,
                ScaledArea(652, 235, 150, 60),
                initValue=str(self.app.screenManager.size[1]), font=font,
                maxLength=4, validator=prompt.intValidator)

        self.heightInput.onEnter.addListener(lambda sender: self.saveSettings())
        self.heightInput.onClick.addListener(self.setFocus)
        self.heightInput.onTab.addListener(self.tabNext)

        self.tabOrder = [self.widthInput, self.heightInput]

        self.fullscreenBox = CheckBox(self.app,
            ScaledLocation(460, 320),
            text='',
            font=font,
            colour=(192, 192, 192),
            initValue=self.app.screenManager.isFullScreen(),
        )
        self.fullscreenBox.onValueChanged.addListener(self.fullscreenChanged)

        self.alphaBox = CheckBox(self.app,
            ScaledLocation(460, 385),
            text='',
            font=font,
            colour=(192, 192, 192),
            initValue=self.app.displaySettings.useAlpha,
        )

        self.windowsBox = CheckBox(self.app,
            ScaledLocation(460, 450),
            text='',
            font=font,
            colour=(192,192,192),
            initValue=app.displaySettings.windowsTranslucent,
        )

        self.panningBox = CheckBox(self.app,
            ScaledLocation(460, 515),
            text='',
            font=font,
            colour=(192,192,192),
            initValue=app.displaySettings.smoothPanning,
        )

        self.centreOnPlayerBox = CheckBox(self.app,
            ScaledLocation(460, 580),
            text='',
            font=font,
            colour=(192,192,192),
            initValue=app.displaySettings.centreOnPlayer,
        )

        self.input = [self.widthInput, self.heightInput, self.widthInput,
                self.fullscreenBox, self.alphaBox, self.windowsBox,
                self.panningBox, self.centreOnPlayerBox]

        self.elements = self.text + self.input + [
            self.invalidInputText,
            button(app, 'save', self.saveSettings, (-100, -75), 'midbottom',
                    secondColour=app.theme.colours.white),
            button(app, 'cancel', self.cancelMenu, (100, -75), 'midbottom',
                    secondColour=app.theme.colours.white),
        ]
        self.setFocus(self.widthInput)


    def cancelMenu(self):
        self.fullscreenBox.setValue(self.app.screenManager.isFullScreen())
        self.alphaBox.setValue(self.app.displaySettings.useAlpha)
        self.windowsBox.setValue(self.app.displaySettings.windowsTranslucent)
        self.panningBox.setValue(self.app.displaySettings.smoothPanning)
        self.centreOnPlayerBox.setValue(self.app.displaySettings.centreOnPlayer)
        self.heightInput.setValue(str(self.app.screenManager.size[1]))
        self.widthInput.setValue(str(self.app.screenManager.size[0]))

        self.onClose.execute()

    def saveSettings(self):
        values = self.getValues()
        if values is not None:
            (screenSize, fullScreen, useAlpha, windowsTranslucent,
                    smoothPanning, centreOnPlayer) = values

            # Save these values.
            self.app.displaySettings.fullScreen = fullScreen
            self.app.displaySettings.useAlpha = useAlpha
            self.app.displaySettings.windowsTranslucent = windowsTranslucent
            self.app.displaySettings.smoothPanning = smoothPanning
            self.app.displaySettings.centreOnPlayer = centreOnPlayer
            if fullScreen:
                self.app.displaySettings.fsSize = screenSize
            else:
                self.app.displaySettings.size = screenSize

            # Write to file and apply.
            self.app.displaySettings.save()
            self.app.displaySettings.apply()

            self.onClose.execute()

    def getValues(self):

        height = self.getInt(self.heightInput.value)
        width = self.getInt(self.widthInput.value)
        fullScreen = self.fullscreenBox.value
        useAlpha = self.alphaBox.value
        windowsTranslucent = self.windowsBox.value
        smoothPanning = self.panningBox.value
        centreOnPlayer = self.centreOnPlayerBox.value

        # The resolutionList is used when fullScreen is true.
        resolutionList = pygame.display.list_modes()
        resolutionList.sort()
        minResolution = resolutionList[0]
        maxResolution = resolutionList[-1]

        if not fullScreen:
            minResolution = (320, 240)

        # These values are used when fullScreen is false.
        widthRange = (minResolution[0], maxResolution[0])
        heightRange = (minResolution[1], maxResolution[1])

        if not widthRange[0] <= width <= widthRange[1]:
            self.incorrectInput('Screen width must be between %d and %d' %
                                (widthRange[0], widthRange[1]))
            width = None
            return
        if not heightRange[0] <= height <= heightRange[1]:
            self.incorrectInput('Screen height must be between %d and %d' %
                                (heightRange[0], heightRange[1]))
            height = None
            return
        if fullScreen:
            selectedResolution = (width, height)
            if selectedResolution not in resolutionList:
                self.incorrectInput('Selected resolution is not valid for '
                        'this display')
                height = width = None
                return

        self.incorrectInput('')

        return ((width, height), fullScreen, useAlpha, windowsTranslucent,
                smoothPanning, centreOnPlayer)

    def getInt(self, value):
        if value == '':
            return 0
        return int(value)

    def incorrectInput(self, string):
        self.invalidInputText.setText(string)
        self.invalidInputText.setFont(self.app.screenManager.fonts.bigMenuFont)

    def fullscreenChanged(self, element):
        # If the resolution boxes haven't been touched, swap their values to
        # the appropriate resolution for the new mode.

        height = self.getInt(self.heightInput.value)
        width = self.getInt(self.widthInput.value)
        fullScreen = self.fullscreenBox.value

        if fullScreen:
            # Going to full screen mode.
            if (width, height) != self.app.displaySettings.size:
                return
            width, height = self.app.displaySettings.fsSize
        else:
            # Going from full screen mode.
            if (width, height) != self.app.displaySettings.fsSize:
                return
            width, height = self.app.displaySettings.size

        self.heightInput.setValue(str(height))
        self.widthInput.setValue(str(width))
