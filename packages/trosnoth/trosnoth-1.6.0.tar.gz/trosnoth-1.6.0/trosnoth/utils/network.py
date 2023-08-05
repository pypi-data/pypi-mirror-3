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

def compress_boolean(tuple):
    '''
    This function takes a given six-byte tuple and converts it into an integer
    for easy network transmission.
    '''
    # Quick error check
    if len(tuple) != 6:
        raise Exception('There is not 6 elements in the given tuple!')

    string_of_bytes = ''
    for character in tuple:
        string_of_bytes += str(int(character))

    # Convert the string into an integer, and return.
    return int(string_of_bytes, 2)

def expand_boolean(number):
    '''
    This function takes a given integer and converts it to a 6 byte tuple of
    boolean values.
    Ah, list comprehension =)
    '''
    return tuple([int((int(number) >> digit) & 1) for digit in range(5, -1,
            -1)])

