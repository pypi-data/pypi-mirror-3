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

import logging
import itertools
import types

def new(count):
    '''new(count) - returns an iterator object which will give count distinct
    instances of the object class.  This is useful for defining setting
    options.  For example, north, south, east, west = new(4) . There is no
    reason that these options should be given numeric values, but it is
    important that north != south != east != west.
    '''
    for i in xrange(count):
        yield object()

# timeNow is used to update things based on how much time has passed.
# Note: on Windows, time.clock() is more precise than time.time()
# On Windows time.clock() also does not change when the system clock changes.
# On linux however, time.clock() measures process time rather than wall time.
import platform
if platform.system() == 'Windows':
    from time import clock as timeNow
else:
    from time import time as timeNow

from hashlib import sha1 as hasher

class RunningAverage(object):
    def __init__(self, count):
        self.values = []
        self.total = 0.
        self.maxCount = count

    @property
    def mean(self):
        if len(self.values) == 0:
            return None
        return self.total / len(self.values)

    def noteValue(self, value):
        self.total += value
        self.values.append(value)
        if len(self.values) > self.maxCount:
            self.total -= self.values.pop(0)

class StaticMeta(type):
    '''
    Metaclass for Function and Static classes below. Ensures that all methods
    are class methods.
    '''
    def __new__(cls, name, bases, dict_):
        for k, v in dict_.iteritems():
            if k == '__new__':
                continue
            if isinstance(v, types.FunctionType):
                dict_[k] = classmethod(v)
        return super(StaticMeta, cls).__new__(cls, name, bases, dict_)

class Static(object):
    '''
    Superclass for defining classes that are not meant to be instantiated. All
    methods become class methods by default.
    '''
    __metaclass__ = StaticMeta
    def __new__(cls, *args, **kwargs):
        raise NotImplementedError('%s class cannot be instantiated' %
                (cls.__name__,))

class Function(Static):
    '''
    Superclass for defining extensible functions, potentially having related
    helper functions. StaticMeta makes all methods be class methods, and when
    the class is called, its run() method is used as the entrypoint.

    This is useful for defining extensible patterns of instructions.

    e.g.

    >>> class doSomething(Function):
    >>>     someConst = 17
    >>>     def run(self, value):
    >>>         x = self.getX(value)
    >>>         return x + self.someConst

    >>>     def getX(self, value):
    >>>         return value

    >>> doSomething(13)
    30
    '''
    def __new__(cls, *args, **kwargs):
        return cls.run(*args, **kwargs)

def initLogging(debug=False, logFile=None):
    import twisted.python.log
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
    logging.getLogger().addHandler(logging.StreamHandler())
    if logFile:
        logging.getLogger().addHandler(logging.FileHandler(logFile))
    observer = twisted.python.log.PythonLoggingObserver()
    twisted.python.log.startLoggingWithObserver(observer.emit)

# Convenience functions for wrapping long strings based on maximum pixel width
# http://www.pygame.org/wiki/TextWrapping

def truncline(text, font, maxwidth):
    real = len(text)
    stext = text
    l = font.size(text)[0]
    cut = 0
    a = 0
    done = 1
    while l > maxwidth:
        a = a + 1
        n = text.rsplit(None, a)[0]
        if stext == n:
            cut += 1
            stext= n[:-cut]
        else:
            stext = n
        l = font.size(stext)[0]
        real = len(stext)
        done = 0
    return real, done, stext

def wrapline(text, font, maxwidth):
    done = 0
    wrapped = []

    while not done:
        nl, done, stext = truncline(text, font, maxwidth)
        wrapped.append(stext.strip())
        text = text[nl:]
    return wrapped

def wrapMultiLine(text, font, maxwidth):
    lines = itertools.chain(*(wrapline(line, font, maxwidth) for line in
            text.splitlines()))
    return list(lines)

class BasicContextManager(object):
    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass
