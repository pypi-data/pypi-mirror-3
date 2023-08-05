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

from trosnoth.utils.event import Event

def test_EventFired():
    e = Event()
    called = [False]
    def fn():
        called[0] = True
    e.addListener(fn)
    assert(called[0] == False)
    e()
    assert(called[0] == True)

def test_EventUnsubscribed():
    e = Event()
    called = [False]
    def fn():
        called[0] = True
    e.addListener(fn)
    e.removeListener(fn)
    assert(called[0] == False)
    e()
    assert(called[0] == False)


def test_eventsWithArgs():
    e = Event()
    values = [None, None]
    def fn(value1, value2):
        values[0] = value1
        values[1] = value2
    e.addListener(fn)
    assert(values == [None, None])
    e(42, 'alligator')
    assert(values == [42, 'alligator'])


def test_eventsWithKeywordArgs():
    e = Event()
    d = {'value1' : 42,
         'value3' : 'a second value'}
    values = [None, None, None]
    def fn(value1=None, value2=None, value3=None):
        values[0] = value1
        values[1] = value2
        values[2] = value3
        
    e.addListener(fn)
    assert(values == [None, None, None])
    e(**d)
    assert(values == [42, None, 'a second value'])

