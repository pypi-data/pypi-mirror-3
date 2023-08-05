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
from trosnoth.gui.common import Region, Abs

class AppStub(object):
    def __init__(self):
        self.screenManager = self

def test_main_corners():
    r = Region(topleft=Abs(0, 1), bottomright=Abs(2, 3))
    app = AppStub()
    x = r.getRect(app)
    assert x.topleft == (0, 1)
    assert x.bottomright == (2, 3)

def test_other_corners():
    r = Region(topright=Abs(5, 2), bottomleft=Abs(1, 3))
    app = AppStub()
    x = r.getRect(app)
    assert x.topright == (5, 2)
    assert x.bottomleft == (1, 3)

def test_corner_and_size():
    r = Region(topright=Abs(5, 2), size=Abs(3, 3))
    app = AppStub()
    x = r.getRect(app)
    assert x.topright == (5, 2)
    assert x.size == (3, 3)

def test_corner_width_height():
    r = Region(topleft=Abs(5, 2), width=Abs(5), height=Abs(2))
    app = AppStub()
    x = r.getRect(app)
    assert x.topleft == (5, 2)
    assert x.width == 5
    assert x.height == 2

def test_aspect_ratio_y_1():
    r = Region(topleft=Abs(10, 15), centrex=Abs(40), aspect=2)
    app = AppStub()
    x = r.getRect(app)
    assert x.topleft == (10, 15)
    assert x.centerx == 40
    assert x.width == 2 * x.height

def test_aspect_ratio_y_2():
    r = Region(midleft=Abs(10, 15), centrex=Abs(40), aspect=2)
    app = AppStub()
    x = r.getRect(app)
    assert x.midleft == (10, 15)
    assert x.centerx == 40
    assert x.width == 2 * x.height

def test_aspect_ratio_y_3():
    r = Region(bottomleft=Abs(10, 15), centrex=Abs(40), aspect=2)
    app = AppStub()
    x = r.getRect(app)
    assert x.bottomleft == (10, 15)
    assert x.centerx == 40
    assert x.width == 2 * x.height

def test_aspect_ratio_y_4():
    try:
        Region(left=Abs(10), centrex=Abs(40), height=Abs(10), aspect=2)
    except TypeError:
        return
    raise AssertionError('Expected TypeError')

def test_aspect_ratio_x_1():
    r = Region(midleft=Abs(10, 15), height=Abs(30), aspect=2)
    app = AppStub()
    x = r.getRect(app)
    assert x.midleft == (10, 15)
    assert x.width == 60
    assert x.height == 30

def test_aspect_ratio_x_2():
    r = Region(centre=Abs(10, 15), height=Abs(30), aspect=2)
    app = AppStub()
    x = r.getRect(app)
    assert x.centre == (10, 15)
    assert x.width == 60
    assert x.height == 30

def test_aspect_ratio_x_3():
    r = Region(midright=Abs(10, 15), height=Abs(30), aspect=2)
    app = AppStub()
    x = r.getRect(app)
    assert x.midright == (10, 15)
    assert x.width == 60
    assert x.height == 30

def test_aspect_ratio_x_4():
    try:
        r = Region(y=Abs(15), size=Abs(10, 15), aspect=2)
    except TypeError:
        return
    raise AssertionError('Expected TypeError')

def test_aspect_ratio_x_2():
    r = Region(center=Abs(10, 15), height=Abs(30), aspect=2)
    app = AppStub()
    x = r.getRect(app)
    assert x.center == (10, 15)
    assert x.width == 60
    assert x.height == 30

def test_overconstraint_x_1():
    try:
        Region(topleft=Abs(0,1), bottomleft=Abs(2,3))
    except TypeError:
        return
    raise AssertionError('Expected TypeError')

def test_overconstraint_y_1():
    try:
        Region(midbottom=Abs(0,1), bottomleft=Abs(2,3))
    except TypeError:
        return
    raise AssertionError('Expected TypeError')

def test_overconstraint_x_2():
    try:
        Region(topleft=Abs(0,1), bottomright=Abs(2,3), centerx=Abs(4))
    except TypeError:
        return
    raise AssertionError('Expected TypeError')

def test_overconstraint_y_2():
    try:
        Region(topleft=Abs(0,1), bottomright=Abs(2,3), height=Abs(4))
    except TypeError:
        return
    raise AssertionError('Expected TypeError')

def test_underconstraint_x_1():
    try:
        Region(topleft=Abs(0,1), height=Abs(3))
    except TypeError:
        return
    raise AssertionError('Expected TypeError')

def test_underconstraint_y_1():
    try:
        Region(centre=Abs(10,11), right=Abs(20))
    except TypeError:
        return
    raise AssertionError('Expected TypeError')

def test_overconstraint_aspect():
    try:
        Region(topleft=Abs(0,1), bottomright=Abs(2,3), aspect=1)
    except TypeError:
        return
    raise AssertionError('Expected TypeError')

def test_underconstraint_aspect():
    try:
        Region(topleft=Abs(0,1), aspect=1)
    except TypeError:
        return
    raise AssertionError('Expected TypeError')

def test_invalid_argument():
    try:
        Region(topleft=Abs(0,1), bottomright=Abs(1,2), foobar=17)
    except TypeError:
        return
    raise AssertionError('Expected TypeError')

def test_scalars():
    r = Region(x=Abs(0), centrey=Abs(1), width=Abs(2), bottom=Abs(3))
    app = AppStub()
    x = r.getRect(app)
    assert x.x == 0
    assert x.centery == 1
    assert x.width == 2
    assert x.bottom == 3

