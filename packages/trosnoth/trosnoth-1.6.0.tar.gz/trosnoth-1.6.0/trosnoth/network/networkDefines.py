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

multicastPort = 5253
UDPClientLANPort = 0
UDPClientInetPort = 6788
defaultServerPort = 6789

multicastGroup = '224.0.0.234'

clientVersion = 'client.v1.6.0+'
serverVersion = 'server.v1.6.0+'
validServerVersions = set(['server.v1.6.0+'])

defaultSettings = {'halfMapWidth': 3,
                   'mapHeight': 2,
                   'maxPlayers': 8,
                   'gameDuration' : 0,
                   # teamNames is a list of two strings
                   'teamNames': False,
                   'beginNow': False,
                   'recordReplay': True,
                   'testMode': False
                   }

validServerAdminIPs = ('127.0.0.1',)

def validServerAdminSender(ip):
    return ip in validServerAdminIPs

