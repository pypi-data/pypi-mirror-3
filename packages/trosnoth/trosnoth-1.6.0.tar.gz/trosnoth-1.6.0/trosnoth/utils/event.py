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

class Event(object):
    def __init__(self, listener=None):
        self.listeners = set()
        if listener is not None:
            self.addListener(listener)

    def addListener(self, obj):
        self.listeners.add(obj)

    def removeListener(self, obj):
        self.listeners.remove(obj)

    def execute(self, *args, **kwargs):
        for call in self.listeners:
            call(*args, **kwargs)

    __call__ = execute
