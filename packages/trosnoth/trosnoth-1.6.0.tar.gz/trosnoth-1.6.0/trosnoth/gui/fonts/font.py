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

from trosnoth.gui.fonts import fontcache

class Font(object):
    def __init__(self, name, size, bold = False):
        self._name = name
        self._size = size
        self._bold = bold
        self._app = None
        self._filename = None

    def render(self, app, text, antialias, colour, background=None):
        if background==None:
            return self._getFont(app).render(text, antialias, colour)
        else:
            return self._getFont(app).render(text, antialias, colour,
                    background)

    def size(self, app, text):
        return self._getFont(app).size(text)

    def getLineSize(self, app):
        return self._getFont(app).get_linesize()

    def getHeight(self, app):
        return self._getFont(app).get_height()

    def _getFont(self, app):
        if app != self._app:
            filename = self._filename = app.getFontFilename(self._name)
            self._app = app
        else:
            filename = self._filename
        return fontcache.get(filename, self._size, self._bold)

    def __repr__(self):
        return "Font: %s size %d" % (self._name, self._size)

class ScaledFont(Font):
    def _getFont(self, app):
        if app != self._app:
            filename = self._filename = app.getFontFilename(self._name)
            self._app = app
        else:
            filename = self._filename
        return fontcache.get(filename,
                int(self._size * app.screenManager.scaleFactor + 0.5),
                self._bold)

    def __repr__(self):
        return "Scaled Font: %s size %d" % (self._name, self._size)
