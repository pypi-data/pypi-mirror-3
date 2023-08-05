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

from trosnoth.gui.screenManager.screenManager import ScreenManager
from trosnoth.gui.errors import MultiWindowException

class WindowManager(ScreenManager):
    '''Handles all the dialog boxes and the main screen'''

    def __init__(self, app, element, size, settings, caption):
        super(WindowManager, self).__init__(app, size, settings, caption)
        self.boxes = []

    def createInterface(self, element):
        super(WindowManager,self).createInterface(element)
        self._fixElements()

    def showDialog(self, dialog):
        self.boxes.insert(len(self.elements)-1, dialog)
        self._fixElements()

    def closeDialog(self, dialog):
        if dialog not in self.boxes:
            raise MultiWindowException(
                    "Attempt to close a dialog that was not open")
        self.boxes.remove(dialog)
        self._fixElements()

    def dialogFocus(self, dialog):
        index = self.boxes.index(dialog)
        self.boxes = (self.boxes[:index] + self.boxes[index+1:] +
                [self.boxes[index]])
        self._fixElements()

    def _fixElements(self):
        self.elements = [self.interface]+ self.boxes
        if self.pointer is not None:
            self.elements.append(self.pointer)
        self.elements.append(self.terminator)
