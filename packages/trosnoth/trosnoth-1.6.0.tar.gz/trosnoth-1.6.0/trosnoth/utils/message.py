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

class MessageClass(type):
    '''
    This metaclass is provided for convenience. It checks if you have provided
    a single string for the .fields class attribute and if so converts it to a
    tuple.
    '''
    def __new__(cls, name, bases, dictn):
        # Test for a single string cls.fields and make tuple.
        if isinstance(dictn.get('fields'), str):
            dictn['fields'] = (dictn['fields'],)

        # Do the real building.
        return type.__new__(cls, name, bases, dictn)


class MessageBase(object):
    '''
    Allows message classes to be defined by:
        class CustomMessage(Message):
            fields = ('myField', 'otherField')
    And then instantiated by:
        x = CustomMessage(17, otherField=2)
    Which will create an object where:
        x.myField == 17
        x.otherField == 2
    '''

    def __init__(self, *args, **kwargs):
        if len(args) > len(self.fields):
            raise TypeError('%s takes at most %d arguments (%d given)' %
                    (type(self), len(self.fields), len(args)))

        # Simply get the args and store them as attributes of self.
        for i in xrange(len(args)):
            k = self.fields[i]
            v = args[i]
            if k in kwargs:
                raise TypeError('got multiple values for keyword argument '
                        '%r' % (k,))
            kwargs[k] = v

        for k,v in kwargs.iteritems():
            setattr(self, k, v)

    def __repr__(self):
        def get(k):
            try:
                return repr(getattr(self, k))
            except AttributeError:
                return '???'
        args = []
        for k in self.fields:
            args.append(get(k))
        return '%s(%s)' % (type(self).__name__, ', '.join(args))

class Message(MessageBase):
    __metaclass__ = MessageClass
