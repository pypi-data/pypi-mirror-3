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

log = logging.getLogger('components')

class Component(object):
    def __init__(self):
        # Find all the plugs.
        plugs = {}
        plugsByName = {}
        for k in dir(self):
            v = getattr(self, k)
            if isinstance(v, Plug):
                plugs[v] = plugsByName[k] = BoundPlug(v, self, k)

        # Go through methods and check for handlers.
        for k in dir(self):
            v = getattr(self, k)
            if isinstance(v, Handler):
                for message, plug in v.bits:
                    if plug is None:
                        # Handles messages from all plugs.
                        for p in plugs.itervalues():
                            if message in p._methods:
                                raise KeyError('handler already defined for '
                                        '%s/%s' % (p, message))
                            p._methods[message] = v.method
                    else:
                        # Handles messages from one plug only.
                        p = plugs[plug]
                        if message in p._methods:
                            raise KeyError('handler already defined for '
                                    '%s/%s' % (p, message))
                        p._methods[message] = v.method

        for k, v in plugsByName.iteritems():
            setattr(self, k, v)

class UnboundPlug(object):
    '''
    This is called UnboundPlug so that error messages make it clear that this
    plug is unbound. Plug is an alias for UnboundPlug in order to make more
    sense in written code.
    '''
    def __init__(self):
        self._defaultHandler = None

    def defaultHandler(self, fn):
        '''
        Decorator that specifies a method as the default message handler.
        '''
        return handler(None, self)(fn)

Plug = UnboundPlug

def queueMessage(target, message):
    try:
        target._receive(message)
    except Exception, e:
        log.exception(str(e))

class UnhandledMessage(Exception):
    pass

class BasePlug(object):
    def __init__(self):
        self.targets = []

    def send(self, message):
        for target in self.targets:
            queueMessage(target, message)

    def _receive(self, message):
        raise UnhandledMessage('BasePlug does not handle %s' % (self.obj,
                type(message)))

    def connectPlug(self, plug):
        '''
        Note that this unplugs the current plug and plugs it into the remote
        plug without unplugging the remote plug from anything it's plugged
        into.
        '''
        if not isinstance(plug, BasePlug):
            raise TypeError('%r is not a BasePlug' % (plug,))
        for other in self.targets:
            self.disconnectPlug(other)

        self.targets = [plug]
        plug.targets.append(self)

    def disconnectAll(self):
        '''
        Disconnects this plug from everything it's attached to.
        '''
        for other in list(self.targets):
            self.disconnectPlug(other)

    def disconnectPlug(self, plug):
        '''
        Unplugs a connection between this plug and the given plug if such a
        connection exists.
        '''
        try:
            self.targets.remove(plug)
        except KeyError:
            pass

        try:
            plug.targets.remove(self)
        except KeyError:
            pass

class DynamicPlug(BasePlug):
    '''
    Plug that can be created and used at run-time.
    '''
    def __init__(self, receiverFn):
        BasePlug.__init__(self)
        self._receive = receiverFn

class BoundPlug(BasePlug):
    def __init__(self, plug, obj, name):
        BasePlug.__init__(self)
        self.plug = plug
        self.obj = obj
        self._name = name
        self._methods = {}

    def __str__(self):
        return '%r.%s' % (self.obj, self._name)

    def __repr__(self):
        return '<BoundPlug %r of %r>' % (self._name, self.obj)

    def _receive(self, message):
        # Find the correct handler.
        try:
            method = self._methods[type(message)]
        except KeyError:
            try:
                # Get the default.
                method = self._methods[None]
            except KeyError:
                raise UnhandledMessage('%s does not handle %s' % (self.obj,
                        type(message)))

        # Call this handler.
        method(self.obj, message)

class Handler(object):
    def __init__(self, method, message, plug=None):
        self.method = method
        if plug is not None and not isinstance(plug, UnboundPlug):
            raise TypeError('plug must be UnboundPlug, not %s' % (plug,))
        self.bits = [(message, plug)]

def handler(message, plug=None):
    def handler(method):
        if isinstance(method, Handler):
            method.bits.append((message, plug))
            return method
        return Handler(method, message, plug)
    return handler


class Adaptor(Component):
    '''
    Simple component with two connected plugs, plug1 and plug2.
    '''

    plug1 = Plug()
    plug2 = Plug()

    @plug1.defaultHandler
    def fromPlug1(self, msg):
        self.plug2.send(msg)

    @plug2.defaultHandler
    def fromPlug2(self, msg):
        self.plug1.send(msg)
