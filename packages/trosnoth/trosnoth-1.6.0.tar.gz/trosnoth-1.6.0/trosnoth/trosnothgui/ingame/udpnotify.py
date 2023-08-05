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

class UDPNotificationBar(NotificationBar):
    '''
    Provides a message that UDP communication with server is not working.
    '''
    def __init__(self, app):
        super(UDPNotificationBar, self).__init__(app,
            message =
                'Slow connection due to UDP failure. Click for more info.',
            url = 'http://www.trosnoth.org/docs/udp_failure',
            font = app.fonts.default,
            area = Area(
                ScaledPoint(0, 0),
                ScaledSize(1024, 30),
                'topleft'
            ),
            buttonPos = Location(ScaledPoint(1024, 0), 'topright'),
            textPos = Area(
                ScaledPoint(512, 15),
                ScaledSize(1024, 30),
                'centre'
            ),
        )
