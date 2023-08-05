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

from trosnoth.gui.common import Location, Area, ScaledPoint, ScaledSize
from trosnoth.gui.notify import NotificationBar

class InternetGameNotificationBar(NotificationBar):
    '''
    Provides a message indicating that games won't be visible on the Internet.
    '''
    def __init__(self, app):
        super(InternetGameNotificationBar, self).__init__(app,
            message='Games you create may not be visible on the Internet. '
                'Click for info.',
            url='http://www.trosnoth.org/docs/'
                'games-you-create-may-not-be-visible',
            font = app.fonts.default,
            area = Area( ScaledPoint(0, 0), ScaledSize(1024, 30), 'topleft'),
            buttonPos = Location(ScaledPoint(1024, 0), 'topright'),
            textPos = Area( ScaledPoint(512, 15), ScaledSize(1024, 30),
                'centre'),
        )
